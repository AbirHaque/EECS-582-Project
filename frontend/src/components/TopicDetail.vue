<template>
  <div class="max-w-5xl mx-auto p-6">
    <!-- Loading state -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-16">
      <div class="w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mb-4"></div>
      <p class="text-gray-600 font-medium">Loading topic insights...</p>
    </div>
    
    <div v-else class="space-y-8">
      <!-- Hero section with backdrop gradient -->
      <div class="relative bg-gradient-to-br from-blue-50 via-white to-indigo-50 rounded-2xl p-6 shadow-sm overflow-hidden">
        <div class="absolute right-0 top-0 w-64 h-64 bg-gradient-to-bl from-blue-100 to-purple-100 rounded-full filter blur-3xl opacity-70 -mr-20 -mt-20"></div>
        <div class="absolute left-0 bottom-0 w-40 h-40 bg-gradient-to-tr from-blue-200 to-indigo-100 rounded-full filter blur-2xl opacity-70 -ml-10 -mb-10"></div>
        
        <div class="relative">
          <router-link to="/" 
                     class="inline-flex items-center gap-2 text-blue-600 font-medium mb-3 group">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 transition-transform group-hover:-translate-x-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to Topics
          </router-link>
          
          <div class="mt-3">
            <h1 class="text-3xl sm:text-4xl font-bold text-gray-800 tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-700 to-indigo-800">
              {{ topic.name }}
            </h1>
            <p class="mt-2 text-gray-600">
              Detailed insights and analysis for this trending topic
            </p>
          </div>
        </div>
      </div>
      
      <div class="bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden">
        <div class="px-6 py-4 bg-gradient-to-r from-gray-50 to-slate-100 border-b border-gray-200 flex justify-between items-center cursor-pointer" @click="toggleSection('insights')">
          <h2 class="text-xl font-semibold text-gray-800">Insights Summary</h2>
          <div class="flex items-center">
            <div class="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <svg v-if="openSections.insights" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 ml-2 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 ml-2 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </div>
        <div v-if="openSections.insights" class="p-6">
          <div v-if="latestSummary" class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-5 border border-blue-100">
            <div class="flex gap-4">
              <div class="flex-shrink-0">
                <div class="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center shadow-sm">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </div>
              </div>
              <div>
                <h3 class="font-semibold text-blue-900 mb-2 text-lg">{{ latestSummary.type.charAt(0).toUpperCase() + latestSummary.type.slice(1) }}</h3>
                <div class="text-blue-800 leading-relaxed">{{ latestSummary.content }}</div>
              </div>
            </div>
          </div>
          <div v-else class="flex flex-col items-center justify-center py-10 text-gray-500 bg-gray-50 rounded-lg">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-gray-400 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            <p class="font-medium">No insights available for this topic yet.</p>
            <p class="text-sm mt-1">Our system is continuously analyzing new data.</p>
          </div>
        </div>
      </div>
      
      <!-- Sentiment Analysis -->
      <div class="bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden">
        <div class="px-6 py-4 bg-gradient-to-r from-purple-50 to-indigo-50 border-b border-gray-200 flex justify-between items-center cursor-pointer" @click="toggleSection('sentiment')">
          <h2 class="text-xl font-semibold text-gray-800">Public Sentiment Analysis</h2>
          <div class="flex items-center">
            <div class="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <svg v-if="openSections.sentiment" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 ml-2 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 ml-2 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </div>
        <div v-if="openSections.sentiment" class="p-6 grid grid-cols-1 lg:grid-cols-2 gap-8">
          <!-- Sentiment chart -->
          <div v-if="sentimentData.sentiments" class="bg-white rounded-lg shadow-sm border border-gray-100 p-4">
            <h3 class="text-lg font-semibold text-gray-800 mb-4">Overall Sentiment</h3>
            <div class="space-y-4">
              <div v-for="(value, sentiment) in filteredSentiments" :key="sentiment" 
                  class="relative">
                <div class="flex justify-between mb-2">
                  <span class="font-semibold text-gray-700 flex items-center">
                    <div :class="['w-3 h-3 rounded-full mr-2', getSentimentDotColor(sentiment)]"></div>
                    {{ sentiment }}
                  </span>
                  <span class="font-semibold" :class="getSentimentTextColor(sentiment)">{{ value }}%</span>
                </div>
                <div class="h-3 w-full bg-gray-200 rounded-full overflow-hidden">
                  <div class="h-full transition-all duration-700 ease-out rounded-full" 
                      :style="{ width: value + '%', backgroundColor: sentimentColors[sentiment] || '#9E9E9E' }">
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Emotions chart -->
          <div v-if="sentimentData.emotions" class="bg-white rounded-lg shadow-sm border border-gray-100 p-4">
            <h3 class="text-lg font-semibold text-gray-800 mb-4">Emotional Tone</h3>
            <div class="space-y-4">
              <div v-for="(value, emotion) in filteredEmotions" :key="emotion"
                  class="relative">
                <div class="flex justify-between mb-2">
                  <span class="font-semibold text-gray-700 flex items-center">
                    <div :class="['w-3 h-3 rounded-full mr-2', getEmotionDotColor(emotion)]"></div>
                    {{ emotion }}
                  </span>
                  <span class="font-semibold" :class="getEmotionTextColor(emotion)">{{ value }}%</span>
                </div>
                <div class="h-3 w-full bg-gray-200 rounded-full overflow-hidden">
                  <div class="h-full transition-all duration-700 ease-out rounded-full" 
                      :style="{ width: value + '%', backgroundColor: emotionColors[emotion] || '#9E9E9E' }">
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Social Media Posts -->
      <div class="bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden">
        <div class="px-6 py-4 bg-gradient-to-r from-blue-50 to-indigo-50 border-b border-gray-200 flex justify-between items-center cursor-pointer" @click="toggleSection('socialMedia')">
          <div>
            <h2 class="text-xl font-semibold text-gray-800">Social Media Posts</h2>
            <p class="text-sm text-gray-600 mt-1">Recent mentions from across platforms</p>
          </div>
          <div class="flex items-center">
            <div class="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
              </svg>
            </div>
            <svg v-if="openSections.socialMedia" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 ml-2 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 ml-2 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </div>
        
        <div v-if="openSections.socialMedia && socialPosts.length" class="divide-y divide-gray-100 max-h-96 overflow-y-auto">
          <div v-for="(post, index) in socialPosts" :key="post.id" 
              class="p-5 hover:bg-gray-50 transition-colors relative border-l-4" 
              :class="[index % 2 === 0 ? 'border-blue-100' : 'border-indigo-100']">
            <p class="text-gray-800 mb-3 leading-relaxed">{{ post.content }}</p>
            <div class="flex items-center gap-3 text-sm text-gray-500">
              <div class="flex items-center gap-1">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>{{ formatPostTime(post.created_at) }}</span>
              </div>
              <div class="w-1 h-1 rounded-full bg-gray-300"></div>
              <div class="flex items-center gap-1">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
                </svg>
                <span>Social Media</span>
              </div>
            </div>
          </div>
        </div>
        
        <div v-if="openSections.socialMedia && !socialPosts.length" class="flex flex-col items-center justify-center py-12 text-gray-500 bg-gray-50">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 text-gray-300 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          <p class="font-medium text-gray-600">No social media posts available</p>
          <p class="text-sm mt-1">We're collecting mentions for this topic</p>
        </div>
      </div>
      
      <!-- Footer -->
      <div class="border-t border-gray-200 pt-4 mt-8">
        <p class="text-center text-sm text-gray-500">
          Topic data is updated automatically as new information becomes available
        </p>
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
      },
      openSections: {
        insights: true,
        sentiment: true,
        socialMedia: true
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
  methods: {
    // Format post timestamp to readable format
    formatPostTime(timestamp) {
      const date = new Date(timestamp);
      return date.toLocaleString('en-US', { 
        month: 'short', 
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit'
      });
    },
    
    // Get text color class based on sentiment
    getSentimentTextColor(sentiment) {
      switch(sentiment) {
        case 'Positive': return 'text-green-700';
        case 'Negative': return 'text-red-700';
        case 'Neutral': return 'text-gray-700';
        default: return 'text-gray-700';
      }
    },
    
    // Get dot color class based on sentiment
    getSentimentDotColor(sentiment) {
      switch(sentiment) {
        case 'Positive': return 'bg-green-500';
        case 'Negative': return 'bg-red-500';
        case 'Neutral': return 'bg-gray-500';
        default: return 'bg-gray-500';
      }
    },
    
    // Get text color class based on emotion
    getEmotionTextColor(emotion) {
      switch(emotion) {
        case 'Joy': return 'text-yellow-700';
        case 'Anger': return 'text-red-700';
        case 'Sadness': return 'text-indigo-700';
        case 'Fear': return 'text-purple-700';
        case 'Surprise': return 'text-cyan-700';
        default: return 'text-gray-700';
      }
    },
    
    // Get dot color class based on emotion
    getEmotionDotColor(emotion) {
      switch(emotion) {
        case 'Joy': return 'bg-yellow-500';
        case 'Anger': return 'bg-red-500';
        case 'Sadness': return 'bg-indigo-500';
        case 'Fear': return 'bg-purple-500';
        case 'Surprise': return 'bg-cyan-500';
        default: return 'bg-gray-500';
      }
    },
    toggleSection(section) {
      this.openSections[section] = !this.openSections[section];
    },
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