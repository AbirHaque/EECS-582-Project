import { createRouter, createWebHistory } from 'vue-router';
import HomePage from './components/HomePage.vue';
import TopicDetail from './components/TopicDetail.vue';

const routes = [
  { path: '/', component: HomePage },
  { path: '/topic/:id', component: TopicDetail }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;