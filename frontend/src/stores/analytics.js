import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../composables/useApi'

export const useAnalyticsStore = defineStore('analytics', () => {
  const correlations = ref([])
  const scatter      = ref([])
  const weekly       = ref(null)
  const loading      = ref(false)

  async function fetchCorrelations(days = 30) {
    loading.value = true
    try {
      const { data } = await api.get('/analytics/correlations', { params: { days } })
      correlations.value = data.correlations
      scatter.value      = data.scatter
    } finally {
      loading.value = false
    }
  }

  async function fetchWeekly() {
    const { data } = await api.get('/analytics/weekly')
    weekly.value = data
  }

  return { correlations, scatter, weekly, loading, fetchCorrelations, fetchWeekly }
})
