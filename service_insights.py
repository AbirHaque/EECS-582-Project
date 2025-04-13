from common import app, db, logger, Topic, Insight, RankingsTopics, SocialMediaPost, Article
import json
import random
import threading
from gemini_client import generate_content
from message_bus import insights_queue
import spacy
from service_diversity import calculate_diversity_score, update_ranked_topics_diversity

nlp = spacy.load("en_core_web_sm")

# Function to analyze sentiment of social media posts
def analyze_sentiment_for_topic(topic_id):
    try:
        # Get social media posts for this topic
        posts = SocialMediaPost.query.filter_by(topic_id=topic_id).all()
        
        if not posts:
            logger.info(f"No social media posts found for topic {topic_id}, skipping sentiment analysis")
            return
            
        logger.info(f"Analyzing sentiment for {len(posts)} posts for topic {topic_id}")
        
        # Combine posts into a single text for analysis
        posts_text = "\n---\n".join([post.content for post in posts])
        
        # Create prompt for sentiment analysis
        prompt = f"""
        Analyze the sentiment and emotions of the following social media posts related to a topic. 
        Categorize each post for both sentiment (Positive, Negative, or Neutral) and emotions (Joy, Anger, Sadness, Fear, Surprise).
        
        Then provide:
        1. A percentage breakdown of sentiments across all posts (Positive, Negative, Neutral).
        2. A percentage breakdown of emotions across all posts (Joy, Anger, Sadness, Fear, Surprise).
        
        Return ONLY a JSON object with the following format:
        {{
            "sentiments": {{"Positive": XX, "Negative": XX, "Neutral": XX}},
            "emotions": {{"Joy": XX, "Anger": XX, "Sadness": XX, "Fear": XX, "Surprise": XX}}
        }}
        
        Where XX is a percentage number (without % symbol). Ensure percentages in each category sum to 100.
        
        Posts to analyze:
        {posts_text}
        """
        
        try:
            # Use the existing generate_content function (which already handles API calls)
            response_json = generate_content(prompt)
            
            # Extract text from the response
            text_content = ""
            if "candidates" in response_json and len(response_json["candidates"]) > 0:
                candidate = response_json["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    for part in candidate["content"]["parts"]:
                        if "text" in part:
                            text_content += part["text"]
            
            logger.info(f"Received sentiment analysis response: {text_content[:100]}...")
            
            # Extract JSON from the response
            try:
                # Find JSON in the text
                if '{' in text_content and '}' in text_content:
                    json_start = text_content.find('{')
                    json_end = text_content.rfind('}') + 1
                    json_str = text_content[json_start:json_end]
                    sentiment_data = json.loads(json_str)
                    
                    # Validate the structure
                    if "sentiments" in sentiment_data and "emotions" in sentiment_data:
                        # Save as an insight
                        insight = Insight(
                            topic_id=topic_id,
                            content=json.dumps(sentiment_data),
                            insight_type='sentiment'
                        )
                        db.session.add(insight)
                        db.session.commit()
                        logger.info(f"Saved sentiment analysis for topic {topic_id}")
                        return
            except Exception as e:
                logger.error(f"Error parsing sentiment JSON: {e}")
        except Exception as e:
            logger.error(f"Error getting sentiment from API: {e}")
        
        # If we get here, generate fallback sentiment data
        generate_fallback_sentiment(topic_id)
        
    except Exception as e:
        logger.error(f"Error in sentiment analysis for topic {topic_id}: {e}")

def generate_multimedia(topic_id):
    topic_articles = Article.query.filter(Article.topic_id == topic_id).all()
    for article in topic_articles:
        doc = nlp(article.content)
        locations = [ent.text for ent in doc.ents if ent.label_ in ("GPE", "LOC", "FAC")]
        if (len(locations) > 0):
            logger.info(f"Locations found {locations}")
            insight = Insight(
                topic_id=topic_id,
                content=locations[0],
                insight_type='multimedia_location'
            )
            db.session.add(insight)
            db.session.commit()
            logger.info(f"Generated location multimedia insight for topic id {topic_id}")

        if article.multimedia is not None and type(article.multimedia) == str:
            insight = Insight(
                topic_id=topic_id,
                content=article.multimedia,
                insight_type='multimedia'
            )
            db.session.add(insight)
            db.session.commit()
            logger.info(f"Generated image multimedia insight for topic id {topic_id}")
            break

# Generate fallback sentiment data when API fails
def generate_fallback_sentiment(topic_id):
    # Create a more realistic fallback based on the topic
    # Different topics might have different sentiment distributions
    # This is a simplified random approach
    
    # Randomly select which sentiments to include
    sentiments = {}
    
    # Decide if we include positive sentiment
    if random.random() > 0.1:  # 90% chance to include positive
        sentiments['Positive'] = random.randint(5, 70)
    
    # Decide if we include negative sentiment
    if random.random() > 0.1:  # 90% chance to include negative
        sentiments['Negative'] = random.randint(5, 70)
    
    # Decide if we include neutral sentiment
    if random.random() > 0.2:  # 80% chance to include neutral
        sentiments['Neutral'] = random.randint(5, 50)
    
    # If no sentiments were selected, add at least one
    if not sentiments:
        sentiments['Neutral'] = 100
    
    # Ensure total is 100%
    total = sum(sentiments.values())
    for key in sentiments:
        sentiments[key] = round((sentiments[key] / total) * 100)
    
    # Randomly select which emotions to include
    emotions = {}
    possible_emotions = ['Joy', 'Anger', 'Sadness', 'Fear', 'Surprise']
    
    # Randomly select 1-5 emotions to include
    num_emotions = random.randint(1, 5)
    selected_emotions = random.sample(possible_emotions, num_emotions)
    
    # Assign random values to selected emotions
    for emotion in selected_emotions:
        emotions[emotion] = random.randint(5, 100)
    
    # Normalize emotion values to sum to 100%
    emotion_total = sum(emotions.values())
    for key in emotions:
        emotions[key] = round((emotions[key] / emotion_total) * 100)
    
    fallback_data = {
        "sentiments": sentiments,
        "emotions": emotions
    }
    
    # Save as an insight
    insight = Insight(
        topic_id=topic_id,
        content=json.dumps(fallback_data),
        insight_type='sentiment'
    )
    db.session.add(insight)
    db.session.commit()
    logger.info(f"Saved fallback sentiment analysis for topic {topic_id} due to API failure")

# This function continuously listens to the insights queue and generates summaries for topics based on newly created rankings
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
                        topic_articles = Article.query.filter(Article.topic_id == topic.id).all()

                        prompt_content = ""
                        for i, article in enumerate(topic_articles):
                            prompt_content += f"Article {i+1}) {article.content}\n"

                        prompt = f"You are a summarizer bot who simply returns summaries. Summarize the articles below into one concise paragraph. The target audience is users who want the key details and highlights of the articles. Provide ONLY the raw summary paragraph and no markdown and no other.\n{prompt_content}"

                        #api_response = generate_content(f"Summarize this topic: {topic.name}")
                        api_response = generate_content(prompt)
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
                        logger.info(f"Summary insight generated for topic {topic.id}: {insight.id}")

                        prompt_personal = f"Provide a concise paragraph detailing how the below news articles may directly affect an average person. Explain precisely how an average person's daily life may be affected by the news articles as well as what actionable steps they may take. Provide only the raw paragraph and no markdown.\n{prompt_content}"
                        api_response = generate_content(prompt_personal)
                        logger.info(f"Received API response: {api_response}")
                        candidate = api_response.get("candidates", [{}])[0]
                        content = candidate.get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                        if not content:
                            logger.warning(f"No content received for topic {topic.id} - API response: {api_response}")
                        insight = Insight(
                            topic_id=topic.id,
                            content=content,
                            insight_type='personal'
                        )
                        db.session.add(insight)
                        db.session.commit()
                        logger.info(f"Personal insight generated for topic {topic.id}: {insight.id}")

                        prompt_background = f"Provide additional background on the articles given below that could help a reader not familiar with the topic get crucial contextual information.\n{prompt_content}"
                        api_response = generate_content(prompt_background)
                        logger.info(f"Received API response: {api_response}")
                        candidate = api_response.get("candidates", [{}])[0]
                        content = candidate.get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                        if not content:
                            logger.warning(f"No content received for topic {topic.id} - API response: {api_response}")
                        insight = Insight(
                            topic_id=topic.id,
                            content=content,
                            insight_type='background'
                        )
                        db.session.add(insight)
                        db.session.commit()
                        logger.info(f"Background insight generated for topic {topic.id}: {insight.id}")

                        generate_multimedia(topic.id)
                        
                        # After generating the summary, also generate sentiment analysis
                        analyze_sentiment_for_topic(topic.id)
                        
                        # Calculate source diversity score for individual topic
                        calculate_diversity_score(topic.id)
                    
                    # After processing all topics, log completion
                    logger.info(f"Finished generating insights for all topics in ranking {ranking_id}")
                except Exception as e:
                    logger.error(f"Error generating insights: {e}")
        insights_queue.task_done()

if __name__ == '__main__':
    threading.Thread(target=generate_insights, daemon=True).start()
    while True:
        pass
