from common import app, Ranking, Insight
from flask import jsonify

@app.route('/topics')
def get_top_topics():
    latest_ranking = Ranking.query.order_by(Ranking.created_at.desc()).first()
    return jsonify([{'id': topic.id, 'name': topic.name} for topic in latest_ranking.topics]) if latest_ranking else jsonify([])

@app.route('/topics/<int:topic_id>')
def get_topic_insights(topic_id):
    insights = Insight.query.filter_by(topic_id=topic_id).all()
    return jsonify([{'type': insight.insight_type, 'content': insight.content} for insight in insights])

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
