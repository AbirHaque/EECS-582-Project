<template>
  <div v-if="insightData" class="space-y-8">
    <!-- Header Section -->
    <div class="relative bg-gradient-to-br from-gray-50 via-white to-gray-100 rounded-lg p-4 shadow-sm border">
      <h1 class="text-2xl font-bold text-gray-800 mb-1">{{ insightData.topicName || 'Saved Insight' }}</h1>
      <p class="text-sm text-gray-500">Topic ID: {{ insightData.topicId }}</p>
      <p class="text-sm text-gray-500">Originally Created: {{ formatTimestamp(insightData.topicCreatedAt) }}</p>
      <p class="text-sm text-gray-500">Saved: {{ formatTimestamp(insightData.savedAt) }}</p>
    </div>

    <!-- Insights Section -->
    <div class="bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden">
      <div class="px-6 py-4 bg-gradient-to-r from-gray-50 to-slate-100 border-b border-gray-200">
        <h2 class="text-xl font-semibold text-gray-800">Insights</h2>
      </div>
      <div class="p-6 grid grid-cols-1 gap-6">
        <!-- Summary -->
        <div v-if="latestSummary" class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4 border border-blue-100">
          <h3 class="text-lg font-semibold text-gray-800 mb-2">Summary</h3>
          <div class="leading-relaxed text-gray-700">{{ latestSummary.content }}</div>
        </div>

        <!-- Personal -->
        <div v-if="latestPersonal" class="bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg p-4 border border-green-100">
          <h3 class="text-lg font-semibold text-gray-800 mb-2">How this may affect you</h3>
          <div class="leading-relaxed text-gray-700">{{ latestPersonal.content }}</div>
        </div>

        <!-- Background -->
        <div v-if="latestBackground" class="bg-gradient-to-r from-yellow-50 to-orange-50 rounded-lg p-4 border border-yellow-100">
          <h3 class="text-lg font-semibold text-gray-800 mb-2">Background Information</h3>
          <div class="leading-relaxed text-gray-700">{{ latestBackground.content }}</div>
        </div>

        <!-- Hashtags -->
        <div v-if="latestHashtags" class="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-4 border border-purple-100">
          <h3 class="text-lg font-semibold text-gray-800 mb-2">Popular Hashtags</h3>
          <div class="leading-relaxed text-gray-700 whitespace-pre-wrap">{{ latestHashtags.content }}</div>
        </div>

        <!-- Multimedia -->
        <div v-if="latestMultimedia" class="bg-gradient-to-r from-cyan-50 to-sky-50 rounded-lg p-4 border border-cyan-100">
          <h3 class="text-lg font-semibold text-gray-800 mb-2">Multimedia</h3>
           <img
              v-if="isImageUrl(latestMultimedia.content)"
              :src="latestMultimedia.content"
              alt="Multimedia content"
              class="max-w-full h-auto rounded mt-2"
            />
          <div v-else class="leading-relaxed text-gray-700">{{ latestMultimedia.content }}</div>
        </div>

         <!-- Multimedia Location (Basic display for now) -->
        <div v-if="latestMultimediaLocation" class="bg-gradient-to-r from-teal-50 to-lime-50 rounded-lg p-4 border border-teal-100">
          <h3 class="text-lg font-semibold text-gray-800 mb-2">Location Multimedia</h3>
          <div class="leading-relaxed text-gray-700 text-sm">
            Location data available (Map view not implemented in saved viewer). Content: {{ latestMultimediaLocation.content }}
          </div>
        </div>

      </div>
    </div>

    <!-- Source Diversity -->
    <div v-if="diversityData" class="bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden">
       <div class="px-6 py-4 bg-gradient-to-r from-green-50 to-emerald-50 border-b border-gray-200">
          <h2 class="text-xl font-semibold text-gray-800">Source Diversity Score</h2>
       </div>
       <div class="p-6">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <!-- Score -->
            <div class="bg-white rounded-lg shadow-sm border border-gray-100 p-6 flex flex-col items-center justify-center col-span-1">
              <div class="text-6xl font-bold" :class="diversityScoreColor">{{ diversityData.score }}</div>
              <div class="mt-2 text-gray-600 text-sm">Diversity Score</div>
              <div class="w-full bg-gray-200 rounded-full h-2.5 mt-4">
                <div class="h-2.5 rounded-full" :style="{ width: diversityData.score + '%' }" :class="diversityScoreBg"></div>
              </div>
              <div class="text-xs text-gray-500 mt-2 text-center">{{ diversityScoreText }}</div>
            </div>
            <!-- Metrics -->
            <div class="bg-white rounded-lg shadow-sm border border-gray-100 p-4 col-span-2">
              <h3 class="text-lg font-semibold text-gray-800 mb-4">Source Metrics</h3>
              <div class="grid grid-cols-2 gap-4">
                <div class="border rounded p-3 bg-gray-50"><div class="text-sm text-gray-500">Unique Sources</div><div class="text-xl font-semibold">{{ diversityData.metrics.domain_count }}</div></div>
                <div class="border rounded p-3 bg-gray-50"><div class="text-sm text-gray-500">Total Articles</div><div class="text-xl font-semibold">{{ diversityData.metrics.total_articles }}</div></div>
                <div class="border rounded p-3 bg-gray-50"><div class="text-sm text-gray-500">Distribution</div><div class="text-xl font-semibold">{{ Math.round(diversityData.metrics.domain_distribution * 100) }}%</div></div>
                <div class="border rounded p-3 bg-gray-50"><div class="text-sm text-gray-500">Content Diversity</div><div class="text-xl font-semibold">{{ Math.round(diversityData.metrics.content_diversity * 100) }}%</div></div>
              </div>
            </div>
            <!-- Breakdown -->
            <div class="bg-white rounded-lg shadow-sm border border-gray-100 p-4 col-span-3">
              <h3 class="text-lg font-semibold text-gray-800 mb-4">Source Breakdown</h3>
              <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                <div v-for="domain in diversityData.domains" :key="domain.domain" class="border rounded p-3 flex justify-between items-center">
                  <div class="font-medium text-gray-800 truncate" :title="domain.domain">{{ domain.domain }}</div>
                  <div class="bg-gray-200 rounded-full px-2 py-1 text-xs font-medium">{{ domain.count }}</div>
                </div>
              </div>
            </div>
          </div>
       </div>
    </div>

    <!-- Sentiment Analysis -->
    <div v-if="sentimentData" class="bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden">
        <div class="px-6 py-4 bg-gradient-to-r from-purple-50 to-indigo-50 border-b border-gray-200">
          <h2 class="text-xl font-semibold text-gray-800">Public Sentiment Analysis</h2>
        </div>
        <div class="p-6 grid grid-cols-1 lg:grid-cols-2 gap-8">
          <!-- Sentiment chart -->
          <div v-if="sentimentData.sentiments" class="bg-white rounded-lg shadow-sm border border-gray-100 p-4">
            <h3 class="text-lg font-semibold text-gray-800 mb-4">Overall Sentiment</h3>
            <div class="space-y-4">
              <div v-for="(value, sentiment) in filteredSentiments" :key="sentiment" class="relative">
                <div class="flex justify-between mb-2">
                  <span class="font-semibold text-gray-700 flex items-center">
                    <div :class="['w-3 h-3 rounded-full mr-2', getSentimentDotColor(sentiment)]"></div>{{ sentiment }}
                  </span>
                  <span class="font-semibold" :class="getSentimentTextColor(sentiment)">{{ value }}%</span>
                </div>
                <div class="h-3 w-full bg-gray-200 rounded-full overflow-hidden">
                  <div class="h-full rounded-full" :style="{ width: value + '%', backgroundColor: sentimentColors[sentiment] || '#9E9E9E' }"></div>
                </div>
              </div>
            </div>
          </div>
          <!-- Emotions chart -->
          <div v-if="sentimentData.emotions" class="bg-white rounded-lg shadow-sm border border-gray-100 p-4">
            <h3 class="text-lg font-semibold text-gray-800 mb-4">Emotional Tone</h3>
            <div class="space-y-4">
              <div v-for="(value, emotion) in filteredEmotions" :key="emotion" class="relative">
                <div class="flex justify-between mb-2">
                  <span class="font-semibold text-gray-700 flex items-center">
                     <div :class="['w-3 h-3 rounded-full mr-2', getEmotionDotColor(emotion)]"></div>{{ emotion }}
                  </span>
                  <span class="font-semibold" :class="getEmotionTextColor(emotion)">{{ value }}%</span>
                </div>
                <div class="h-3 w-full bg-gray-200 rounded-full overflow-hidden">
                  <div class="h-full rounded-full" :style="{ width: value + '%', backgroundColor: emotionColors[emotion] || '#9E9E9E' }"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
    </div>

    <!-- Social Media Posts -->
    <div v-if="insightData.socialPosts && insightData.socialPosts.length > 0" class="bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden">
        <div class="px-6 py-4 bg-gradient-to-r from-blue-50 to-indigo-50 border-b border-gray-200">
          <h2 class="text-xl font-semibold text-gray-800">Social Media Posts</h2>
        </div>
        <div class="divide-y divide-gray-100 max-h-96 overflow-y-auto">
          <div v-for="(post, index) in insightData.socialPosts" :key="post.id || index" class="p-5 hover:bg-gray-50 transition-colors relative border-l-4" :class="[index % 2 === 0 ? 'border-blue-100' : 'border-indigo-100']">
            <p class="text-gray-800 mb-3 leading-relaxed">{{ post.content }}</p>
            <div class="flex items-center gap-3 text-sm text-gray-500">
              <div class="flex items-center gap-1">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                <span>{{ formatTimestamp(post.created_at) }}</span>
              </div>
              <!-- Add other post metadata if available -->
            </div>
          </div>
        </div>
    </div>

    <!-- References -->
     <div v-if="insightData.references && insightData.references.length > 0" class="bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden">
        <div class="px-6 py-4 bg-gradient-to-r from-gray-50 to-gray-100 border-b border-gray-200">
          <h2 class="text-xl font-semibold text-gray-800">References</h2>
        </div>
        <div class="p-4">
           <div class="flex flex-wrap gap-2">
            <div
              v-for="([domain, refs]) in Object.entries(referencesByDomain)"
              :key="domain"
              class="relative">
              <button
                @click="openDomain = openDomain === domain ? '' : domain"
                class="bg-white text-gray-800 px-3 py-1 rounded-full border border-gray-300 hover:bg-gray-100 transition text-sm">
                {{ domain }} {{ refs.length > 1 ? '(' + refs.length + ')' : '' }}
              </button>
              <div
                v-if="openDomain === domain"
                class="absolute left-0 mt-2 w-64 bg-white rounded-xl shadow-lg z-50 transition-transform transform origin-top scale-95 border">
                <div
                  v-for="ref in refs"
                  :key="ref.id || ref.url"
                  class="px-4 py-2 hover:bg-gray-50 break-all text-sm">
                  <a :href="ref.url" target="_blank" class="text-blue-600 hover:underline">
                    {{ ref.title || ref.url }}
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
     </div>


  </div>
  <div v-else class="p-6 text-center text-gray-500">
    <p>No insight data loaded.</p>
  </div>
