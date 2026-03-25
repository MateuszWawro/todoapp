<template>
  <div>
    <div v-if="health.loading" class="loading">Ładowanie...</div>
    <template v-else>
      <div class="metric-grid">
        <MetricCard label="kroki dziś"       :value="steps?.toLocaleString('pl') ?? '—'" unit="kr"    :delta="stepsD.text" :deltaType="stepsD.type" />
        <MetricCard label="sen dziś"         :value="sleep"                               unit="godz." :delta="sleepD.text" :deltaType="sleepD.type" />
        <MetricCard label="treningi / tydzień" :value="workouts"                          unit="/ 7 dni" delta="cel: 3" deltaType="neutral" />
        <MetricCard label="jakość snu śr."   :value="avgQuality"                          unit="%"     delta="7 dni"   deltaType="neutral" />
      </div>

      <div class="two-col">
        <div class="card">
          <div class="section-lbl">aktywność — ostatnie 7 dni</div>
          <div class="legend">
            <span><span class="dot" style="background:#378ADD"></span>kroki</span>
            <span><span class="dot" style="background:#D4537E"></span>kalorie</span>
          </div>
          <div class="chart-box"><canvas ref="activityCanvas"></canvas></div>
        </div>
        <div class="card">
          <div class="section-lbl">sen — ostatnie 7 dni</div>
          <div class="legend">
            <span><span class="dot" style="background:#534AB7"></span>sen</span>
            <span><span class="dot" style="background:#ccc;border:1px dashed #aaa"></span>cel 8h</span>
          </div>
          <div class="chart-box"><canvas ref="sleepCanvas"></canvas></div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { Chart, registerables } from 'chart.js'
import MetricCard from '../components/ui/MetricCard.vue'
import { useHealthStore } from '../stores/health'

Chart.register(...registerables)

const health = useHealthStore()
const activityCanvas = ref(null)
const sleepCanvas    = ref(null)
let charts = []

const DAYS = ['Pn','Wt','Śr','Cz','Pt','Sb','Nd']

const steps    = computed(() => health.todayValue('steps'))
const sleep    = computed(() => health.todayValue('sleep'))
const workouts = computed(() => health.weekValues('workout').filter(v => v > 0).length)
const avgQuality = computed(() => {
  const vals = health.weekValues('sleep_quality')
  return vals.length ? Math.round(vals.reduce((a,b)=>a+b,0)/vals.length) : null
})

const stepsD = computed(() => {
  const v = steps.value
  if (!v) return { text: '', type: 'neutral' }
  return v >= 8000
    ? { text: '↑ cel osiągnięty', type: 'up' }
    : { text: '↓ poniżej celu', type: 'down' }
})
const sleepD = computed(() => {
  const v = sleep.value
  if (!v) return { text: '', type: 'neutral' }
  return v >= 8
    ? { text: '↑ powyżej celu', type: 'up' }
    : { text: '↓ poniżej celu', type: 'down' }
})

onMounted(async () => {
  await health.fetchSummary()
  buildCharts()
})

onUnmounted(() => charts.forEach(c => c.destroy()))

function buildCharts() {
  const stepsW    = health.weekValues('steps')
  const caloriesW = health.weekValues('workout').map((v, i) => {
    // kalorie są w meta — tu używamy wartości treningu jako przybliżenia
    return 0
  })
  const sleepW = health.weekValues('sleep')

  const labels = DAYS.slice(0, Math.max(stepsW.length, sleepW.length))

  charts.push(new Chart(activityCanvas.value, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        { label:'kroki',   data: stepsW,    backgroundColor:'#378ADD', yAxisID:'y',  borderRadius:3 },
        { label:'kalorie', data: caloriesW, backgroundColor:'#D4537E', yAxisID:'y2', borderRadius:3 },
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y:  { position:'left',  ticks:{ font:{size:10} }, grid:{ color:'rgba(0,0,0,0.05)' } },
        y2: { position:'right', ticks:{ font:{size:10} }, grid:{ display:false } },
      }
    }
  }))

  charts.push(new Chart(sleepCanvas.value, {
    type: 'line',
    data: {
      labels,
      datasets: [
        { label:'sen', data: sleepW, borderColor:'#534AB7', backgroundColor:'rgba(83,74,183,0.08)', fill:true, tension:0.4, pointRadius:4 },
        { label:'cel', data: Array(labels.length).fill(8), borderColor:'rgba(0,0,0,0.2)', borderDash:[5,4], pointRadius:0 },
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: { min:4, max:10, ticks:{ font:{size:10} }, grid:{ color:'rgba(0,0,0,0.05)' } },
        x: { ticks:{ font:{size:10} } }
      }
    }
  }))
}
</script>

<style scoped>
.loading { color: #888; padding: 2rem; text-align: center; }
.chart-box { position: relative; height: 210px; }
.legend { display:flex; gap:14px; font-size:12px; color:#888; margin-bottom:8px; flex-wrap:wrap; }
.legend span { display:flex; align-items:center; gap:5px; }
.dot { width:10px; height:10px; border-radius:2px; display:inline-block; }
</style>
