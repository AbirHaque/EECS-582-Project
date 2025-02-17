<template>
  <div class="home-page">
    <div class="header">
      <h1>Trending News Topics</h1>
      <div class="update-info">
        <div class="status-container">
          <span :class="{ 'indicator': true, 'updating': isUpdating }"></span>
          <span class="status-text">
            {{ isUpdating ? 'Updating...' : 'Last updated: ' + lastUpdateTime }}
          </span>
        </div>
      </div>
    </div>

    <div class="ranking-info">
      <p>Current Ranking: #{{ currentRankingId }}</p>
      <button @click="toggleRankingHistory" class="history-button">
        {{ showHistory ? 'Hide' : 'Show' }} Ranking History
      </button>
    </div>

    <div v-if="showHistory" class="ranking-history">
      <h3>Rankings from the last hour:</h3>
      <div class="history-list">
        <div v-for="ranking in rankingHistory" :key="ranking.id" class="history-item">
          <div class="history-header">
            <strong>Ranking #{{ ranking.id }}</strong>
            <span>{{ formatTime(ranking.created_at) }}</span>
          </div>
          <div class="topic-changes" v-if="getTopicChanges(ranking)">
            {{ getTopicChanges(ranking) }}
          </div>
        </div>
      </div>
    </div>

    <div v-if="error" class="error">
      {{ error }}
    </div>
    <div v-else>
      <ul>
        <li v-for="topic in topics" :key="topic.id" :class="{ 'new-topic': newTopics.includes(topic.id) }">
          <router-link :to="{ path: '/topic/' + topic.id, query: { name: topic.name } }">{{ topic.name }}</router-link>
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
    async fetchTopics() {
      this.isUpdating = true;
      try {
        await new Promise(resolve => setTimeout(resolve, 500));
        
        const response = await axios.get('http://localhost:5000/topics');
        console.log("API Response:", response.data);
        
        this.currentRankingId = response.data.ranking_id;
        const currentTopics = response.data.topics;
        
        const currentTopicIds = new Set(currentTopics.map(topic => topic.id));
        this.newTopics = currentTopics
          .filter(topic => !this.previousTopicIds.has(topic.id))
          .map(topic => topic.id);
        
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
    async fetchRankingHistory() {
      try {
        const response = await axios.get('http://localhost:5000/rankings/history');
        this.rankingHistory = response.data;
      } catch (error) {
        console.error('Error fetching ranking history:', error);
      }
    },
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
    toggleRankingHistory() {
      this.showHistory = !this.showHistory;
      if (this.showHistory) {
        this.fetchRankingHistory();
      }
    }
  },
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
  beforeUnmount() {
    if (this.pollInterval) clearInterval(this.pollInterval);
    if (this.historyPollInterval) clearInterval(this.historyPollInterval);
  }
};
</script>

<style>
.home-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.ranking-info {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
}

.history-button {
  padding: 8px 16px;
  background-color: #2196F3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.history-button:hover {
  background-color: #1976D2;
}

.ranking-history {
  background-color: #f5f5f5;
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 20px;
}

.history-list {
  max-height: 300px;
  overflow-y: auto;
}

.history-item {
  padding: 10px;
  border-bottom: 1px solid #ddd;
  background-color: white;
  margin-bottom: 8px;
  border-radius: 4px;
}

.history-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
}

.topic-changes {
  font-size: 0.9em;
  color: #666;
  margin-top: 5px;
}

.status-container {
  display: flex;
  align-items: center;
  gap: 8px;
}

.indicator {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #4CAF50;
  transition: background-color 0.3s ease;
}

.updating {
  background-color: #FFA000;
  animation: blink 1s infinite;
}

@keyframes blink {
  0% { opacity: 1; }
  50% { opacity: 0.4; }
  100% { opacity: 1; }
}

.status-text {
  font-size: 0.9em;
  color: #666;
}

h1 {
  color: #333;
  margin: 0;
}

ul {
  list-style: none;
  padding: 0;
}

li {
  margin: 10px 0;
  padding: 10px;
  border-bottom: 1px solid #eee;
  transition: background-color 0.3s ease;
}

.new-topic {
  background-color: #e3f2fd;
  animation: fadeBackground 3s forwards;
}

@keyframes fadeBackground {
  from { background-color: #e3f2fd; }
  to { background-color: transparent; }
}

.error {
  color: red;
  padding: 10px;
  background-color: #ffebee;
  border-radius: 4px;
  margin: 10px 0;
}

a {
  color: #2196F3;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}
</style>