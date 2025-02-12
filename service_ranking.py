from common import app, db, logger, Topic, Ranking, RankingsTopics, SocialMediaPost
import threading, requests
from datetime import datetime, timezone
from message_bus import ranking_queue, social_queue, send_message

def rank_topics():
    logger.info("Rank topics service started.")
    while True:
        message = ranking_queue.get()
        logger.info(f"Received message in rank_topics: {message}")
        if message['queue'] == 'topics_generated':
            with app.app_context():
                try:
                    topic_ids = eval(message['body'])
                    topics = Topic.query.filter(Topic.id.in_(topic_ids)).all()
                    ranked = sorted(topics, key=lambda t: len(t.articles), reverse=True)[:10]
                    new_ranking = Ranking()
                    db.session.add(new_ranking)
                    db.session.commit()
                    for idx, topic in enumerate(ranked):
                        rt = RankingsTopics(ranking_id=new_ranking.id, topic_id=topic.id, rank_order=idx+1)
                        db.session.add(rt)
                    db.session.commit()
                    logger.info(f"Ranking created: {new_ranking.id}")
                    send_message('rankings_created', str(new_ranking.id))
                except Exception as e:
                    logger.error(f"Error processing topics: {e}")
        ranking_queue.task_done()

def ingest_social():
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
                        search_query = topic.name
                        response = requests.get(
                            'https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts',
                            params={'q': search_query, 'sort': 'latest', 'limit': 25}
                        )
                        if response.status_code == 200:
                            posts = response.json().get('posts', [])
                            for post in posts:
                                record = post.get('record', {})
                                created_at_str = record.get('createdAt')
                                created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00")) if created_at_str else datetime.now(timezone.utc)
                                social_post = SocialMediaPost(
                                    topic_id=topic.id,
                                    content=record.get('text', ''),
                                    created_at=created_at,
                                    views=post.get('views', 0),
                                    likes=post.get('likes', 0)
                                )
                                db.session.add(social_post)
                            db.session.commit()
                        else:
                            logger.error(f"Failed to fetch posts for topic '{search_query}': {response.status_code}")
                except Exception as e:
                    logger.error(f"Error processing social media posts: {e}")
        social_queue.task_done()

if __name__ == '__main__':
    threading.Thread(target=rank_topics, daemon=True).start()
    threading.Thread(target=ingest_social, daemon=True).start()
    while True:
        pass
