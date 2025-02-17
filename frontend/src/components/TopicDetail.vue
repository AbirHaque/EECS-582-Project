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
      loading: true // Controls loading state visibility
    };
  },
  computed: {
    // Computed property that returns the most recent summary insight
    latestSummary() {
      const summaries = this.insights.filter(i => i.type === 'summary');
      return summaries.length ? summaries[summaries.length - 1] : null;
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
        this.loading = false;
      })
      .catch(error => {
        console.error('Error fetching topic details:', error);
        this.loading = false;
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
</style>