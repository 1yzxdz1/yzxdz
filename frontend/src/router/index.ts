import { createRouter, createWebHistory } from 'vue-router'

import AppLayout from '@/layout/AppLayout.vue'
import AnalysisView from '@/views/AnalysisView.vue'
import AuthView from '@/views/AuthView.vue'
import DashboardView from '@/views/DashboardView.vue'
import MockExamView from '@/views/MockExamView.vue'
import PaperDetailView from '@/views/PaperDetailView.vue'
import PracticeView from '@/views/PracticeView.vue'
import StatisticsView from '@/views/StatisticsView.vue'
import SubjectDetailView from '@/views/SubjectDetailView.vue'
import SubjectsView from '@/views/SubjectsView.vue'
import WrongBookView from '@/views/WrongBookView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: AuthView,
    },
    {
      path: '/',
      component: AppLayout,
      meta: { requiresAuth: true },
      children: [
        { path: '', name: 'dashboard', component: DashboardView },
        { path: 'subjects', name: 'subjects', component: SubjectsView },
        { path: 'subjects/:id', name: 'subject-detail', component: SubjectDetailView, props: true },
        { path: 'papers/:id', name: 'paper-detail', component: PaperDetailView, props: true },
        { path: 'practice', name: 'practice', component: PracticeView },
        { path: 'mock-exam', name: 'mock-exam', component: MockExamView },
        { path: 'analysis', name: 'analysis', component: AnalysisView },
        { path: 'wrong-book', name: 'wrong-book', component: WrongBookView },
        { path: 'statistics', name: 'statistics', component: StatisticsView },
      ],
    },
  ],
})

router.beforeEach((to) => {
  const token = localStorage.getItem('ncre-auth-token')
  if (to.meta.requiresAuth && !token) {
    return '/login'
  }
  if (to.path === '/login' && token) {
    return '/'
  }
  return true
})

export default router
