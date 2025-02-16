<template>
  <div>
    <h1>Trending News Topics</h1>
    <ul>
      <li v-for="topic in topics" :key="topic.id">
        <router-link :to="'/topic/' + topic.id">{{ topic.name }}</router-link>
      </li>
    </ul>
  </div>
</template>
<script>
import axios from 'axios';
export default {
  name: "HomePage",
  data() {
    return {
      topics: []
    };
  },
  async created() {
    try {
      const response = await axios.get('http://localhost:5000/topics');
      console.log("API Response:", response.data);
      this.topics = response.data;
    } catch (error) {
      console.error('Error fetching topics:', error);
    }
  }
};
</script>
