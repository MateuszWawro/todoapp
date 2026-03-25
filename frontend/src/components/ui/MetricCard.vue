<template>
  <div class="metric-card">
    <div class="metric-lbl">{{ label }}</div>
    <div class="metric-val">
      {{ value ?? '—' }}<span v-if="unit" class="metric-unit"> {{ unit }}</span>
    </div>
    <div v-if="delta" class="metric-delta" :class="deltaClass">{{ delta }}</div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({
  label: String,
  value: [String, Number],
  unit:  String,
  delta: String,
  deltaType: { type: String, default: 'up' }  // 'up' | 'down' | 'neutral'
})
const deltaClass = computed(() => props.deltaType)
</script>
