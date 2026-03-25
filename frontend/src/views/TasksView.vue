<template>
  <div>
    <!-- Dodaj zadanie -->
    <div class="add-row">
      <input
        v-model="newTitle"
        type="text"
        placeholder="nowe zadanie..."
        @keydown.enter="addTask"
      />
      <select v-model="newCat">
        <option value="personal">osobiste</option>
        <option value="work">praca</option>
        <option value="health">zdrowie</option>
      </select>
      <button class="add-btn" @click="addTask">+ dodaj</button>
    </div>

    <!-- Metryki -->
    <div class="task-metrics">
      <MetricCard label="do zrobienia" :value="store.todo.length" />
      <MetricCard label="ukończone"    :value="store.done.length" delta="dziś" deltaType="up" />
      <MetricCard label="czas pracy"
        :value="totalHours > 0 ? totalHours + 'h ' + totalMinsRem : totalMinsRem"
        unit="min" />
    </div>

    <!-- Lista -->
    <div v-if="store.loading" class="loading">Ładowanie...</div>
    <div v-else class="task-list">
      <div
        v-for="task in store.tasks"
        :key="task.id"
        class="task-item"
        :class="{ done: task.status === 'done' }"
      >
        <div
          class="chk"
          :class="{ on: task.status === 'done' }"
          @click="toggleDone(task)"
        >{{ task.status === 'done' ? '✓' : '' }}</div>

        <span class="task-txt">{{ task.title }}</span>

        <span class="cat-badge" :class="'cat-' + task.category">{{ task.category }}</span>

        <span class="task-time">{{ fmtTime(task._elapsed) }}</span>

        <button
          v-if="task.status !== 'done'"
          class="timer-btn"
          :class="{ running: store.activeTimer === task.id }"
          @click="toggleTimer(task)"
        >
          {{ store.activeTimer === task.id ? '⏹ stop' : '▶ start' }}
        </button>

        <button class="del-btn" @click="deleteTask(task.id)">✕</button>
      </div>

      <div v-if="!store.tasks.length" class="empty">Brak zadań — dodaj pierwsze!</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import MetricCard from '../components/ui/MetricCard.vue'
import { useTasksStore } from '../stores/tasks'

const store   = useTasksStore()
const newTitle = ref('')
const newCat   = ref('personal')

onMounted(() => store.fetchTasks())

const totalHours   = computed(() => Math.floor(store.totalMins / 60))
const totalMinsRem = computed(() => store.totalMins % 60)

function fmtTime(min) {
  if (!min) return '—'
  const h = Math.floor(min/60), m = min%60
  return h > 0 ? `${h}h ${m}min` : `${m}min`
}

async function addTask() {
  const t = newTitle.value.trim()
  if (!t) return
  await store.addTask(t, newCat.value)
  newTitle.value = ''
}

async function toggleDone(task) {
  const next = task.status === 'done' ? 'todo' : 'done'
  if (store.activeTimer === task.id) await store.stopTimer(task.id)
  await store.updateTask(task.id, { status: next })
}

async function toggleTimer(task) {
  if (store.activeTimer === task.id) {
    await store.stopTimer(task.id)
  } else {
    await store.startTimer(task.id)
  }
}

async function deleteTask(id) {
  if (store.activeTimer === id) await store.stopTimer(id)
  await store.deleteTask(id)
}
</script>

<style scoped>
.add-row { display:flex; gap:8px; margin-bottom:14px; flex-wrap:wrap; }
.add-row input { flex:1; min-width:0; }
.add-row select { width:130px; }
.add-btn {
  background:#1a1a18; color:#fff; border:none;
  border-radius:8px; padding:7px 16px; cursor:pointer;
  font-weight:500; white-space:nowrap;
}
.add-btn:hover { background:#333; }

.task-metrics {
  display:grid; grid-template-columns:repeat(3,1fr);
  gap:10px; margin-bottom:14px;
}

.loading { color:#888; padding:2rem; text-align:center; }
.empty   { color:#aaa; text-align:center; padding:2rem; font-size:14px; }

.task-list { display:flex; flex-direction:column; gap:8px; }
.task-item {
  display:flex; align-items:center; gap:10px;
  background:#fff; border:1px solid rgba(0,0,0,0.08);
  border-radius:9px; padding:10px 14px;
  transition: opacity .2s;
}
.task-item.done { opacity:.5; }

.chk {
  width:18px; height:18px; border-radius:50%;
  border:1.5px solid #ccc; cursor:pointer; flex-shrink:0;
  display:flex; align-items:center; justify-content:center;
  font-size:10px; transition: background .15s, border-color .15s;
}
.chk.on { background:#eaf3de; border-color:#3b6d11; color:#3b6d11; }

.task-txt { flex:1; font-size:14px; }

.cat-badge { font-size:11px; padding:2px 9px; border-radius:99px; }
.cat-personal { background:#e6f1fb; color:#185fa5; }
.cat-work     { background:#faeeda; color:#854f0b; }
.cat-health   { background:#eaf3de; color:#3b6d11; }

.task-time { font-size:12px; color:#888; white-space:nowrap; min-width:48px; text-align:right; }

.timer-btn {
  font-size:11px; padding:3px 10px;
  border-radius:7px; border:1px solid #ddd;
  background:none; color:#666; cursor:pointer; white-space:nowrap;
}
.timer-btn:hover   { background:#f5f5f3; }
.timer-btn.running { border-color:#c0392b; color:#c0392b; }

.del-btn {
  font-size:11px; color:#ccc; background:none;
  border:none; cursor:pointer; padding:2px 4px;
}
.del-btn:hover { color:#c0392b; }

@media (max-width:700px) {
  .add-row select { width:calc(50% - 4px); }
  .add-btn        { width:calc(50% - 4px); }
  .task-item      { flex-wrap:wrap; gap:6px; }
  .task-txt       { width:calc(100% - 30px); }
}
</style>
