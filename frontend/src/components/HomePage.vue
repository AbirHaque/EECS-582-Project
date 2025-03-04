<template>
  <div class="max-w-5xl mx-auto p-6 space-y-8">
    <!-- Hero section with backdrop gradient -->
    <div class="relative bg-gradient-to-br from-blue-50 via-white to-indigo-50 rounded-2xl p-6 mb-8 shadow-sm overflow-hidden">
      <div class="absolute right-0 top-0 w-64 h-64 bg-gradient-to-bl from-blue-100 to-purple-100 rounded-full filter blur-3xl opacity-70 -mr-20 -mt-20"></div>
      <div class="absolute left-0 bottom-0 w-40 h-40 bg-gradient-to-tr from-blue-200 to-indigo-100 rounded-full filter blur-2xl opacity-70 -ml-10 -mb-10"></div>
      
      <div class="relative">
        <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-4">
          <div>
            <h1 class="text-4xl font-extrabold text-gray-800 tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-800">
              InSite <span class="text-gray-700 font-medium">|</span> Trending Now
            </h1>
            <p class="mt-2 text-gray-600 max-w-2xl">Real-time analysis of what's capturing the media's attention right now.</p>
          </div>
          <div class="flex items-center gap-2 bg-white px-4 py-2 rounded-full shadow backdrop-blur-sm bg-opacity-80 border border-gray-100">
            <span :class="['inline-block w-2 h-2 rounded-full transition-colors', 
                         isUpdating ? 'bg-yellow-400 animate-pulse' : 'bg-green-500']"></span>
            <span class="text-sm font-medium text-gray-600">
              {{ isUpdating ? 'Refreshing data...' : 'Updated: ' + lastUpdateTime }}
            </span>
          </div>
        </div>
        
        <div class="flex flex-col sm:flex-row sm:items-center gap-4">
          <div class="px-3 py-1 bg-white bg-opacity-80 text-blue-800 rounded-full font-medium text-sm border border-blue-100 shadow-sm">
            Ranking #{{ currentRankingId }}
          </div>
          <button @click="toggleRankingHistory" 
                class="px-4 py-2 rounded-md flex items-center gap-2 text-sm font-medium transition-all
                      bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800
                      text-white shadow hover:shadow-md">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path v-if="showHistory" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
            {{ showHistory ? 'Hide History' : 'View History' }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- Ranking history section -->
    <div v-if="showHistory" 
         class="bg-white rounded-xl shadow-md overflow-hidden transition-all duration-300 transform"
         :class="{'opacity-100 translate-y-0': showHistory, 'opacity-0 -translate-y-4': !showHistory}">
      <div class="px-6 py-4 bg-gradient-to-r from-blue-50 to-indigo-50 border-b border-blue-100">
        <h3 class="text-lg font-semibold text-gray-800">Rankings Timeline</h3>
        <p class="text-sm text-gray-600">See how topics have changed over the past hour</p>
      </div>
      <div class="max-h-96 overflow-y-auto p-4">
        <div v-for="ranking in rankingHistory" :key="ranking.id" 
             class="mb-3 bg-white border border-gray-100 rounded-lg shadow-sm overflow-hidden">
          <div class="p-3 bg-gray-50 border-b border-gray-100 flex justify-between items-center">
            <div class="flex items-center gap-2">
              <span class="w-6 h-6 flex items-center justify-center rounded-full bg-blue-100 text-blue-700 text-xs font-bold">#{{ ranking.id }}</span>
              <span class="font-medium text-gray-800">{{ formatTime(ranking.created_at) }}</span>
            </div>
          </div>
          <div v-if="getTopicChanges(ranking)" class="p-3 text-sm">
            <div class="flex gap-2 items-start text-gray-700">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-blue-500 flex-shrink-0 mt-0.5" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
              </svg>
              <span>{{ getTopicChanges(ranking) }}</span>
            </div>
          </div>
          <div v-else class="px-3 py-2 text-sm text-gray-500 italic">
            No changes detected
          </div>
        </div>
      </div>
    </div>
    
    <!-- Error message -->
    <div v-if="error" 
         class="bg-red-50 border-l-4 border-red-500 p-4 rounded-md flex items-start gap-3 shadow-sm">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-red-500 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
      </svg>
      <span class="text-red-800">{{ error }}</span>
    </div>
    
    <div v-else>
      <!-- Section title -->
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-xl font-bold text-gray-800 flex items-center">
          <span class="mr-2">Trending Topics</span>
          <span class="bg-blue-100 text-blue-800 text-xs px-2 py-0.5 rounded-full">{{ topics.length }}</span>
        </h2>
        
        <div class="flex gap-3">
          <button @click="viewMode = 'list'" 
                  :class="['p-1.5 rounded-md transition-colors', 
                          viewMode === 'list' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600 hover:bg-gray-200']">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <button @click="viewMode = 'grid'" 
                  :class="['p-1.5 rounded-md transition-colors', 
                          viewMode === 'grid' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600 hover:bg-gray-200']">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
            </svg>
          </button>
        </div>
      </div>
      
      <!-- List View (Horizontal Layout) -->
      <div v-if="viewMode === 'list'" class="space-y-4">
        <!-- Top trending topic - featured section -->
        <div v-if="topics.length > 0" 
              class="relative group bg-white rounded-xl shadow-md overflow-hidden border border-gray-100">
          <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 to-blue-500"></div>
          <div class="p-6">
            <div class="flex justify-between items-start">
              <div>
                <div class="flex items-center mb-3">
                  <span class="bg-red-100 text-red-800 text-xs font-bold px-2 py-1 rounded-full">Top Story</span>
                  <span v-if="newTopics.includes(topics[0].id)" 
                      class="ml-2 bg-blue-500 text-white text-xs px-2 py-0.5 rounded-full font-medium">
                    New
                  </span>
                </div>
                <h3 class="text-xl font-semibold text-gray-900 mb-2">{{ topics[0].name }}</h3>
                <div class="text-sm text-gray-600">This topic is trending across multiple sources</div>
              </div>
              <router-link :to="{ path: '/topic/' + topics[0].id, query: { name: topics[0].name } }" 
                          class="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white px-4 py-2 rounded-md font-medium text-sm transition-all flex items-center gap-1 shadow-sm hover:shadow">
                <span>View</span>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </router-link>
            </div>
          </div>
        </div>
        
        <!-- Horizontal list for remaining topics -->
        <div class="bg-white rounded-xl shadow-md border border-gray-100 overflow-hidden">
          <div class="px-6 py-4 bg-gradient-to-r from-gray-50 to-gray-100 border-b border-gray-200">
            <h3 class="font-medium text-gray-700">Other Trending Topics</h3>
          </div>
          
          <ul class="divide-y divide-gray-100">
            <li v-for="(topic, index) in topics.slice(1)" :key="topic.id" 
                class="group hover:bg-gray-50 transition-colors">
              <div class="flex items-center justify-between p-4 sm:px-6">
                <div class="flex items-center gap-4">
                  <!-- Rank indicator -->
                  <div class="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold"
                      :class="getRankIndicatorClass(index + 1)">
                    #{{ index + 2 }}
                  </div>
                  
                  <!-- Topic info -->
                  <div>
                    <div class="flex items-center gap-2">
                      <h4 class="font-medium text-gray-900">{{ topic.name }}</h4>
                      <span v-if="newTopics.includes(topic.id)" 
                          class="bg-blue-500 text-white text-xs px-2 py-0.5 rounded-full font-medium">
                        New
                      </span>
                    </div>
                    <div class="text-xs text-gray-500 mt-0.5">
                      {{ getTopicCategory(index + 1) }}
                    </div>
                  </div>
                </div>
                
                <!-- Action button -->
                <router-link :to="{ path: '/topic/' + topic.id, query: { name: topic.name } }" 
                           class="flex items-center gap-1 text-sm font-medium text-blue-600 hover:text-blue-800 transition-colors"
                           style="min-width: 120px; white-space: nowrap;">
                  <span class="hidden sm:inline">View Details</span>
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                </router-link>
              </div>
            </li>
          </ul>
          
          <!-- Empty state within list -->
          <div v-if="topics.length <= 1" class="flex flex-col items-center justify-center py-8 text-gray-500">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-gray-300 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z" />
            </svg>
            <p class="text-gray-600 font-medium">No additional topics available</p>
          </div>
        </div>
      </div>
      
      <!-- Grid View (Original Card Layout) -->
      <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="(topic, index) in topics" :key="topic.id" 
            :class="['relative bg-white rounded-xl border overflow-hidden transition-all duration-300 hover:shadow-md transform hover:-translate-y-1 group', 
                    getTopicCategoryStyle(index).borderClass,
                    newTopics.includes(topic.id) ? 'ring-2 ring-blue-400 ring-opacity-70' : '']">
          
          <!-- Category indicator -->
          <div :class="['absolute top-0 left-0 h-full w-1', getTopicCategoryStyle(index).bgClass]"></div>
          
          <!-- Category badge -->
          <div :class="['absolute top-3 right-3 px-2 py-0.5 rounded-full text-xs font-medium', 
                      getTopicCategoryStyle(index).badgeClass]">
            {{ getTopicCategory(index) }}
          </div>
          
          <!-- New badge -->
          <div v-if="newTopics.includes(topic.id)" 
               class="absolute top-3 left-3 bg-blue-500 text-white text-xs px-2 py-0.5 rounded-full font-medium z-10">
            New
          </div>
          
          <router-link :to="{ path: '/topic/' + topic.id, query: { name: topic.name } }" 
                      class="block p-5 pl-6 h-full no-underline">
            
            <!-- Rank indicator -->
            <div class="absolute bottom-3 right-3 w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center text-xs text-gray-600 font-bold group-hover:bg-gray-200 transition-colors">
              #{{ index + 1 }}
            </div>
            
            <h3 class="text-lg font-medium text-gray-900 mb-2 pr-10">{{ topic.name }}</h3>
            <div class="text-sm text-gray-500 flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              View insights
            </div>
          </router-link>
        </div>
      </div>
      
      <!-- Empty state (no topics at all) -->
      <div v-if="topics.length === 0 && !error" class="flex flex-col items-center justify-center py-16 bg-gray-50 rounded-xl">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-gray-400 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 16l2.879-2.879m0 0a3 3 0 104.243-4.242 3 3 0 00-4.243 4.242zM21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <h3 class="text-gray-600 font-medium">No trending topics found</h3>
        <p class="text-gray-500 text-sm mt-1">Check back soon for new content</p>
      </div>
    </div>
    
    <!-- Footer -->
    <div class="border-t border-gray-200 pt-4 mt-8">
      <p class="text-center text-sm text-gray-500">
        Data updates automatically every few minutes. Last check: {{ lastUpdateTime }}
      </p>
    </div>
  </div>
