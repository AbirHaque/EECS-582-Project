from common import app, db, logger, Article, Topic, init_database, db_path
from datetime import datetime, timezone
import os, feedparser, requests
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sentence_transformers import SentenceTransformer
import chromadb
import newspaper
import numpy as np
from sklearn.cluster import HDBSCAN
from abc import ABC, abstractmethod
from typing import List
from message_bus import send_message

class IngestionStrategy(ABC):

    @abstractmethod
    def ingest(self):
        pass

class RSSFeedIngestionStrategy(IngestionStrategy):

    def __init__(self):
        self.RSS_FEEDS = [
            'https://moxie.foxnews.com/google-publisher/latest.xml',
            'https://feeds.feedburner.com/ndtvnews-world-news',
            'https://www.theguardian.com/world/rss'
        ]
    
    def ingest(self):
        articles = []
        for feed_url in self.RSS_FEEDS:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                published_at = datetime.now(timezone.utc)
                if hasattr(entry, 'published_parsed'):
                    published_at = datetime(*entry.published_parsed[:6])
                content = ''
                if hasattr(entry, 'content'):
                    content = entry.content[0].value
                elif hasattr(entry, 'summary'):
                    content = entry.summary
                elif hasattr(entry, 'description'):
                    content = entry.description
                article = Article(
                    title=entry.title,
                    url=entry.link,
                    published_at=published_at,
                    content=content,
                    processed=False
                )
                articles.append(article)
        return articles

class NewsAPIIngestionStrategy(IngestionStrategy):
    def __init__(self, api_key):
        self.api_key = api_key
        

    def ingest(self):
        articles = []
        url = (f'https://newsapi.org/v2/top-headlines?country=us&apiKey={self.api_key}')
        response = requests.get(url).json()

        if response['status'] != 'ok':
            raise RuntimeError("News API call failed")
        
        for article in response['articles']:
            if article['content'] is None: # logic should probably be moved to pre-processing phase
                continue

            try:
                art = newspaper.article(url)
                art.download()
                art.parse()
            except:
                continue
            
            if len(art.text) <= 100: continue

            ingested_article = Article(
                title = article['title'],
                url = article['url'],
                content = art.text,
                published_at = datetime.strptime(article['publishedAt'], "%Y-%m-%dT%H:%M:%SZ"),
                processed = False
            )
            articles.append(ingested_article)
        return articles

class MultipleIngestionStrategy(IngestionStrategy):

    def __init__(self, strategies: List[IngestionStrategy]):
        self.strategies = strategies
    
    def ingest(self):
        articles = []
        for strategy in self.strategies:
            articles.extend(strategy.ingest())
        return articles

class Ingestor(ABC):
    @abstractmethod
    def __init__(self, ingestionStrategy: IngestionStrategy):
        self.ingestionStrategy = ingestionStrategy
    
    @abstractmethod
    def run_ingestion(self):
        pass


class NewsIngestor(Ingestor):
    def __init__(self, ingestionStrategy: IngestionStrategy):
        self.ingestionStrategy = ingestionStrategy
    
    def run_ingestion(self):
        new_articles = self.ingestionStrategy.ingest()

        with app.app_context():
            for article in new_articles:
                if Article.query.filter_by(url=article.url).first():
                    continue

                db.session.add(article)
                db.session.commit()
                logger.info(f"Article ingested: {article.title}")
                send_message('articles_ingested', str(article.id))

def ingest_news():
    strategies = []

    load_dotenv()
    news_api_key = os.getenv("NEWS_API_KEY")
    if not news_api_key:
        raise ValueError("NEWS_API_KEY not found in environment variables.")
    strategies.append(NewsAPIIngestionStrategy(news_api_key))
    strategies.append(RSSFeedIngestionStrategy())
    news_ingestion_strategy = MultipleIngestionStrategy(strategies)

    newsIngestor = NewsIngestor(news_ingestion_strategy)
    newsIngestor.run_ingestion()

class ClusteringStrategy(ABC):

    @abstractmethod
    def __init__(self, DBClient, vectorDBClient):
        pass

    @abstractmethod
    def _set_articles_to_cluster(self):
        pass

    @abstractmethod
    def cluster(self):
        pass

