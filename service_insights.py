from common import app, db, logger, Topic, Insight, RankingsTopics
import threading
from gemini_client import generate_content
from message_bus import insights_queue

def generate_insights():
    logger.info("Insights generation service started.")
    while True:
        message = insights_queue.get()
        logger.info(f"Received message in generate_insights: {message}")
        if message['queue'] == 'rankings_created':
            with app.app_context():
                try:
                    ranking_id = int(message['body'])
                    ranked_items = RankingsTopics.query.filter_by(ranking_id=ranking_id).order_by(RankingsTopics.rank_order).all()
                    for item in ranked_items:
                        topic = Topic.query.get(item.topic_id)
                        api_response = generate_content(f"Summarize this topic: {topic.name}")
                        logger.info(f"Received API response: {api_response}")
                        candidate = api_response.get("candidates", [{}])[0]
                        content = candidate.get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                        if not content:
                            logger.warning(f"No content received for topic {topic.id} - API response: {api_response}")
                        insight = Insight(
                            topic_id=topic.id,
                            content=content,
                            insight_type='summary'
                        )
                        db.session.add(insight)
                        db.session.commit()
                        logger.info(f"Insight generated for topic {topic.id}: {insight.id}")
                except Exception as e:
                    logger.error(f"Error generating insights: {e}")
        insights_queue.task_done()

if __name__ == '__main__':
    threading.Thread(target=generate_insights, daemon=True).start()
    while True:
        pass
