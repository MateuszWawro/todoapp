<template>
  <div>
    <div v-if="health.loading" class="loading">Ładowanie...</div>
    <template v-else>
      <div class="metric-grid">
        <MetricCard label="średni sen"  :value="avgSleep"  unit="godz." />
        <MetricCard label="najkrótszy" :value="minSleep"  unit="godz." deltaType="down" :delta="minSleep < 7 ? '↓ niedobór' : ''" />
        <MetricCard label="najdłuższy" :value="maxSleep"  unit="godz." deltaType="up"   :delta="maxSleep >= 8 ? '↑ świetnie' : ''" />
        <MetricCard label="jakość śr." :value="avgQuality" unit="%" />
      </div>

      <div class="two-col">
        <div class="card">
          <div class="section-lbl">sen vs cel 8h — ostatnie 14 dni</div>
          <div class="legend">
            <span><span class="dot" style="background:#1D9E75"></span>≥ 8h</span>
            <span><span class="dot" style="background:#378ADD"></span>7–8h</span>
            <span><span class="dot" style="background:#D85A30"></span>&lt; 7h</span>
          </div>
          <div class="chart-box"><canvas ref="barCanvas"></canvas></div>
        </div>
        <div class="card">
          <div class="section-lbl">jakość snu — ostatnie 14 dni</div>
          <div class="chart-box"><canvas ref="qualityCanvas"></canvas></div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Chart, registerables } from 'chart.js'
import MetricCard from '../components/ui/MetricCard.vue'
import { useHealthStore } from '../stores/health'

Chart.register(...registerables)

const health       = useHealthStore()
const barCanvas    = ref(null)
const qualityCanvas = ref(null)
let charts = []

onMounted(async () => {
  await health.fetchMetrics('sleep', 14)
  buildCharts()
})
onUnmounted(() => charts.forEach(c => c.destroy()))

const sleep14 = computed(() => health.metrics.filter(m => m.type === 'sleep'))
const vals    = computed(() => sleep14.value.map(m => parseFloat(m.value)))
const labels  = computed(() => sleep14.value.map(m => m.date?.slice(5)))  // MM-DD

const avgSleep  = computed(() => vals.value.length ? (vals.value.reduce((a,b)=>a+b,0)/vals.value.length).toFixed(1) : null)
const minSleep  = computed(() => vals.value.length ? Math.min(...vals.value).toFixed(1) : null)
const maxSleep  = computed(() => vals.value.length ? Math.max(...vals.value).toFixed(1) : null)
const avgQuality = computed(() => {
  const q = health.metrics.filter(m => m.type === 'sleep_quality').map(m => parseFloat(m.value))
  return q.length ? Math.round(q.reduce((a,b)=>a+b,0)/q.length) : null
})

function buildCharts() {
  const v = vals.value
  const l = labels.value

  charts.push(new Chart(barCanvas.value, {
    type: 'bar',
    data: {
      labels: l,
      datasets: [
        { label:'sen', data: v, backgroundColor: v.map(x => x>=8?'#1D9E75':x>=7?'#378ADD':'#D85A30'), borderRadius:3 },
        { label:'cel 8h', data: Array(l.length).fill(8), type:'line', borderColor:'rgba(0,0,0,0.2)', borderDash:[5,4], pointRadius:0 },
      ]
    },
    options: {
      responsive:true, maintainAspectRatio:false,
      plugins:{ legend:{ display:false } },
      scales:{
        y:{ min:4, max:10, ticks:{font:{size:10}}, grid:{color:'rgba(0,0,0,0.05)'} },
        x:{ ticks:{font:{size:9}, maxRotation:45, autoSkip:false} }
      }
    }
  }))

  const qVals = health.metrics.filter(m=>m.type==='sleep_quality').map(m=>parseFloat(m.value))
  charts.push(new Chart(qualityCanvas.value, {
    type: 'line',
    data: {
      labels: l,
      datasets: [{ label:'jakość', data: qVals.length ? qVals : Array(l.length).fill(null),
        borderColor:'#534AB7', backgroundColor:'rgba(83,74,183,0.07)', fill:true, tension:0.4, pointRadius:2 }]
    },
    options: {
      responsive:true, maintainAspectRatio:false,
      plugins:{ legend:{ display:false } },
      scales:{
        y:{ min:50, max:100, ticks:{font:{size:10}, callback:v=>v+'%'}, grid:{color:'rgba(0,0,0,0.05)'} },
        x:{ ticks:{font:{size:9}, maxRotation:45, autoSkip:false} }
      }
    }
  }))
}
</script>

<style scoped>
.loading { color:#888; padding:2rem; text-align:center; }
.chart-box { position:relative; height:210px; }
.legend { display:flex; gap:14px; font-size:12px; color:#888; margin-bottom:8px; flex-wrap:wrap; }
.legend span { display:flex; align-items:center; gap:5px; }
.dot { width:10px; height:10px; border-radius:2px; display:inline-block; }
</style>
