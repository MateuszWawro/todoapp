import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../composables/useApi'

export const useHealthStore = defineStore('health', () => {
  const summary = ref(null)
  const metrics = ref([])
  const loading = ref(false)

  async function fetchSummary() {
    loading.value = true
    try {
      const { data } = await api.get('/health/summary')
      summary.value = data
    } finally {
      loading.value = false
    }
  }

  async function fetchMetrics(type, days = 14) {
    const { data } = await api.get('/health/metrics', { params: { type, days } })
    metrics.value = data
    return data
  }

  // Pomocnik: dane na dziś dla danego type
  function todayValue(type) {
    return summary.value?.today?.find(m => m.type === type)?.value ?? null
  }

  // Pomocnik: 7 dni dla danego type → tablica wartości
  function weekValues(type) {
    return summary.value?.week
      ?.filter(m => m.type === type)
      ?.map(m => parseFloat(m.value)) ?? []
  }

  return { summary, metrics, loading, fetchSummary, fetchMetrics, todayValue, weekValues }
})
