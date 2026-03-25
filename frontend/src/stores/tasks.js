import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../composables/useApi'

export const useTasksStore = defineStore('tasks', () => {
  const tasks   = ref([])
  const loading = ref(false)
  const activeTimer = ref(null)  // task_id z uruchomionym timerem

  const todo      = computed(() => tasks.value.filter(t => t.status !== 'done'))
  const done      = computed(() => tasks.value.filter(t => t.status === 'done'))
  const totalMins = computed(() => tasks.value.reduce((s, t) => s + (t._elapsed || 0), 0))

  async function fetchTasks(params = {}) {
    loading.value = true
    try {
      const { data } = await api.get('/tasks', { params })
      // Pobierz sesje dla każdego zadania (łączny czas)
      tasks.value = await Promise.all(data.map(async t => {
        const sessions = await fetchSessions(t.id)
        const elapsed  = sessions.reduce((s, sess) => s + (sess.duration_minutes || 0), 0)
        return { ...t, _elapsed: elapsed, _sessions: sessions }
      }))
    } finally {
      loading.value = false
    }
  }

  async function fetchSessions(taskId) {
    const { data } = await api.get(`/tasks/${taskId}/sessions`)
    return data
  }

  async function addTask(title, category, estimatedMinutes = null) {
    const { data } = await api.post('/tasks', { title, category, estimated_minutes: estimatedMinutes })
    tasks.value.unshift({ ...data, _elapsed: 0, _sessions: [] })
    return data
  }

  async function updateTask(id, patch) {
    const { data } = await api.patch(`/tasks/${id}`, patch)
    const idx = tasks.value.findIndex(t => t.id === id)
    if (idx !== -1) tasks.value[idx] = { ...tasks.value[idx], ...data }
    return data
  }

  async function deleteTask(id) {
    await api.delete(`/tasks/${id}`)
    tasks.value = tasks.value.filter(t => t.id !== id)
  }

  async function startTimer(id) {
    await api.post(`/tasks/${id}/sessions`, { action: 'start' })
    activeTimer.value = id
    await updateTask(id, { status: 'in_progress' })
  }

  async function stopTimer(id) {
    const { data } = await api.post(`/tasks/${id}/sessions`, { action: 'stop' })
    activeTimer.value = null
    const idx = tasks.value.findIndex(t => t.id === id)
    if (idx !== -1) tasks.value[idx]._elapsed = data.total_minutes
  }

  return {
    tasks, loading, activeTimer,
    todo, done, totalMins,
    fetchTasks, addTask, updateTask, deleteTask, startTimer, stopTimer,
  }
})
