from common import app, db, logger, Article, Topic, ArticlesTopics, init_database, db_path
from datetime import datetime, timezone
import os, feedparser, requests
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sentence_transformers import SentenceTransformer
import chromadb
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
            ingested_article = Article(
                title = article['title'],
                url = article['url'],
                content = article['content'],
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
    newsAPIIngestionStrategy = NewsAPIIngestionStrategy(news_api_key)
    strategies.append(newsAPIIngestionStrategy)

    strategies.append(RSSFeedIngestionStrategy())

    news_ingestion_strategy = MultipleIngestionStrategy(strategies)
    newsIngestor = NewsIngestor(news_ingestion_strategy)
    newsIngestor.run_ingestion()

# def ingest_news():
#     with app.app_context():
#         for feed_url in RSS_FEEDS:
#             feed = feedparser.parse(feed_url)
#             for entry in feed.entries:
#                 article = Article.query.filter_by(url=entry.link).first()
#                 if not article:
#                     published_at = datetime.now(timezone.utc)
#                     if hasattr(entry, 'published_parsed'):
#                         published_at = datetime(*entry.published_parsed[:6])
#                     content = ''
#                     if hasattr(entry, 'content'):
#                         content = entry.content[0].value
#                     elif hasattr(entry, 'summary'):
#                         content = entry.summary
#                     elif hasattr(entry, 'description'):
#                         content = entry.description
#                     article = Article(
#                         title=entry.title,
#                         url=entry.link,
#                         published_at=published_at,
#                         content=content,
#                         processed=False
#                     )
#                     db.session.add(article)
#                     db.session.commit()
#                     logger.info(f"Article ingested: {article.title}")
#                     send_message('articles_ingested', str(article.id))

def process_articles():
    engine = create_engine(f'sqlite:///{db_path}')
    with engine.connect() as conn:
        articles = conn.execute(text("SELECT id, title FROM article WHERE processed = False")).fetchall()
    
    if not articles:
        logger.info("No unprocessed articles found.")
        return
    
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode([a.title for a in articles])
    
    client = chromadb.Client()
    collection = client.create_collection("news")
    ids = [str(a.id) for a in articles]
    collection.add(ids=ids, embeddings=embeddings.tolist())
    results = collection.query(query_embeddings=embeddings, n_results=5)
    logger.info(f"Response from chromadb: {results}")
    
    threshold = 0.2
    with app.app_context():
        topics = []
        for idx, cluster in enumerate(results['ids']):
            distances = results.get('distances', [[]])[idx]
            filtered_ids = [int(a_id) for a_id, d in zip(cluster, distances) if d < threshold]
            if not filtered_ids:
                filtered_ids = [int(cluster[0])]
            topic_articles = [Article.query.get(article_id) for article_id in filtered_ids]
            topic_name = " & ".join([a.title for a in topic_articles[:3]])
            topic = Topic(name=topic_name)
            db.session.add(topic)
            db.session.commit()
            topics.append(topic.id)
            for article in topic_articles:
                at = ArticlesTopics(article_id=article.id, topic_id=topic.id)
                db.session.add(at)
                article.processed = True
                db.session.add(article)
            db.session.commit()
    logger.info(f"Topics generated: {topics}")
    send_message('topics_generated', str(topics))

if __name__ == '__main__':
    if not os.path.exists(db_path):
        logger.info("Database file not found. Initializing database...")
        init_database()
    else:
        logger.info("Database file already exists.")
    ingest_news()
    process_articles()
