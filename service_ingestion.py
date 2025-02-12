from common import app, db, logger, Article, Topic, ArticlesTopics, init_database, db_path
from datetime import datetime, timezone
import os, feedparser
from sqlalchemy import create_engine, text
from sentence_transformers import SentenceTransformer
import chromadb
from message_bus import send_message

RSS_FEEDS = [
    'https://moxie.foxnews.com/google-publisher/latest.xml',
    'https://feeds.feedburner.com/ndtvnews-world-news',
    'https://www.theguardian.com/world/rss'
]

def ingest_news():
    with app.app_context():
        for feed_url in RSS_FEEDS:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                article = Article.query.filter_by(url=entry.link).first()
                if not article:
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
                    db.session.add(article)
                    db.session.commit()
                    logger.info(f"Article ingested: {article.title}")
                    send_message('articles_ingested', str(article.id))

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
