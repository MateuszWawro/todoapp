<template>
  <div id="app">
    <router-view v-if="!isLoggedIn" />
    <template v-else>
      <header class="topbar">
        <div class="topbar-left">
          <span class="logo">life dashboard</span>
          <span class="username">— {{ auth.user?.username }}</span>
        </div>
        <button class="logout-btn" @click="logout">wyloguj</button>
      </header>

      <nav class="tabs">
        <router-link class="tab" to="/">przegląd</router-link>
        <router-link class="tab" to="/sleep">sen</router-link>
        <router-link class="tab" to="/tasks">zadania</router-link>
        <router-link class="tab" to="/correlations">korelacje</router-link>
      </nav>

      <main class="content">
        <router-view />
      </main>
    </template>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'

const auth   = useAuthStore()
const router = useRouter()

const isLoggedIn = computed(() => auth.isLoggedIn)

onMounted(async () => {
  if (auth.token && !auth.user) {
    try { await auth.fetchMe() }
    catch { auth.logout(); router.push('/login') }
  }
})

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<style>
#app { min-height: 100vh; }

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 11px 20px;
  background: #fff;
  border-bottom: 1px solid rgba(0,0,0,0.08);
}
.topbar-left { display: flex; align-items: center; gap: 8px; }
.logo    { font-size: 15px; font-weight: 600; }
.username { font-size: 13px; color: #888; }
.logout-btn {
  font-size: 13px; color: #666; background: none;
  border: 1px solid #ddd; border-radius: 7px;
  padding: 4px 12px; cursor: pointer;
}
.logout-btn:hover { background: #f5f5f3; }

.tabs {
  display: flex;
  background: #fff;
  border-bottom: 1px solid rgba(0,0,0,0.08);
  padding: 0 20px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}
.tab {
  font-size: 13px;
  color: #888;
  padding: 9px 14px;
  text-decoration: none;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
  white-space: nowrap;
  transition: color .15s;
}
.tab.router-link-active { color: #1a1a18; border-bottom-color: #1a1a18; font-weight: 500; }
.tab:hover:not(.router-link-active) { color: #444; }

.content { padding: 20px; }

/* ── shared UI ──────────────────────────────────────────────────────────────── */
.card {
  background: #fff;
  border: 1px solid rgba(0,0,0,0.08);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 14px;
}
.section-lbl {
  font-size: 11px; font-weight: 500; color: #888;
  text-transform: uppercase; letter-spacing: .05em;
  margin-bottom: 12px;
}
.metric-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  margin-bottom: 14px;
}
.metric-card {
  background: #f5f5f3; border-radius: 9px; padding: 13px 14px;
}
.metric-lbl { font-size: 11px; color: #888; margin-bottom: 3px; text-transform: uppercase; letter-spacing: .04em; }
.metric-val { font-size: 22px; font-weight: 600; }
.metric-unit { font-size: 12px; font-weight: 400; color: #888; }
.metric-delta { font-size: 11px; margin-top: 2px; }
.up   { color: #3b6d11; }
.down { color: #a32d2d; }

.two-col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

/* ── responsive ─────────────────────────────────────────────────────────────── */
@media (max-width: 700px) {
  .metric-grid { grid-template-columns: repeat(2, 1fr); }
  .two-col { grid-template-columns: 1fr; }
  .content { padding: 12px; }
  .card { padding: 12px; margin-bottom: 10px; }
  .tabs { padding: 0 10px; }
  .tab { padding: 9px 10px; font-size: 12px; }
  .topbar { padding: 10px 14px; }
}
@media (max-width: 400px) {
  .metric-grid { gap: 8px; }
  .metric-val { font-size: 18px; }
  .metric-card { padding: 10px 11px; }
}
</style>