<template>
  <div>
    <div v-if="store.loading" class="loading">Obliczanie korelacji...</div>
    <template v-else>
      <div class="two-col">
        <div class="card">
          <div class="section-lbl">korelacje z produktywnością</div>

          <div v-if="!store.correlations.length" class="empty">
            Za mało danych — potrzeba min. 5 dni z danymi zdrowotnymi i zadaniami.
          </div>

          <div v-for="c in store.correlations" :key="c.label" class="corr-row">
            <span class="corr-lbl">{{ c.label }}</span>
            <div class="corr-bar-bg">
              <div
                class="corr-bar-fill"
                :style="{ width: Math.abs(c.r) * 100 + '%', background: c.r > 0 ? '#1D9E75' : '#D85A30' }"
              ></div>
            </div>
            <span class="corr-num" :style="{ color: c.r > 0 ? '#3b6d11' : '#a32d2d' }">
              {{ c.r > 0 ? '+' : '' }}{{ c.r.toFixed(2) }}
            </span>
            <span class="sig-badge" :class="c.significant ? 'sig' : 'insig'">
              {{ c.significant ? 'istotne' : 'p=' + c.p }}
            </span>
          </div>
        </div>

        <div class="card">
          <div class="section-lbl">sen vs ukończone zadania</div>
          <div class="chart-box"><canvas ref="scatterCanvas"></canvas></div>
        </div>
      </div>

      <div class="card info-card">
        <div class="section-lbl">jak czytać korelacje?</div>
        <p>Wartość bliższa <strong>+1</strong> oznacza silną pozytywną zależność, bliższa <strong>-1</strong> silną negatywną. Wartości poniżej ±0.3 są słabe. Wyniki oznaczone jako <em>istotne</em> mają p&lt;0.05 — czyli statystycznie wiarygodne. Potrzebujesz min. 5 dni danych do obliczenia korelacji.</p>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { Chart, registerables } from 'chart.js'
import { useAnalyticsStore } from '../stores/analytics'

Chart.register(...registerables)

const store        = useAnalyticsStore()
const scatterCanvas = ref(null)
let chart = null

onMounted(async () => {
  await store.fetchCorrelations(30)
  buildScatter()
})
onUnmounted(() => { if (chart) chart.destroy() })

function buildScatter() {
  if (!scatterCanvas.value) return
  chart = new Chart(scatterCanvas.value, {
    type: 'scatter',
    data: {
      datasets: [{
        data: store.scatter.map(p => ({ x: p.sleep, y: p.tasks })),
        backgroundColor: '#378ADD',
        pointRadius: 6,
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { title:{ display:true, text:'sen (godz.)', font:{size:11} }, min:4, max:10, ticks:{ font:{size:10} } },
        y: { title:{ display:true, text:'zadania ukończone', font:{size:11} }, min:0, ticks:{ stepSize:1, font:{size:10} } }
      }
    }
  })
}
</script>

<style scoped>
.loading { color:#888; padding:2rem; text-align:center; }
.empty   { color:#aaa; font-size:13px; padding:1rem 0; }
.chart-box { position:relative; height:260px; }

.corr-row {
  display:flex; align-items:center; gap:10px;
  padding:10px 0; border-bottom:1px solid rgba(0,0,0,0.07);
}
.corr-row:last-child { border-bottom:none; }
.corr-lbl  { flex:1; font-size:13px; }
.corr-bar-bg { width:100px; height:6px; background:#eee; border-radius:3px; overflow:hidden; flex-shrink:0; }
.corr-bar-fill { height:100%; border-radius:3px; transition:width .3s; }
.corr-num { font-size:13px; font-weight:600; width:40px; text-align:right; flex-shrink:0; }
.sig-badge {
  font-size:10px; padding:2px 6px; border-radius:99px; flex-shrink:0;
}
.sig   { background:#eaf3de; color:#3b6d11; }
.insig { background:#f5f5f3; color:#888; }

.info-card p { font-size:13px; color:#666; line-height:1.6; }
.info-card strong { color:#1a1a18; }
.info-card em { color:#534AB7; font-style:normal; }

@media (max-width:700px) {
  .corr-bar-bg { width:60px; }
  .sig-badge { display:none; }
}
</style>
