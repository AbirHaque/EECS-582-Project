from common import app, Ranking, Insight
from flask import jsonify
from datetime import datetime, timedelta

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

@app.route('/topics/<int:topic_id>')
def get_topic_insights(topic_id):
    insights = Insight.query.filter_by(topic_id=topic_id).all()
    return jsonify([{'type': insight.insight_type, 'content': insight.content} for insight in insights])

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)