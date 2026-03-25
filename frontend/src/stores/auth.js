import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../composables/useApi'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token'))
  const user  = ref(null)

  const isLoggedIn = computed(() => !!token.value)

  async function login(username, password) {
    const { data } = await api.post('/auth/login', { username, password })
    token.value = data.token
    localStorage.setItem('token', data.token)
    await fetchMe()
  }

  async function fetchMe() {
    const { data } = await api.get('/auth/me')
    user.value = data
  }

  function logout() {
    token.value = null
    user.value  = null
    localStorage.removeItem('token')
  }

  return { token, user, isLoggedIn, login, logout, fetchMe }
})