</template>

<script setup>
import { ref, computed, defineProps } from 'vue';

const props = defineProps({
  insightData: Object
});

const openDomain = ref('');

// --- Computed properties to extract data ---
const latestSummary = computed(() => props.insightData?.insights?.find(i => i.type === 'summary'));
const latestPersonal = computed(() => props.insightData?.insights?.find(i => i.type === 'personal'));
const latestBackground = computed(() => props.insightData?.insights?.find(i => i.type === 'background'));
const latestHashtags = computed(() => props.insightData?.insights?.find(i => i.type === 'hashtags'));
const latestMultimedia = computed(() => props.insightData?.insights?.find(i => i.type === 'multimedia'));
const latestMultimediaLocation = computed(() => props.insightData?.insights?.find(i => i.type === 'multimedia_location'));

const sentimentData = computed(() => props.insightData?.sentimentData);
const diversityData = computed(() => props.insightData?.diversityData);

const referencesByDomain = computed(() => {
    if (!props.insightData?.references) return {};
    return props.insightData.references.reduce((acc, ref) => {
        try {
            let d = ref.url.split('/')[2];
            acc[d] = acc[d] ? acc[d].concat(ref) : [ref];
        } catch (e) {
            // Handle potential errors if URL is malformed
            console.warn("Could not parse domain from reference URL:", ref.url);
        }
        return acc;
    }, {});
});