class HDBSCANClusteringStrategy(ClusteringStrategy):

    def __init__(self, DBClient, vectorDBClient):
        self.db = DBClient
        self.vectorDBClient = vectorDBClient
        self.articles = None

    def _set_articles_to_cluster(self):
        collection = self.vectorDBClient.get_collection("news")
        self.articles = collection.get(include=["embeddings"])
        print(self.articles)
 
        
    def cluster(self):
        self._set_articles_to_cluster()

        embeddings = np.array(self.articles['embeddings'])
        hdb = HDBSCAN(min_cluster_size=2)
        hdb.fit(embeddings)

        labels = set()
        topics = {} # map labels to topics

        with app.app_context():
            article_objects = [Article.query.get(article_id) for article_id in self.articles["ids"]]

            for article, label in zip(article_objects, hdb.labels_):
                if label != -1 and label not in labels:
                    labels.add(label)
                    topic = Topic(name=article.title)
                    self.db.session.add(topic)
                    self.db.session.commit()
                    self.db.session.refresh(topic)
                    topics[label] = topic.id
                if label != -1:
                    article.topic_id = topics[label]
                
                article.processed = True
            
            db.session.commit() # persist article topic_id updates
        
        topics_list = [v for v in topics.values()]
        return topics_list
        
class NearestTopicClusteringStrategy(ClusteringStrategy):

    def cluster(self):
        pass

class TopicGenerator:
    def __init__(self, clustering_strategy: ClusteringStrategy):
        self.clustering_strategy = clustering_strategy
    
    def run_clustering(self):
        new_topics = self.clustering_strategy.cluster()
        if len(new_topics) > 0:
            logger.info(f"Topics generated: {new_topics}")
            send_message('topics_generated', str(new_topics))
        else:
            logger.info("No topics generated")


def cluster_articles():

    engine = create_engine(f'sqlite:///{db_path}')
    with engine.connect() as conn:
        articles = conn.execute(text("SELECT id, title FROM article WHERE processed = False")).fetchall()

    if not articles:
        logger.info("No unprocessed articles found.")
        return

    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode([a.title for a in articles])

    client = chromadb.Client()
    collection = client.create_collection("news", get_or_create=True)
    ids = [str(a.id) for a in articles]
    collection.add(ids=ids, embeddings=embeddings.tolist())

    strategy = HDBSCANClusteringStrategy(db, client)
    topic_generator = TopicGenerator(strategy)
    topic_generator.run_clustering()


# def process_articles():
#     engine = create_engine(f'sqlite:///{db_path}')
#     with engine.connect() as conn:
#         articles = conn.execute(text("SELECT id, title FROM article WHERE processed = False")).fetchall()
    
#     if not articles:
#         logger.info("No unprocessed articles found.")
#         return
    
#     # model = SentenceTransformer('all-MiniLM-L6-v2')
#     # embeddings = model.encode([a.title for a in articles])
    
#     # client = chromadb.Client()
#     # collection = client.create_collection("news")
#     # ids = [str(a.id) for a in articles]
#     # collection.add(ids=ids, embeddings=embeddings.tolist())
#     client = chromadb.Client()
#     collection = client.get_collection("news")
#     results = collection.query(query_embeddings=embeddings, n_results=5)
#     logger.info(f"Response from chromadb: {results}")
    
#     threshold = 0.2
#     with app.app_context():
#         topics = []
#         for idx, cluster in enumerate(results['ids']):
#             distances = results.get('distances', [[]])[idx]
#             filtered_ids = [int(a_id) for a_id, d in zip(cluster, distances) if d < threshold]
#             if not filtered_ids:
#                 filtered_ids = [int(cluster[0])]
#             topic_articles = [Article.query.get(article_id) for article_id in filtered_ids]
#             topic_name = " & ".join([a.title for a in topic_articles[:3]])
#             topic = Topic(name=topic_name)
#             db.session.add(topic)
#             db.session.commit()
#             topics.append(topic.id)
#             for article in topic_articles:
#                 at = ArticlesTopics(article_id=article.id, topic_id=topic.id)
#                 db.session.add(at)
#                 article.processed = True
#                 db.session.add(article)
#             db.session.commit()
#     logger.info(f"Topics generated: {topics}")
#     send_message('topics_generated', str(topics))

if __name__ == '__main__':
    if not os.path.exists(db_path):
        logger.info("Database file not found. Initializing database...")
        init_database()
    else:
        logger.info("Database file already exists.")
    ingest_news()
    cluster_articles()
    # process_articles()
