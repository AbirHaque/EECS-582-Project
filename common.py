# Importing necessary modules
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import logging


# Initializing the Flask application
app = Flask(__name__, instance_relative_config=True)
CORS(app)
# Defining the database file path inside the instance folder
db_path = os.path.join(app.instance_path, 'news.db')
# Configuring the flask app inside the instance folder
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

os.makedirs(app.instance_path, exist_ok=True)
# Defining the Article model (table) to store news articles
class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    url = db.Column(db.String(255), unique=True)
    published_at = db.Column(db.DateTime)
    content = db.Column(db.Text)
    processed = db.Column(db.Boolean, default=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))
    multimedia = db.Column(db.Text)

# Defining the Topic model (table) to store topics/categories of articles
class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    #articles = db.relationship('Article', secondary='articles_topics')

# Defining the Ranking model (table) to rank topics
class Ranking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    topics = db.relationship('Topic', secondary='rankings_topics')

# Defining a linking table between Rankings and Topics
class RankingsTopics(db.Model):
    __tablename__ = 'rankings_topics'
    ranking_id = db.Column(db.Integer, db.ForeignKey('ranking.id'), primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), primary_key=True)
    rank_order = db.Column(db.Integer)


# Defining the Insight model (table) to store insights related to topics
class Insight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))
    content = db.Column(db.Text)
    insight_type = db.Column(db.String(50))

# Defining the SocialMediaPost model (table) to store social media posts about topics
class SocialMediaPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    views = db.Column(db.Integer)
    likes = db.Column(db.Integer)

# class ArticlesTopics(db.Model):
#     __tablename__ = 'articles_topics'
#     article_id = db.Column(db.Integer, db.ForeignKey('article.id'), primary_key=True)
#     topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), primary_key=True)

# Function to initialize the database
def init_database():
    with app.app_context():
        db.drop_all()
        db.create_all()
        logger.info("Database initialized successfully!")

if __name__ == '__main__':
    print("App and db defined:", app, db)
