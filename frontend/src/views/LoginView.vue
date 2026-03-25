<template>
  <div class="login-wrap">
    <div class="login-card">
      <div class="login-logo">life dashboard</div>
      <div class="login-sub">twoje dane, twoje życie</div>

      <label class="lbl">login</label>
      <input v-model="form.username" type="text" placeholder="mateusz / agnieszka"
             @keydown.enter="submit" />

      <label class="lbl">hasło</label>
      <input v-model="form.password" type="password" placeholder="••••••••"
             @keydown.enter="submit" />

      <p v-if="error" class="err">{{ error }}</p>

      <button class="btn" :disabled="loading" @click="submit">
        {{ loading ? 'logowanie...' : 'zaloguj się' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const auth   = useAuthStore()
const router = useRouter()
const form   = reactive({ username: '', password: '' })
const error  = ref('')
const loading = ref(false)

async function submit() {
  if (!form.username || !form.password) return
  error.value   = ''
  loading.value = true
  try {
    await auth.login(form.username, form.password)
    router.push('/')
  } catch {
    error.value = 'Nieprawidłowy login lub hasło'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-wrap {
  display: flex; align-items: center; justify-content: center;
  min-height: 100vh; background: #eeede8;
}
.login-card {
  background: #fff; border: 1px solid rgba(0,0,0,0.1);
  border-radius: 14px; padding: 2rem 2.25rem; width: 340px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.07);
  display: flex; flex-direction: column; gap: 4px;
}
.login-logo { font-size: 22px; font-weight: 600; margin-bottom: 2px; }
.login-sub  { font-size: 13px; color: #888; margin-bottom: 12px; }
.lbl        { font-size: 12px; color: #666; margin-top: 8px; }
input       { width: 100%; }
.err        { font-size: 13px; color: #c0392b; margin-top: 4px; }
.btn {
  margin-top: 12px; width: 100%;
  background: #1a1a18; color: #fff; border: none;
  border-radius: 8px; padding: 10px; font-size: 14px;
  font-weight: 500; cursor: pointer;
}
.btn:hover:not(:disabled) { background: #333; }
.btn:disabled { opacity: .6; cursor: not-allowed; }

@media (max-width: 400px) {
  .login-wrap { align-items: flex-start; padding-top: 2rem; }
  .login-card { width: calc(100% - 2rem); margin: 0 1rem; }
}
</style>