</template>

<script setup>
import axios from 'axios';
import { ref, reactive, onMounted, onBeforeUnmount, watch, computed } from 'vue';

// Data
const topics = ref([]);
const previousTopics = ref([]);
const error = ref(null);
const lastUpdateTime = ref('Never');
const isUpdating = ref(false);
const newTopics = ref([]);
const previousTopicIds = ref(new Set());
const currentRankingId = ref(null);
const rankingHistory = ref([]);
const showHistory = ref(false);
const initialLoad = ref(true);
const viewMode = ref(localStorage.getItem('topicsViewMode') || 'list');

const categoryStyles = reactive([
  { borderClass: 'border-red-200', badgeClass: 'bg-red-100 text-red-800', bgClass: 'bg-red-500' },
  { borderClass: 'border-orange-200', badgeClass: 'bg-orange-100 text-orange-800', bgClass: 'bg-orange-500' },
  { borderClass: 'border-amber-200', badgeClass: 'bg-amber-100 text-amber-800', bgClass: 'bg-amber-500' },
  { borderClass: 'border-blue-200', badgeClass: 'bg-blue-100 text-blue-800', bgClass: 'bg-blue-500' },
  { borderClass: 'border-indigo-200', badgeClass: 'bg-indigo-100 text-indigo-800', bgClass: 'bg-indigo-500' },
  { borderClass: 'border-purple-200', badgeClass: 'bg-purple-100 text-purple-800', bgClass: 'bg-purple-500' },
  { borderClass: 'border-gray-200', badgeClass: 'bg-gray-100 text-gray-800', bgClass: 'bg-gray-500' }
]);

