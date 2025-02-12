import os
from common import db_path, init_database, logger
import threading
import service_ingestion
import service_ranking
import service_insights
import service_api

if not os.path.exists(db_path):
    logger.info("Database file not found, initializing database...")
    init_database()
else:
    logger.info("Database file exists.")

def start_ingestion():
    service_ingestion.ingest_news()
    service_ingestion.process_articles()

def start_rank_topics():
    service_ranking.rank_topics()

def start_ingest_social():
    service_ranking.ingest_social()

def start_generate_insights():
    service_insights.generate_insights()

if __name__ == '__main__':
    print("Starting all services...")
    threading.Thread(target=start_ingestion, daemon=True).start()
    threading.Thread(target=start_rank_topics, daemon=True).start()
    threading.Thread(target=start_ingest_social, daemon=True).start()
    threading.Thread(target=start_generate_insights, daemon=True).start()

    print("API service running at http://localhost:5000")
    service_api.app.run(host='0.0.0.0', debug=True)