// --- Formatting and Styling ---
const formatTimestamp = (timestamp) => {
  if (!timestamp) return 'N/A';
  try {
    return new Date(timestamp).toLocaleString();
  } catch (e) {
    return timestamp; // Return original if parsing fails
  }
};

const isImageUrl = (url) => {
    if (typeof url !== 'string') return false;
    return /\.(jpg|jpeg|png|webp|avif|gif|svg)$/i.test(url);
};


// Sentiment/Emotion Colors (copied from TopicDetail)
const sentimentColors = { 'Positive': '#4CAF50', 'Negative': '#F44336', 'Neutral': '#9E9E9E' };
const emotionColors = { 'Joy': '#FFEB3B', 'Anger': '#F44336', 'Sadness': '#3F51B5', 'Fear': '#673AB7', 'Surprise': '#00BCD4' };

const getSentimentTextColor = (sentiment) => {
  switch(sentiment) {
    case 'Positive': return 'text-green-700';
    case 'Negative': return 'text-red-700';
    default: return 'text-gray-700';
  }
};
const getSentimentDotColor = (sentiment) => {
  switch(sentiment) {
    case 'Positive': return 'bg-green-500';
    case 'Negative': return 'bg-red-500';
    default: return 'bg-gray-500';
  }
};
const getEmotionTextColor = (emotion) => {
  switch(emotion) {
    case 'Joy': return 'text-yellow-700';
    case 'Anger': return 'text-red-700';
    case 'Sadness': return 'text-indigo-700';
    case 'Fear': return 'text-purple-700';
    case 'Surprise': return 'text-cyan-700';
    default: return 'text-gray-700';
  }
};
const getEmotionDotColor = (emotion) => {
  switch(emotion) {
    case 'Joy': return 'bg-yellow-500';
    case 'Anger': return 'bg-red-500';
    case 'Sadness': return 'bg-indigo-500';
    case 'Fear': return 'bg-purple-500';
    case 'Surprise': return 'bg-cyan-500';
    default: return 'bg-gray-500';
  }
};

