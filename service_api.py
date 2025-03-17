from common import app, Ranking, Insight, SocialMediaPost, Article
import json
from flask import jsonify
from datetime import datetime, timedelta
import spacy

nlp = spacy.load("en_core_web_sm")

# Defining an endpoint to retrieve the latest ranking of topics
@app.route('/topics')
def get_top_topics():
    latest_ranking = Ranking.query.order_by(Ranking.created_at.desc()).first()
    if latest_ranking:
        return jsonify({
            'ranking_id': latest_ranking.id,
            'created_at': latest_ranking.created_at.isoformat(),
            'topics': [{'id': topic.id, 'name': topic.name} for topic in latest_ranking.topics]
        })
    return jsonify({})

# Defining an endpoint to retrieve ranking history from the last hour
@app.route('/rankings/history')
def get_ranking_history():
    # Get rankings from the last hour
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    rankings = Ranking.query.filter(Ranking.created_at >= one_hour_ago).order_by(Ranking.created_at.desc()).all()
    
    return jsonify([{
        'id': ranking.id,
        'created_at': ranking.created_at.isoformat(),
        'topic_count': len(ranking.topics),
        'topics': [{'id': topic.id, 'name': topic.name} for topic in ranking.topics]
    } for ranking in rankings])

# Defining an endpoint to fetch insights related to a specific topi
@app.route('/topics/<int:topic_id>')
def get_topic_insights(topic_id):
    insights = Insight.query.filter_by(topic_id=topic_id).all()
    return jsonify([{'type': insight.insight_type, 'content': insight.content} for insight in insights])

# Defining an endpoint to fetch social media posts related to a specific topic
@app.route('/topics/<int:topic_id>/social')
def get_topic_social_posts(topic_id):
    posts = SocialMediaPost.query.filter_by(topic_id=topic_id).all()
    return jsonify([{
        'id': post.id,
        'content': post.content,
        'created_at': post.created_at.isoformat(),
        'views': post.views,
        'likes': post.likes
    } for post in posts])

# Defining an endpoint to fetch references related to a specific topic
@app.route('/topics/<int:topic_id>/references')
def get_topic_references(topic_id):
    references = Article.query.filter_by(topic_id=topic_id).all()
    return jsonify([{
        'id': reference.id,
        'title': reference.title,
        'url': reference.url
        # Missing rest of columns, but thats fine for now
    } for reference in references])

# Defining an endpoint to fetch sentiment analysis for a specific topic
@app.route('/topics/<int:topic_id>/sentiment')
def get_topic_sentiment(topic_id):
    sentiment_insight = Insight.query.filter_by(topic_id=topic_id, insight_type="sentiment").order_by(Insight.id.desc()).first()
    
    if sentiment_insight:
        try:
            # Parse the sentiment data from the JSON string
            sentiment_data = json.loads(sentiment_insight.content)
            return jsonify({
                'topic_id': topic_id,
                'sentiment': sentiment_data
            })
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid sentiment data format'}), 500
    else:
        return jsonify({'error': 'No sentiment analysis available for this topic'}), 404

# Function to generate key phrases of text
@app.route('/keyphrases/<text>')
def generate_key_phrases(text):
    nlp_text = nlp(text)
    key_phrases = [chunk.text for chunk in nlp_text.noun_chunks]
    return key_phrases[:10]
    #return jsonify([{'type': insight.insight_type, 'content': insight.content} for insight in insights])

# Running the Flask application if this script is executed directly
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True
    )