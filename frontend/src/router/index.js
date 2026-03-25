import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/login',        name: 'login',        component: () => import('../views/LoginView.vue'), meta: { public: true } },
  { path: '/',             name: 'overview',     component: () => import('../views/OverviewView.vue') },
  { path: '/sleep',        name: 'sleep',        component: () => import('../views/SleepView.vue') },
  { path: '/tasks',        name: 'tasks',        component: () => import('../views/TasksView.vue') },
  { path: '/correlations', name: 'correlations', component: () => import('../views/CorrelationsView.vue') },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Auth guard
router.beforeEach((to) => {
  const token = localStorage.getItem('token')
  if (!to.meta.public && !token) return '/login'
  if (to.name === 'login' && token) return '/'
})

export default router