// Computed properties
const topicsLength = computed(() => topics.value.length);

// Helper functions
const getTopicCategory = (index) => {
  if (index === 0) return 'Top Story';
  if (index < 3) return 'Trending';
  if (index < 6) return 'Popular';
  return 'Rising';
};

const getTopicCategoryStyle = (index) => {
  return categoryStyles[Math.min(index, categoryStyles.length - 1)];
};

const getRankIndicatorClass = (index) => {
  if (index === 1) return 'bg-red-100 text-red-800';
  if (index === 2) return 'bg-orange-100 text-orange-800';
  if (index === 3) return 'bg-amber-100 text-amber-800';
  return 'bg-gray-100 text-gray-700';
};

const formatTime = (isoString) => {
  const utcDate = new Date(isoString + 'Z');
  return utcDate.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: true,
    timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone
  });
};

const getTopicChanges = (ranking) => {
  if (rankingHistory.value.length < 2) return null;
  const currentIndex = rankingHistory.value.findIndex(r => r.id === ranking.id);
  if (currentIndex === rankingHistory.value.length - 1) return null;

  const nextRanking = rankingHistory.value[currentIndex + 1];
  const currentTopicIds = new Set(ranking.topics.map(t => t.id));
  const nextTopicIds = new Set(nextRanking.topics.map(t => t.id));

  const added = ranking.topics.filter(t => !nextTopicIds.has(t.id));
  const removed = nextRanking.topics.filter(t => !currentTopicIds.has(t.id));

  if (added.length === 0 && removed.length === 0) return null;

  let changes = [];
  if (added.length > 0) changes.push(`Added: ${added.map(t => t.name).join(', ')}`);
  if (removed.length > 0) changes.push(`Removed: ${removed.map(t => t.name).join(', ')}`);

  return changes.join(' | ');
};

