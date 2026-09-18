<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, putJSON } from '../api'
const s = ref({})
const peakFactor = ref(1.2)
const saved = ref(false)
const busy = ref(false)

const load = async () => {
  s.value = await getJSON('/api/settings')
  peakFactor.value = Number(s.value.peak_factor ?? 1.2)
}
onMounted(load)

const save = async () => {
  busy.value = true
  saved.value = false
  try {
    const r = await putJSON('/api/settings/peak_factor', { peak_factor: Number(peakFactor.value) })
    peakFactor.value = r.peak_factor
    s.value.peak_factor = String(r.peak_factor)
    saved.value = true
  } finally {
    busy.value = false
  }
}
</script>
<template>
  <div class="page">
    <h1>参数</h1>
    <div class="panel">
      <h3>尖峰系数 peak_factor</h3>
      <p class="muted">仅影响修改之后发起的新对比；已钉选的运行保留其钉选当时的系数与合计。</p>
      <div class="form-row">
        <label>系数 <input type="number" min="0.01" step="0.05" v-model.number="peakFactor" /></label>
        <button :disabled="busy" @click="save">保存</button>
        <span v-if="saved" class="ok">已保存，新对比将使用 ×{{ peakFactor }}</span>
      </div>
    </div>
    <ul class="panel kv">
      <li v-for="(v, k) in s" :key="k"><span class="muted">{{ k }}</span> {{ v }}</li>
    </ul>
  </div>
</template>
<style scoped>
.kv { list-style: none; padding: 1rem; margin: 1rem 0 0; }
.kv li { padding: 0.35rem 0; border-bottom: 1px solid color-mix(in srgb, var(--muted) 25%, transparent); }
.form-row { display: flex; gap: 0.75rem; align-items: end; }
input[type=number] { width: 6rem; margin-left: 0.35rem; }
.ok { color: var(--accent); }
</style>
