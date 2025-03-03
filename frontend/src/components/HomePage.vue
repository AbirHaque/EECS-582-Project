<template>
  <div class="max-w-3xl mx-auto p-5">
    <div class="flex justify-between items-center mb-5">
      <h1 class="text-3xl font-bold text-gray-800 m-0">Trending News Topics</h1>
      <div class="flex items-center gap-2">
        <span :class="['inline-block w-2 h-2 rounded-full transition-colors', isUpdating ? 'bg-yellow-500 animate-pulse' : 'bg-green-500']"></span>
        <span class="text-sm text-gray-500">
          {{ isUpdating ? 'Updating...' : 'Last updated: ' + lastUpdateTime }}
        </span>
      </div>
    </div>
    <div class="flex items-center gap-4 mb-5">
      <p>Current Ranking: #{{ currentRankingId }}</p>
      <button @click="toggleRankingHistory" class="px-4 py-2 bg-blue-500 text-white rounded text-sm hover:bg-blue-700">
        {{ showHistory ? 'Hide' : 'Show' }} Ranking History
      </button>
    </div>
    <div v-if="showHistory" class="bg-gray-100 p-4 rounded mb-5">
      <h3 class="text-lg font-semibold mb-2">Rankings from the last hour:</h3>
      <div class="max-h-72 overflow-y-auto">
        <div v-for="ranking in rankingHistory" :key="ranking.id" class="p-2 border-b border-gray-300 bg-white mb-2 rounded">
          <div class="flex justify-between mb-1">
            <strong>Ranking #{{ ranking.id }}</strong>
            <span>{{ formatTime(ranking.created_at) }}</span>
          </div>
          <div class="text-sm text-gray-500 mt-1" v-if="getTopicChanges(ranking)">
            {{ getTopicChanges(ranking) }}
          </div>
        </div>
      </div>
    </div>
    <div v-if="error" class="text-red-500 p-2 bg-red-100 rounded my-2">
      {{ error }}
    </div>
    <div v-else>
      <ul class="list-none p-0">
        <li v-for="topic in topics" :key="topic.id" :class="[ 'my-2 p-2 border-b border-gray-200 transition-colors', newTopics.includes(topic.id) ? 'bg-blue-100' : '' ]">
          <router-link :to="{ path: '/topic/' + topic.id, query: { name: topic.name } }" class="text-blue-500 no-underline hover:underline">
            {{ topic.name }}
          </router-link>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: "HomePage",
  data() {
    return {
      topics: [],
      error: null,
      pollInterval: null,
      lastUpdateTime: 'Never',
      isUpdating: false,
      newTopics: [],
      previousTopicIds: new Set(),
      currentRankingId: null,
      rankingHistory: [],
      showHistory: false,
      historyPollInterval: null
    };
  },
  methods: {
    // Fetches current topics from the API
    async fetchTopics() {
      this.isUpdating = true;
      try {
        // Small delay to make loading state visible to user
        await new Promise(resolve => setTimeout(resolve, 500));
        // Make API request to get current topics
        const response = await axios.get('http://localhost:5000/topics');
        console.log("API Response:", response.data);
        // Update the current ranking ID and topics data
        this.currentRankingId = response.data.ranking_id;
        const currentTopics = response.data.topics;
        // Determine which topics are new since last update
        const currentTopicIds = new Set(currentTopics.map(topic => topic.id));
        this.newTopics = currentTopics
          .filter(topic => !this.previousTopicIds.has(topic.id))
          .map(topic => topic.id);
        // Update component state with new data
        this.topics = currentTopics;
        this.previousTopicIds = currentTopicIds;
        this.error = null;
        this.lastUpdateTime = new Date().toLocaleTimeString();
        
        setTimeout(() => {
          this.newTopics = [];
        }, 3000);
      } catch (error) {
        console.error('Error fetching topics:', error);
        this.error = 'Failed to load topics. Please refresh the page.';
      } finally {
        setTimeout(() => {
          this.isUpdating = false;
        }, 500);
      }
    },
    // Fetches historical ranking data from the API
    async fetchRankingHistory() {
      try {
        const response = await axios.get('http://localhost:5000/rankings/history');
        this.rankingHistory = response.data;
      } catch (error) {
        console.error('Error fetching ranking history:', error);
      }
    },
    // Formats ISO timestamp into user-friendly local time
    formatTime(isoString) {
      const utcDate = new Date(isoString + 'Z');  // Explicitly handle as UTC
      return utcDate.toLocaleTimeString('en-US', { 
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: true,
        timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone // Use local timezone
      });
    },
    // Analyzes changes between two consecutive rankings
    getTopicChanges(ranking) {
      if (this.rankingHistory.length < 2) return null;
      const currentIndex = this.rankingHistory.findIndex(r => r.id === ranking.id);
      if (currentIndex === this.rankingHistory.length - 1) return null;
      
      const nextRanking = this.rankingHistory[currentIndex + 1];
      const currentTopicIds = new Set(ranking.topics.map(t => t.id));
      const nextTopicIds = new Set(nextRanking.topics.map(t => t.id));
      
      const added = ranking.topics.filter(t => !nextTopicIds.has(t.id));
      const removed = nextRanking.topics.filter(t => !currentTopicIds.has(t.id));
      
      if (added.length === 0 && removed.length === 0) return null;
      
      let changes = [];
      if (added.length > 0) changes.push(`Added: ${added.map(t => t.name).join(', ')}`);
      if (removed.length > 0) changes.push(`Removed: ${removed.map(t => t.name).join(', ')}`);
      
      return changes.join(' | ');
    },
    // Toggles the visibility of the ranking history section
    toggleRankingHistory() {
      this.showHistory = !this.showHistory;
      if (this.showHistory) {
        this.fetchRankingHistory();
      }
    }
  },
  // Lifecycle hook: Called when component is created
  created() {
    this.fetchTopics();
    this.pollInterval = setInterval(() => {
      this.fetchTopics();
    }, 10000);
    
    this.historyPollInterval = setInterval(() => {
      if (this.showHistory) {
        this.fetchRankingHistory();
      }
    }, 30000);
  },
  // Lifecycle hook: Called right before component is destroyed
  beforeUnmount() {
    if (this.pollInterval) clearInterval(this.pollInterval);
    if (this.historyPollInterval) clearInterval(this.historyPollInterval);
  }
};
</script>