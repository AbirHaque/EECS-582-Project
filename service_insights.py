from common import app, db, logger, Topic, Insight, RankingsTopics
import threading
from ollama import chat
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
                        response = chat(
                            model='llama3.2',
                            messages=[{"role": "user", "content": f"Summarize this topic: {topic.name}"}]
                        )
                        insight = Insight(
                            topic_id=topic.id,
                            content=response.message.content,
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
