from common import app, db, logger, Topic, Insight, Article
import json
import threading
from sqlalchemy import func, distinct, select
from urllib.parse import urlparse
import re
from collections import Counter

def calculate_diversity_score(topic_id):
    """
    Calculate a source diversity score for a topic based on the number and variety 
    of sources ingested for that particular topic.
    
    The score is based on:
    1. Number of different domains/sources 
    2. Distribution of articles across different domains
    3. Variety of content types (long-form, short-form, etc.)
    
    Returns a score from 0-100, with higher scores indicating more diverse sources.
    """
    try:
        # Explicitly select only the columns we need to avoid multimedia column error
        articles_query = select(
            Article.url,
            Article.content
        ).where(Article.topic_id == topic_id)
        
        result = db.session.execute(articles_query)
        articles_data = result.fetchall()
        
        if not articles_data:
            logger.info(f"No articles found for topic {topic_id}, skipping diversity analysis")
            return None
            
        logger.info(f"Calculating source diversity for {len(articles_data)} articles for topic {topic_id}")
        
        # 1. Count number of different domains/sources
        domains = []
        content_lengths = []
        
        for article in articles_data:
            if article.url:
                # Extract domain from URL
                domain = urlparse(article.url).netloc
                domains.append(domain)
            
            # Calculate content length for content type diversity
            if article.content:
                content_lengths.append(len(article.content))
        
        # If no valid domains found, return None
        if not domains:
            return None
        
        # Calculate metrics
        unique_domains_count = len(set(domains))
        total_domains = len(domains)
        
        # Calculate domain distribution (Gini coefficient-like measure)
        domain_counts = Counter(domains)
        domain_distribution = list(domain_counts.values())
        
        # A perfect distribution would have all domains with equal count
        # Calculate how far the actual distribution is from perfect
        if len(domain_distribution) > 1:
            max_value = max(domain_distribution)
            min_value = min(domain_distribution)
            distribution_score = 1 - ((max_value - min_value) / (max_value + min_value))
        else:
            distribution_score = 0  # Only one domain
        
        # Calculate content length diversity
        if content_lengths:
            content_std_dev = 0
            if len(content_lengths) > 1:
                avg_length = sum(content_lengths) / len(content_lengths)
                content_std_dev = (sum((length - avg_length) ** 2 for length in content_lengths) / len(content_lengths)) ** 0.5
                # Normalize to a 0-1 scale
                content_diversity = min(1, content_std_dev / avg_length)
            else:
                content_diversity = 0
        else:
            content_diversity = 0
        
        # Calculate final score (0-100)
        # Weight the components:
        # - 60% for unique domain count (normalized by log scale to not penalize smaller topics)
        # - 30% for domain distribution 
        # - 10% for content diversity
        
        # Normalize domain count using log scale (1 domain = 0, 10+ domains = 1)
        normalized_domain_count = min(1, max(0, (unique_domains_count - 1) / 9))
        
        # Calculate weighted score
        score = (normalized_domain_count * 0.6 + 
                distribution_score * 0.3 + 
                content_diversity * 0.1) * 100
        
        # Round to nearest integer
        score = round(score)
        
        # Ensure score is between 0-100
        score = max(0, min(100, score))
        
        # Build the detailed data
        diversity_data = {
            "score": score,
            "metrics": {
                "domain_count": unique_domains_count,
                "total_articles": total_domains,
                "domain_distribution": distribution_score,
                "content_diversity": content_diversity
            },
            "domains": [{"domain": domain, "count": count} for domain, count in domain_counts.items()]
        }
        
        # Save as an insight
        insight = Insight(
            topic_id=topic_id,
            content=json.dumps(diversity_data),
            insight_type='source_diversity'
        )
        db.session.add(insight)
        db.session.commit()
        logger.info(f"Saved source diversity score for topic {topic_id}: {score}")
        
        return diversity_data
        
    except Exception as e:
        logger.error(f"Error calculating source diversity for topic {topic_id}: {e}")
        return None

def update_ranked_topics_diversity():
    """Update source diversity scores for topics that appear in the latest ranking"""
    with app.app_context():
        # Get the latest ranking
        from sqlalchemy import desc
        from common import Ranking, RankingsTopics
        
        latest_ranking = db.session.query(Ranking).order_by(desc(Ranking.created_at)).first()
        
        calculated_count = 0
        if latest_ranking:
            # Get topics from this ranking
            ranked_topics = db.session.query(RankingsTopics).filter_by(ranking_id=latest_ranking.id).order_by(RankingsTopics.rank_order).all()
            
            logger.info(f"Calculating diversity scores for {len(ranked_topics)} ranked topics")
            
            for ranked_topic in ranked_topics:
                result = calculate_diversity_score(ranked_topic.topic_id)
                if result:
                    calculated_count += 1
            
            # If we couldn't calculate diversity for any ranked topics,
            # find topics that have articles and calculate for them
            if calculated_count == 0:
                logger.info("No ranked topics had articles. Finding topics with articles...")
                # Find topics that have associated articles
                from sqlalchemy import func, distinct
                topics_with_articles = db.session.query(distinct(Article.topic_id)).filter(Article.topic_id != None).all()
                topic_ids = [t[0] for t in topics_with_articles]
                
                if topic_ids:
                    logger.info(f"Found {len(topic_ids)} topics with articles. Calculating diversity for top 10.")
                    # Limit to 10 topics to avoid excessive processing
                    for topic_id in topic_ids[:10]:
                        calculate_diversity_score(topic_id)
                        calculated_count += 1
                else:
                    logger.info("No topics with articles found in the database.")
            
            logger.info(f"Successfully calculated diversity scores for {calculated_count} topics")
        else:
            logger.info("No rankings found, skipping diversity score calculation")
    
if __name__ == '__main__':
    # This allows running this module directly to update all diversity scores
    with app.app_context():
        update_ranked_topics_diversity()
