<script setup>
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import { postJSON } from '../api'
const kwh = ref(400)
const cmp = ref(null)
const pinned = ref(false)
const busy = ref(false)

const run = async (pin) => {
  busy.value = true
  try {
    cmp.value = await postJSON('/api/compare', { kwh: kwh.value, persist: true, pinned: pin })
    pinned.value = pin
  } finally {
    busy.value = false
  }
}
const pinCurrent = async () => {
  if (!cmp.value?.run_id) return
  await postJSON(`/api/compare/runs/${cmp.value.run_id}/pin`)
  pinned.value = true
}
</script>
<template>
  <div class="page">
    <h1>平段 vs 尖峰</h1>
    <div class="panel">
      <label>电量 <input type="number" v-model.number="kwh" /></label>
      <button :disabled="busy" @click="run(false)">对比</button>
      <button :disabled="busy" @click="run(true)">对比并钉选</button>
    </div>
    <div v-if="cmp" class="compare-grid">
      <div class="panel"><h3>平段</h3><div class="hero-num">¥{{ cmp.plain_total }}</div></div>
      <div class="panel">
        <h3>尖峰 ×{{ cmp.peak_factor }}</h3>
        <div class="hero-num">¥{{ cmp.peak_total }}</div>
      </div>
      <div class="panel"><h3>差额</h3><div class="hero-num">¥{{ cmp.delta }}</div></div>
    </div>
    <div v-if="cmp" class="panel snapshot-bar">
      <template v-if="pinned">
        <span class="badge">📌 已钉选 #{{ cmp.run_id }}，系数 ×{{ cmp.peak_factor }} 已快照</span>
        <RouterLink :to="`/compare/runs/${cmp.run_id}`">打开钉选详情</RouterLink>
      </template>
      <template v-else>
        <span class="muted">记录 #{{ cmp.run_id }}，未钉选；全局系数变更后该数字不会保留。</span>
        <button @click="pinCurrent">钉选此结果</button>
      </template>
    </div>
  </div>
</template>
<style scoped>
.compare-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.75rem; }
.snapshot-bar { display: flex; justify-content: space-between; align-items: center; gap: 1rem; margin-top: 0.75rem; }
.badge { color: var(--accent); }
</style>