// Filtered Sentiments/Emotions (copied logic)
const filteredSentiments = computed(() => {
  if (!sentimentData.value?.sentiments) return {};
  return Object.entries(sentimentData.value.sentiments)
    .filter(([, value]) => value > 0)
    .reduce((obj, [key, value]) => { obj[key] = value; return obj; }, {});
});
const filteredEmotions = computed(() => {
  if (!sentimentData.value?.emotions) return {};
  return Object.entries(sentimentData.value.emotions)
    .filter(([, value]) => value > 0)
    .reduce((obj, [key, value]) => { obj[key] = value; return obj; }, {});
});

// Diversity Score Styling (copied logic)
const diversityScoreColor = computed(() => {
    if (!diversityData.value) return 'text-gray-600';
    const score = diversityData.value.score;
    if (score < 33) return 'text-red-600';
    if (score < 66) return 'text-yellow-500';
    return 'text-green-600';
});
const diversityScoreBg = computed(() => {
    if (!diversityData.value) return 'bg-gray-600';
    const score = diversityData.value.score;
    if (score < 33) return 'bg-red-600';
    if (score < 66) return 'bg-yellow-500';
    return 'bg-green-600';
});
const diversityScoreText = computed(() => {
    if (!diversityData.value) return '';
    const score = diversityData.value.score;
    if (score < 33) return 'Low diversity';
    if (score < 66) return 'Moderate diversity';
    return 'High diversity';
});

</script>

<style scoped>
/* Add specific styles if needed */
</style>
