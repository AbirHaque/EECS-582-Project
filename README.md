# Insite Capstone Application

## Overview
This application ingests news articles from various RSS feeds, processes them to create topics, ranks the topics, generates insights using a chat API, and provides a REST API to access the data.

## File Descriptions

- **common.py**  
  Sets up the core Flask app, SQLAlchemy database, logging, and defines the database models (Article, Topic, Ranking, Insight, SocialMediaPost, etc.). Also provides a utility to initialize the database.

- **message_bus.py**  
  Implements the message queues (ranking_queue, social_queue, insights_queue) and a helper function `send_message` to facilitate inter-service communication.

- **service_ingestion.py**  
  Contains two main functions:
  - `ingest_news()`: Ingests news articles from predefined RSS feeds, saves them to the database, and sends messages on successful ingestion.
  - `process_articles()`: Processes unprocessed articles, uses a SentenceTransformer to encode article titles, clusters them using chromadb, and creates topics linking the articles.

- **service_ranking.py**  
  Includes:
  - `rank_topics()`: Listens to messages for generated topics, ranks topics by the number of articles, saves ranking results, and notifies other services.
  - `ingest_social()`: Listens for ranking events, fetches related social media posts, and saves them to the database.

- **service_insights.py**  
  Waits for ranking events, fetches topics for a ranking, and uses an external chat API (ollama) to generate summarized insights for each topic.

- **service_api.py**  
  Provides a simple REST API with endpoints:
  - `/topics`: Returns topics from the most recent ranking.
  - `/topics/<topic_id>`: Returns insights for the specific topic.

- **startup.py**  
  Acts as the entry point for the application. It initializes the database if needed, starts background threads for each service (ingestion, ranking, social ingestion, insights generation), and runs the API service.

## Running the Application
1. Ensure the database is initialized (automatically handled by startup.py).
2. Start the application by running `startup.py`.
3. Access the API endpoints at `http://localhost:5000`.

## Environment Configuration
Create a `.env` file in the project root with the following content:
```
GEMINI_API_KEY={API_KEY}
NEWS_API_KEY={NEWS_API_KEY}
```
Ensure that the `.env` file is not committed (already added to .gitignore).

## Notes
- Communication between services is managed via the custom message bus defined in message_bus.py.
- Each service operates on its own thread for concurrent processing.
- Logging is enabled for tracking operations and errors throughout the application.

