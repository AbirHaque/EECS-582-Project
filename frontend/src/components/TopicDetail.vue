<template>
  <div class="home-page">
    <!-- Loading state when data is being fetched -->
    <div v-if="loading">
      <p>Loading topic insights...</p>
    </div>
    <!-- Main content when data is loaded -->
    <div v-else>
      <div class="header">
        <!-- Header section with navigation and topic title -->
        <router-link to="/" class="home-button">Home</router-link>
        <h1>{{ topic.name }}</h1>
      </div>
      <!-- Insights section displaying summary information -->
      <div class="insights">
        <h2>Insights:</h2>
        <div v-if="latestSummary">
          <p><strong>{{ latestSummary.type }}:</strong> {{ latestSummary.content }}</p>
        </div>
        <p v-else>No insights available.</p>
      </div>
      <!-- New social posts section -->
      <div class="social-posts" v-if="socialPosts.length">
        <h2>Social Media Posts:</h2>
        <div class="social-posts-container">
          <ul>
            <li v-for="post in socialPosts" :key="post.id">
              <p>{{ post.content }}</p>
              <small>{{ new Date(post.created_at).toLocaleString() }}</small>
            </li>
          </ul>
        </div>
      </div>
      <div class="social-posts" v-else>
        <p>No social media posts available.</p>
      </div>
      
      <!-- Sentiment Analysis Section -->
      <div class="sentiment-section" v-if="sentimentData">
        <h2>Public Sentiment Analysis</h2>
        
        <!-- Sentiments Chart -->
        <div class="sentiment-chart" v-if="sentimentData.sentiments">
          <h3>Overall Sentiment</h3>
          <div class="chart-container">
            <div class="sentiment-bars">
              <div v-for="(value, sentiment) in filteredSentiments" :key="sentiment" 
                   class="sentiment-bar" 
                   :style="{ width: Math.max(value, 10) + '%', 'background-color': sentimentColors[sentiment] || '#9E9E9E' }">
                <span>{{ sentiment }}: {{ value }}%</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Emotions Chart -->
        <div class="sentiment-chart" v-if="sentimentData.emotions">
          <h3>Emotional Tone</h3>
          <div class="chart-container">
            <div class="emotion-bars">
              <div v-for="(value, emotion) in filteredEmotions" :key="emotion" 
                   class="emotion-bar" 
                   :style="{ width: Math.max(value, 10) + '%', 'background-color': emotionColors[emotion] || '#9E9E9E' }">
                <span>{{ emotion }}: {{ value }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: "TopicDetail",
  data() {
    return {
      topic: null, // Stores the current topic object
      insights: [], // Stores the insights related to this topic
      socialPosts: [], // added to store social media posts
      sentimentData: null, // Stores sentiment analysis data
      loading: true, // Controls loading state visibility
      sentimentColors: {
        'Positive': '#4CAF50', // Green
        'Negative': '#F44336', // Red
        'Neutral': '#9E9E9E'  // Gray
      },
      emotionColors: {
        'Joy': '#FFEB3B',      // Yellow
        'Anger': '#F44336',    // Red
        'Sadness': '#3F51B5',  // Indigo
        'Fear': '#673AB7',     // Deep Purple
        'Surprise': '#00BCD4'  // Cyan
      }
    };
  },
  computed: {
    // Computed property that returns the most recent summary insight
    latestSummary() {
      const summaries = this.insights.filter(i => i.type === 'summary');
      return summaries.length ? summaries[summaries.length - 1] : null;
    },
    // Computed property that returns only sentiments with values > 0
    filteredSentiments() {
      if (!this.sentimentData || !this.sentimentData.sentiments) return {};
      
      // Filter out sentiments with 0 values
      const result = {};
      Object.entries(this.sentimentData.sentiments).forEach(([sentiment, value]) => {
        if (value > 0) {
          result[sentiment] = value;
        }
      });
      
      return result;
    },
    // Computed property that returns only emotions with values > 0
    filteredEmotions() {
      if (!this.sentimentData || !this.sentimentData.emotions) return {};
      
      // Filter out emotions with 0 values
      const result = {};
      Object.entries(this.sentimentData.emotions).forEach(([emotion, value]) => {
        if (value > 0) {
          result[emotion] = value;
        }
      });
      
      return result;
    }
  },
  created() {
    // Extract the topic ID from the route parameters
    const topicId = this.$route.params.id;
    // Fetch topic details and insights from the API
    axios.get(`http://localhost:5000/topics/${topicId}`)
      .then(response => {
        if (Array.isArray(response.data)) {
          this.insights = response.data;
          this.topic = { name: this.$route.query.name || "Topic " + topicId };
        } else {
          this.topic = response.data.topic || response.data;
          this.insights = response.data.insights ?? [];
        }
      })
      .catch(error => {
        console.error('Error fetching topic details:', error);
      })
      .finally(() => {
        this.loading = false;
      });
    // Fetch social media posts
    axios.get(`http://localhost:5000/topics/${topicId}/social`)
      .then(response => {
        this.socialPosts = response.data;
      })
      .catch(error => {
        console.error('Error fetching social media posts:', error);
      });
      
    // Fetch sentiment analysis
    axios.get(`http://localhost:5000/topics/${topicId}/sentiment`)
      .then(response => {
        if (response.data && response.data.sentiment) {
          this.sentimentData = response.data.sentiment;
        }
      })
      .catch(error => {
        console.error('Error fetching sentiment analysis:', error);
      });
  }
};
</script>

<style scoped>
.home-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}
.header {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  margin-bottom: 20px;
}
a {
  color: #2196F3;
  text-decoration: none;
}
a:hover {
  text-decoration: underline;
}
.insights {
  margin-top: 20px;
}
.home-button {
  padding: 8px 16px;
  background-color: #2196F3;
  color: white;
  border-radius: 4px;
  text-decoration: none;
  transition: background-color 0.3s ease;
}
.home-button:hover {
  background-color: #1976D2;
}
.social-posts {
  margin-top: 20px;
}

.social-posts-container {
  max-height: 300px; /* Adjust height for max 3 posts */
  overflow-y: auto;
}

.social-posts ul {
  list-style: none;
  padding: 0;
}
.social-posts li {
  border-bottom: 1px solid #ddd;
  padding: 10px 0;
}

/* Sentiment Analysis Styles */
.sentiment-section {
  margin-top: 30px;
  padding: 15px;
  background-color: #f5f5f5;
  border-radius: 8px;
}

.sentiment-chart {
  margin-bottom: 20px;
}

.chart-container {
  margin-top: 10px;
}

.sentiment-bars, .emotion-bars {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.sentiment-bar, .emotion-bar {
  height: 30px;
  border-radius: 4px;
  color: white;
  display: flex;
  align-items: center;
  padding-left: 10px;
  font-weight: bold;
  transition: width 0.5s ease;
}
</style>