# Suppressing specific warnings to reduce unnecessary console output
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# Suppressing TensorFlow log messages to avoid clutter
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
from common import db_path, init_database, logger
import threading
import service_ingestion
import service_ranking
import service_insights
import service_api
import sys

# Checks if the database file exists; if not, initialize the database
if not os.path.exists(db_path):
    logger.info("Database file not found, initializing database...")
    init_database()
else:
    logger.info("Database file exists.")

# Function to start the ingestion service which fetches news articles and clusters similar articles together
def start_ingestion():
    service_ingestion.ingest_news()
    service_ingestion.cluster_articles()

# Function to start the topic ranking service
def start_rank_topics():
    service_ranking.rank_topics()

# Function to start the social media data ingestion service
def start_ingest_social():
    service_ranking.ingest_social()

# Function to start the insights generation service
def start_generate_insights():
    service_insights.generate_insights()

if __name__ == '__main__':
    # Check for demo mode flag
    if "--demo" in sys.argv:
        print("Demo mode enabled: only running the API service.")
        print("API service running at http://localhost:5000")
        service_api.app.run(host='0.0.0.0', debug=True)
    else:
        print("Starting all services...")
        threading.Thread(target=start_ingestion, daemon=True).start()
        threading.Thread(target=start_rank_topics, daemon=True).start()
        threading.Thread(target=start_ingest_social, daemon=True).start()
        threading.Thread(target=start_generate_insights, daemon=True).start()

        print("API service running at http://localhost:5000")
        service_api.app.run(host='0.0.0.0', debug=True)