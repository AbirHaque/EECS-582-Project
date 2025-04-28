<template>
  <div
    :class="[
      'fixed top-0 right-0 h-full bg-white shadow-lg transition-transform duration-300 ease-in-out z-50 border-l border-gray-200 flex flex-col',
      isOpen ? 'translate-x-0 w-full md:w-1/2 lg:w-2/5' : 'translate-x-full w-0'
    ]"
  >
    <!-- Header -->
    <div class="flex justify-between items-center p-4 border-b border-gray-200 bg-gray-50">
      <h2 class="text-lg font-semibold text-gray-800">Saved Insights</h2>
      <button @click="closeSidebar" class="text-gray-500 hover:text-gray-700">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <!-- Content Area -->
    <div class="flex-grow overflow-y-auto">
      <!-- Insight Selection / Upload -->
      <div v-if="!selectedInsight" class="p-4 space-y-4">
        <div>
          <h3 class="text-md font-medium text-gray-700 mb-2">Load from Browser Storage</h3>
          <ul v-if="savedInsightKeys.length > 0" class="max-h-60 overflow-y-auto border rounded-md divide-y">
            <li v-for="key in savedInsightKeys" :key="key" class="p-2 hover:bg-gray-50 cursor-pointer flex justify-between items-center" @click="loadInsightFromStorage(key)">
              <span class="text-sm text-gray-800 truncate pr-2">{{ getInsightNameFromKey(key) }}</span>
              <button @click.stop="deleteInsight(key)" class="text-red-500 hover:text-red-700 p-1 rounded-full hover:bg-red-100">
                 <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                 </svg>
              </button>
            </li>
          </ul>
          <p v-else class="text-sm text-gray-500 italic">No insights saved in browser storage.</p>
        </div>

        <div class="border-t pt-4">
          <h3 class="text-md font-medium text-gray-700 mb-2">Upload Insight File (.json)</h3>
          <input type="file" @change="handleFileUpload" accept=".json" class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"/>
          <p v-if="uploadError" class="text-red-500 text-sm mt-1">{{ uploadError }}</p>
        </div>
      </div>

      <!-- Insight Viewer -->
      <div v-else class="p-4">
         <button @click="selectedInsight = null" class="mb-4 inline-flex items-center gap-1 text-blue-600 hover:text-blue-800 text-sm font-medium">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to List
         </button>
        <InsightViewer :insightData="selectedInsight" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, defineProps, defineEmits } from 'vue';
import InsightViewer from './InsightViewer.vue'; // Import the viewer component

const props = defineProps({
  isOpen: Boolean
});

const emit = defineEmits(['close']);

const savedInsightKeys = ref([]);
const selectedInsight = ref(null);
const uploadError = ref('');

const closeSidebar = () => {
  emit('close');
};

const loadSavedInsightKeys = () => {
  savedInsightKeys.value = [];
  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    if (key && key.startsWith('savedInsightData_')) {
      savedInsightKeys.value.push(key);
    }
  }
  // Sort keys, maybe by date if possible, or just alphabetically
  savedInsightKeys.value.sort();
};

const getInsightNameFromKey = (key) => {
    try {
        const data = JSON.parse(localStorage.getItem(key));
        const date = new Date(data.savedAt).toLocaleString();
        return `${data.topicName || 'Unnamed Topic'} (Saved: ${date})`;
    } catch (e) {
        return key; // Fallback to key name
    }
};


const loadInsightFromStorage = (key) => {
  try {
    const jsonData = localStorage.getItem(key);
    if (jsonData) {
      selectedInsight.value = JSON.parse(jsonData);
      uploadError.value = '';
    } else {
      uploadError.value = 'Could not load insight from storage.';
    }
  } catch (error) {
    console.error('Error loading insight from storage:', error);
    uploadError.value = 'Failed to parse insight data from storage.';
    selectedInsight.value = null;
  }
};

const handleFileUpload = (event) => {
  const file = event.target.files[0];
  if (!file) return;

  if (file.type !== 'application/json') {
    uploadError.value = 'Please upload a valid .json file.';
    return;
  }

  const reader = new FileReader();
  reader.onload = (e) => {
    try {
      const jsonData = e.target.result;
      selectedInsight.value = JSON.parse(jsonData);
      uploadError.value = '';
    } catch (error) {
      console.error('Error parsing uploaded JSON file:', error);
      uploadError.value = 'Failed to parse the uploaded JSON file.';
      selectedInsight.value = null;
    }
  };
  reader.onerror = () => {
      uploadError.value = 'Error reading the file.';
      selectedInsight.value = null;
  };
  reader.readAsText(file);
};

const deleteInsight = (key) => {
    if (confirm(`Are you sure you want to delete the insight "${getInsightNameFromKey(key)}"?`)) {
        try {
            localStorage.removeItem(key);
            loadSavedInsightKeys(); // Refresh the list
            if (selectedInsight.value && selectedInsight.value.storageKey === key) {
                selectedInsight.value = null; // Clear view if the deleted item was selected
            }
        } catch (error) {
            console.error('Error deleting insight:', error);
            alert('Failed to delete the insight.');
        }
    }
};


onMounted(() => {
  loadSavedInsightKeys();
});
</script>

<style scoped>
/* Add any specific styles for the sidebar if needed */
</style>
