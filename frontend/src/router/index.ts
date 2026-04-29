import { createRouter, createWebHistory } from 'vue-router'
import CreatorView from '@/views/CreatorView.vue'
import KnowledgeBaseView from '@/views/KnowledgeBaseView.vue'

const routes = [
  { path: '/', redirect: '/creator' },
  { path: '/creator', name: 'Creator', component: CreatorView },
  { path: '/knowledge', name: 'Knowledge', component: KnowledgeBaseView }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
