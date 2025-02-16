<template>
  <div v-if="topic">
    <h1>{{ topic.name }}</h1>
    <router-link to="/">Home</router-link>
  </div>
  <div v-else>
    <p>Loading topic insights...</p>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: "TopicDetail",
  data() {
    return {
      topic: null
    };
  },
  created() {
    const topicId = this.$route.params.id;
    axios.get('http://localhost:5000/topics')
      .then(response => {
        this.topic = response.data.find(t => t.id == topicId);
      })
      .catch(error => {
        console.error('Error fetching topic details:', error);
      });
  }
};
</script>