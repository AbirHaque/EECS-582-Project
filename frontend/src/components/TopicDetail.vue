<template>
  <div class="max-w-3xl mx-auto p-5">
    <div v-if="loading">
      <p>Loading topic insights...</p>
    </div>
    <div v-else>
      <div class="flex flex-col items-start mb-5">
        <router-link to="/" class="px-4 py-2 bg-blue-500 text-white rounded no-underline hover:bg-blue-700">Home</router-link>
        <h1 class="mt-2 text-2xl font-bold">{{ topic.name }}</h1>
      </div>
      <div class="mt-5">
        <h2 class="text-xl font-semibold">Insights:</h2>
        <div v-if="latestSummary">
          <p><strong>{{ latestSummary.type }}:</strong> {{ latestSummary.content }}</p>
        </div>
        <p v-else>No insights available.</p>
      </div>
      <div class="mt-5" v-if="socialPosts.length">
        <h2 class="text-xl font-semibold">Social Media Posts:</h2>
        <div class="max-h-72 overflow-y-auto">
          <ul class="list-none p-0">
            <li v-for="post in socialPosts" :key="post.id" class="border-b border-gray-300 py-2">
              <p>{{ post.content }}</p>
              <small>{{ new Date(post.created_at).toLocaleString() }}</small>
            </li>
          </ul>
        </div>
      </div>
      <div class="mt-5" v-else>
        <p>No social media posts available.</p>
      </div>
      <div class="mt-7 p-4 bg-gray-100 rounded-lg" v-if="sentimentData">
        <h2 class="text-xl font-semibold mb-4">Public Sentiment Analysis</h2>
        <div class="mb-5" v-if="sentimentData.sentiments">
          <h3 class="text-lg font-semibold">Overall Sentiment</h3>
          <div class="mt-2">
            <div class="flex flex-col gap-2">
              <div v-for="(value, sentiment) in filteredSentiments" :key="sentiment" 
                class="h-8 rounded text-white flex items-center pl-2 font-bold transition-all duration-500" 
                :style="{ width: Math.max(value, 10) + '%', backgroundColor: sentimentColors[sentiment] || '#9E9E9E' }">
                <span>{{ sentiment }}: {{ value }}%</span>
              </div>
            </div>
          </div>
        </div>
        <div class="mb-5" v-if="sentimentData.emotions">
          <h3 class="text-lg font-semibold">Emotional Tone</h3>
          <div class="mt-2">
            <div class="flex flex-col gap-2">
              <div v-for="(value, emotion) in filteredEmotions" :key="emotion" 
                class="h-8 rounded text-white flex items-center pl-2 font-bold transition-all duration-500" 
                :style="{ width: Math.max(value, 10) + '%', backgroundColor: emotionColors[emotion] || '#9E9E9E' }">
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