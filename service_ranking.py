from common import app, db, logger, Topic, Ranking, RankingsTopics, SocialMediaPost, Article
import threading, requests
from datetime import datetime, timezone
from message_bus import ranking_queue, social_queue, send_message
import time
import math

RANK_INTERVAL = 300  # Run ranking every 5 minutes
RECENCY_WEIGHT = 0.6  # Weight for time decay
ARTICLE_COUNT_WEIGHT = 0.4  # Weight for article count
TIME_DECAY_HOURS = 24  # Time decay factor in hours

def ensure_timezone(dt):
    """Ensure datetime has timezone information"""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt

def calculate_topic_score(topic, current_time):
    """
    Calculate topic score based on:
    1. Recency of articles (with time decay)
    2. Number of articles
    3. Source diversity
    """
    # current_time = datetime.now(timezone.utc)
    
    # Calculate recency score
    recency_scores = []
    sources = set()
    try:
        topic_articles = Article.query.filter(Article.topic_id == topic.id).all()
        for article in topic_articles:
            article_time = ensure_timezone(article.published_at)
            # Time decay calculation
            age_hours = (current_time - article_time).total_seconds() / 3600
            time_factor = math.exp(-age_hours / TIME_DECAY_HOURS)  # Exponential decay
            recency_scores.append(time_factor)
            
            # Track unique sources
            if hasattr(article, 'source') and article.source:
                sources.add(article.source)
        
        # Average recency score (time decay)
        avg_recency = sum(recency_scores) / len(recency_scores) if recency_scores else 0
        
        # Article count score (normalized by log to prevent domination by count)
        article_count = math.log(1 + len(topic_articles))
        
        # Source diversity bonus (normalized)
        source_diversity = len(sources) / 3  # Assuming we want at least 3 sources for max diversity
        
        # Combine scores with weights
        final_score = (
            RECENCY_WEIGHT * avg_recency +
            ARTICLE_COUNT_WEIGHT * article_count +
            0.2 * source_diversity  # 20% weight for source diversity
        )

        logger.info(f"Topic score calculated: {topic}, {final_score}, article count: {article_count}")
        
        return final_score
    except Exception as e:
        logger.error(f"Error calculating score for topic {topic.id}: {e}")
        return 0


def create_new_ranking(topics):
    """Create new ranking with error handling"""
    try:
        # Calculate scores and sort topics
        topic_scores = []
        current_time = datetime.now(timezone.utc)
        for topic in topics:
            
            score = calculate_topic_score(topic, current_time)
            topic_scores.append((topic, score))
        
        ranked_topics = sorted(topic_scores, key=lambda x: x[1], reverse=True)[:10]
        
        # Create new ranking
        new_ranking = Ranking()
        db.session.add(new_ranking)
        db.session.commit()
        
        # Add ranked topics
        for idx, (topic, _) in enumerate(ranked_topics):
            rt = RankingsTopics(
                ranking_id=new_ranking.id,
                topic_id=topic.id,
                rank_order=idx+1
            )
            db.session.add(rt)
        
        db.session.commit()
        logger.info(f"Created new ranking {new_ranking.id} with {len(ranked_topics)} topics")
        send_message('rankings_created', str(new_ranking.id))
        return new_ranking.id
    
    except Exception as e:
        logger.error(f"Error creating new ranking: {e}")
        db.session.rollback()
        return None

def periodic_ranking():
    """Periodic ranking with improved error handling"""
    logger.info("Starting periodic ranking service")
    while True:
        try:
            with app.app_context():
                topics = Topic.query.all()
                if topics:
                    ranking_id = create_new_ranking(topics)
                    if ranking_id:
                        logger.info(f"Periodic ranking completed, created ranking {ranking_id}")
                else:
                    logger.info("No topics found for ranking")
        except Exception as e:
            logger.error(f"Error in periodic ranking: {e}")
        
        time.sleep(RANK_INTERVAL)

def handle_new_topics(message):
    """Handle new topics with error handling"""
    with app.app_context():
        try:
            topic_ids = eval(message['body'])
            topics = Topic.query.filter(Topic.id.in_(topic_ids)).all()
            if topics:
                all_topics = Topic.query.all()
                create_new_ranking(all_topics)
                logger.info("Ranking updated due to new topics")
        except Exception as e:
            logger.error(f"Error processing new topics: {e}")

def rank_topics():
    """Main ranking service"""
    logger.info("Rank topics service started")
    
    # Start periodic ranking
    threading.Thread(target=periodic_ranking, daemon=True).start()
    
    # Handle event-based ranking
    while True:
        message = ranking_queue.get()
        logger.info(f"Received message in rank_topics: {message}")
        
        if message['queue'] == 'topics_generated':
            handle_new_topics(message)
        
        ranking_queue.task_done()
        
def ingest_social():
    """Social media ingestion service with improved datetime handling"""
    logger.info("Social media ingestion service started.")
    while True:
        message = social_queue.get()
        logger.info(f"Received message in ingest_social: {message}")
        if message['queue'] == 'rankings_created':
            with app.app_context():
                try:
                    ranking_id = int(message['body'])
                    ranking = Ranking.query.get(ranking_id)
                    for topic in ranking.topics:
                        search_query = " ".join(topic.name.split()[:3])
                        response = requests.get(
                            'https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts',
                            params={'q': search_query, 'sort': 'latest', 'limit': 25}
                        )
                        if response.status_code == 200:
                            posts = response.json().get('posts', [])
                            for post in posts:
                                record = post.get('record', {})
                                created_at_str = record.get('createdAt')
                                try:
                                    if created_at_str:
                                        # Truncate microseconds to 6 digits and ensure proper format
                                        if '.' in created_at_str:
                                            base, ms = created_at_str.split('.')
                                            ms = ms.replace('Z', '')[:6]  # Remove Z and truncate to 6 digits
                                            created_at_str = f"{base}.{ms}Z"
                                        created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
                                    else:
                                        created_at = datetime.now(timezone.utc)
                                except ValueError as e:
                                    logger.warning(f"Invalid datetime format: {created_at_str}, using current time")
                                    created_at = datetime.now(timezone.utc)

                                social_post = SocialMediaPost(
                                    topic_id=topic.id,
                                    content=record.get('text', ''),
                                    created_at=created_at,
                                    views=post.get('views', 0),
                                    likes=post.get('likes', 0)
                                )
                                db.session.add(social_post)
                            db.session.commit()
                            logger.info(f"Ingested social media posts for topic: {topic.name}")
                        else:
                            logger.error(f"Failed to fetch posts for topic '{search_query}': {response.status_code}")
                except Exception as e:
                    logger.error(f"Error processing social media posts: {e}")
                    db.session.rollback()
        social_queue.task_done()

if __name__ == '__main__':
    threading.Thread(target=rank_topics, daemon=True).start()
    threading.Thread(target=ingest_social, daemon=True).start()
    
    while True:
        time.sleep(1)