// API calls
const fetchTopics = async () => {
  isUpdating.value = true;
  try {
    if (!initialLoad.value) {
      await new Promise(resolve => setTimeout(resolve, 500));
    }

    const response = await axios.get('http://localhost:5000/topics');
    console.log("API Response:", response.data);

    currentRankingId.value = response.data.ranking_id;
    const currentTopics = response.data.topics;

    loadPreviousTopicIds();

    const currentTopicIds = new Set(currentTopics.map(topic => topic.id));
    newTopics.value = currentTopics
      .filter(topic => !previousTopicIds.value.has(topic.id))
      .map(topic => topic.id);

    currentTopics.forEach(topic => {
      previousTopicIds.value.add(topic.id);
    });
    savePreviousTopicIds();

    const shouldUpdateTopics = initialLoad.value || hasTopicsChanged(currentTopics, topics.value);

    if (shouldUpdateTopics) {
      previousTopics.value = [...topics.value];
      topics.value = currentTopics;
      lastUpdateTime.value = new Date().toLocaleTimeString();
    }

    error.value = null;
    initialLoad.value = false;

    setTimeout(() => {
      newTopics.value = [];
    }, 3000);
  } catch (err) {
    console.error('Error fetching topics:', err);
    error.value = 'Failed to load topics. Please refresh the page.';
  } finally {
    setTimeout(() => {
      isUpdating.value = false;
    }, 500);
  }
};

const fetchRankingHistory = async () => {
  try {
    const response = await axios.get('http://localhost:5000/rankings/history');
    rankingHistory.value = response.data;
  } catch (err) {
    console.error('Error fetching ranking history:', err);
  }
};

// Local storage functions
const savePreviousTopicIds = () => {
  try {
    localStorage.setItem('previousTopicIds', JSON.stringify([...previousTopicIds.value]));
  } catch (e) {
    console.error('Error saving to localStorage:', e);
  }
};

const loadPreviousTopicIds = () => {
  try {
    const savedIds = localStorage.getItem('previousTopicIds');
    if (savedIds) {
      previousTopicIds.value = new Set(JSON.parse(savedIds));
    }
  } catch (e) {
    console.error('Error loading from localStorage:', e);
    previousTopicIds.value = new Set();
  }
};

// Comparison function
const hasTopicsChanged = (newTopicsList, oldTopicsList) => {
  if (newTopicsList.length !== oldTopicsList.length) {
    return true;
  }

  const oldTopicMap = new Map(oldTopicsList.map(topic => [topic.id, topic]));

  for (const newTopic of newTopicsList) {
    const oldTopic = oldTopicMap.get(newTopic.id);
    if (!oldTopic || oldTopic.name !== newTopic.name) {
      return true;
    }
  }
  return false;
};

// Toggle ranking history
const toggleRankingHistory = () => {
  showHistory.value = !showHistory.value;
  if (showHistory.value) {
    fetchRankingHistory();
  }
};

// Lifecycle hooks
onMounted(() => {
  loadPreviousTopicIds();
  fetchTopics();
  const pollInterval = setInterval(fetchTopics, 500000);
  const historyPollInterval = setInterval(() => {
    if (showHistory.value) {
      fetchRankingHistory();
    }
  }, 30000);

  onBeforeUnmount(() => {
    clearInterval(pollInterval);
    clearInterval(historyPollInterval);
    savePreviousTopicIds();
  });
});

// Watchers
watch(viewMode, (newMode) => {
  try {
    localStorage.setItem('topicsViewMode', newMode);
  } catch (e) {
    console.error('Error saving view mode preference:', e);
  }
});
</script>