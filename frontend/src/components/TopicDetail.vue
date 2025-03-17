<template>
  <div class="max-w-5xl mx-auto p-6">
    <!-- Loading state -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-16">
      <div class="w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mb-4"></div>
      <p class="text-gray-600 font-medium">Loading topic insights...</p>
    </div>
    
    <div v-else class="space-y-8">
      <!-- Hero section with backdrop gradient -->
      <div class="relative bg-gradient-to-br from-blue-50 via-white to-indigo-50 rounded-2xl p-6 shadow-sm">
        <div class="absolute right-0 top-0 w-64 h-64 bg-gradient-to-bl from-blue-100 to-purple-100 rounded-full filter blur-3xl opacity-70 -mr-20 -mt-20"></div>
        <!-- <div class="absolute left-0 bottom-0 w-40 h-40 bg-gradient-to-tr from-blue-200 to-indigo-100 rounded-full filter blur-2xl opacity-70 -ml-10 -mb-10"></div> -->
        
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
        <div class="relative overflow-visible">
          <div class="flex flex-wrap gap-2 mt-4">
            <div 
              v-for="([domain, refs]) in Object.entries(references.reduce((acc, ref) => {
                let d = ref.url.split('/')[2];
                acc[d] = acc[d] ? acc[d].concat(ref) : [ref];
                return acc;
              }, {}))" 
              :key="domain" 
              class="relative">
              <button 
                @click="openDomain = openDomain === domain ? '' : domain"
                class="bg-white text-gray-800 px-3 py-1 rounded-full border border-gray-300 hover:bg-gray-100 transition">
                {{ domain }} {{ refs.length > 1 ? '(' + refs.length + ')' : '' }}
              </button>
              <div 
                v-if="openDomain === domain" 
                class="absolute left-0 mt-2 w-64 bg-white rounded-xl shadow-lg z-50 transition-transform transform origin-top scale-95">
                <div 
                  v-for="ref in refs" 
                  :key="ref.id" 
                  class="px-4 py-2 hover:bg-gray-50 break-all">
                  <a :href="ref.url" target="_blank" class="text-blue-600 hover:underline">
                    {{ ref.title }}
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      
      <div class="bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden">
        <div class="px-6 py-4 bg-gradient-to-r from-gray-50 to-slate-100 border-b border-gray-200 flex justify-between items-center cursor-pointer" @click="toggleSection('insights')">
          <h2 class="text-xl font-semibold text-gray-800">Insights</h2>
          <div class="flex items-center">
            <div class="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
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
        <div v-if="openSections.insights" class="p-6 grid grid-cols-1 lg:grid-cols-1 gap-8">
        <!-- Summary Insight -->
        <div v-if="latestSummary" class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-5 border border-blue-100">
          <div class="flex gap-4 cursor-pointer" @click="toggleSection('insights_summary')">
            <div class="flex-shrink-0">
              <div class="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center shadow-sm">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
            <div class="flex items-center">
              <h2 class="text-xl font-semibold text-gray-800 justify-center">Summary</h2>
              <svg v-if="openSections.insights_summary" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 ml-2 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
              </svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 ml-2 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </div>

          <div v-if="openSections.insights_summary" class="p-6">
            <!-- Render the highlighted summary -->
            <div class="leading-relaxed" v-html="highlightedSummary"></div>
          </div>
        </div>


          <div v-else class="flex flex-col items-center justify-center py-10 text-gray-500 bg-gray-50 rounded-lg">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-gray-400 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            <p class="font-medium">No summary insights available for this topic yet.</p>
            <p class="text-sm mt-1">Our system is continuously analyzing new data.</p>
          </div>

          <!-- Personal Insight -->
          <div v-if="latestPersonal" class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-5 border border-blue-100">
            <div class="flex gap-4 cursor-pointer" @click="toggleSection('insights_personal')">
              <div class="flex-shrink-0">
                <div class="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center shadow-sm">
                  <svg class="h-7 w-7 text-blue-600" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                      <!-- <circle cx="12" cy="7" r="5"/>  
                      <path d="M4 22c0-5 4-9 8-9s8 4 8 9" />
                   -->
                  <path xmlns="http://www.w3.org/2000/svg" d="M12.0224 13.9993C11.3753 15.0098 11.0001 16.2111 11.0001 17.5C11.0001 19.1303 11.6003 20.6205 12.5919 21.7615C11.7963 21.9216 10.9314 22.0011 10.0001 22.0011C6.57915 22.0011 4.05619 20.9289 2.51403 18.7646C2.18207 18.2987 2.00366 17.7409 2.00366 17.1688V16.2488C2.00366 15.0068 3.01052 13.9999 4.25254 13.9999L12.0224 13.9993ZM17.5001 12C20.5377 12 23.0001 14.4624 23.0001 17.5C23.0001 20.5376 20.5377 23 17.5001 23C14.4626 23 12.0001 20.5376 12.0001 17.5C12.0001 14.4624 14.4626 12 17.5001 12ZM17.5001 19.751C17.1552 19.751 16.8756 20.0306 16.8756 20.3755C16.8756 20.7204 17.1552 21 17.5001 21C17.845 21 18.1246 20.7204 18.1246 20.3755C18.1246 20.0306 17.845 19.751 17.5001 19.751ZM17.5002 13.8741C16.4522 13.8741 15.6359 14.6915 15.6468 15.8284C15.6494 16.1045 15.8754 16.3262 16.1516 16.3236C16.4277 16.3209 16.6494 16.0949 16.6467 15.8188C16.6412 15.2398 17.0064 14.8741 17.5002 14.8741C17.9725 14.8741 18.3536 15.266 18.3536 15.8236C18.3536 16.0158 18.2983 16.1659 18.1296 16.3851L18.0356 16.501L17.9366 16.6142L17.6712 16.9043L17.5348 17.0615C17.1515 17.5182 17.0002 17.854 17.0002 18.3716C17.0002 18.6477 17.224 18.8716 17.5002 18.8716C17.7763 18.8716 18.0002 18.6477 18.0002 18.3716C18.0002 18.1684 18.0587 18.0126 18.239 17.7813L18.3239 17.6772L18.4249 17.5618L18.6906 17.2713L18.8252 17.1162C19.2035 16.6654 19.3536 16.333 19.3536 15.8236C19.3536 14.7199 18.5312 13.8741 17.5002 13.8741ZM10.0001 2.00464C12.7615 2.00464 15.0001 4.24321 15.0001 7.00464C15.0001 9.76606 12.7615 12.0046 10.0001 12.0046C7.2387 12.0046 5.00012 9.76606 5.00012 7.00464C5.00012 4.24321 7.2387 2.00464 10.0001 2.00464Z"/>
                </svg>
                </div>
              </div>
              <div class="flex items-center">
                <h2 class="text-xl font-semibold text-gray-800 justify-center">How this may affect you</h2>
                  <svg v-if="openSections.insights_personal" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 ml-2 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
                  </svg>
                  <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 ml-2 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                  </svg>
              </div>
            </div>

            <div v-if="openSections.insights_personal" class="p-6">
              <div class="leading-relaxed">{{ latestPersonal.content }}</div>
            </div>
          </div>
          <div v-else class="flex flex-col items-center justify-center py-10 text-gray-500 bg-gray-50 rounded-lg">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-gray-400 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            <p class="font-medium">No personal insights available for this topic yet.</p>
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
      topic: null,
      insights: [],
      socialPosts: [],
      references: [],
      sentimentData: null,
      loading: true,
      sentimentColors: {
        'Positive': '#4CAF50',
        'Negative': '#F44336',
        'Neutral': '#9E9E9E'
      },
      emotionColors: {
        'Joy': '#FFEB3B',
        'Anger': '#F44336',
        'Sadness': '#3F51B5',
        'Fear': '#673AB7',
        'Surprise': '#00BCD4'
      },
      openSections: {
        insights: true,
        sentiment: true,
        socialMedia: true,
        references: true,
        insights_summary: true,
        insights_personal: true
      },
      openDomain: "",
      summaryKeyphrases: []  // stores the keyphrases for the summary text
    };
  },
  computed: {
    latestSummary() {
      const summaries = this.insights.filter(i => i.type === 'summary');
      return summaries.length ? summaries[summaries.length - 1] : null;
    },
    latestPersonal() {
      const personalInsights = this.insights.filter(i => i.type === 'personal');
      return personalInsights.length ? personalInsights[personalInsights.length - 1] : null;
    },
    filteredSentiments() {
      if (!this.sentimentData || !this.sentimentData.sentiments) return {};
      const result = {};
      Object.entries(this.sentimentData.sentiments).forEach(([sentiment, value]) => {
        if (value > 0) {
          result[sentiment] = value;
        }
      });
      return result;
    },
    filteredEmotions() {
      if (!this.sentimentData || !this.sentimentData.emotions) return {};
      const result = {};
      Object.entries(this.sentimentData.emotions).forEach(([emotion, value]) => {
        if (value > 0) {
          result[emotion] = value;
        }
      });
      return result;
    },
    highlightedSummary() {
        let summaryText = this.latestSummary && this.latestSummary.content ? this.latestSummary.content : '';
        // Wrap all keyphrases in a span with Tailwind utility classes.
        this.summaryKeyphrases.forEach(phrase => {
          const regex = new RegExp(`(${this.escapeRegExp(phrase)})`, 'gi');
          summaryText = summaryText.replace(regex, '<span class="bg-blue-200 px-1 rounded">$1</span>');
        });
        return summaryText;
    }
  },
  methods: {
    formatPostTime(timestamp) {
      const date = new Date(timestamp);
      return date.toLocaleString('en-US', { 
        month: 'short', 
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit'
      });
    },
    getSentimentTextColor(sentiment) {
      switch(sentiment) {
        case 'Positive': return 'text-green-700';
        case 'Negative': return 'text-red-700';
        case 'Neutral': return 'text-gray-700';
        default: return 'text-gray-700';
      }
    },
    getSentimentDotColor(sentiment) {
      switch(sentiment) {
        case 'Positive': return 'bg-green-500';
        case 'Negative': return 'bg-red-500';
        case 'Neutral': return 'bg-gray-500';
        default: return 'bg-gray-500';
      }
    },
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
    escapeRegExp(string) {
      return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }
  },
  watch: {
    latestSummary(newSummary) {
      if (newSummary && newSummary.content) {
        // Fetch keyphrases for the summary text.
        const encodedText = encodeURIComponent(newSummary.content);
        axios.get(`http://localhost:5000/keyphrases/${encodedText}`)
          .then(response => {
            this.summaryKeyphrases = response.data;
          })
          .catch(error => {
            console.error('Error fetching keyphrases:', error);
          });
      }
    }
  },
  created() {
    const topicId = this.$route.params.id;
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
    axios.get(`http://localhost:5000/topics/${topicId}/social`)
      .then(response => {
        this.socialPosts = response.data;
      })
      .catch(error => {
        console.error('Error fetching social media posts:', error);
      });
    axios.get(`http://localhost:5000/topics/${topicId}/references`)
      .then(response => {
        this.references = response.data;
        console.error(response.data);
      })
      .catch(error => {
        console.error('Error fetching references:', error);
      });
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
.highlight {
  background-color: #fffd54;
  padding: 0 2px;
  border-radius: 2px;
}
</style>