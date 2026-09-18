<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, putJSON } from '../api'
const s = ref({})
const peakFactor = ref(1.2)
const msg = ref('')
const err = ref('')

const load = async () => {
  s.value = await getJSON('/api/settings')
  peakFactor.value = Number(s.value.peak_factor ?? 1.2)
}

const save = async () => {
  msg.value = ''
  err.value = ''
  try {
    s.value = await putJSON('/api/settings', { peak_factor: peakFactor.value })
    peakFactor.value = Number(s.value.peak_factor)
    msg.value = '已保存：此后新对比使用新系数；已钉选记录仍保留当时的系数与合计。'
  } catch (e) {
    err.value = '保存失败：系数须为正数'
  }
}

onMounted(load)
</script>
<template>
  <div class="page">
    <h1>参数</h1>
    <div class="panel">
      <label>尖峰系数 peak_factor
        <input type="number" step="0.05" min="0.01" v-model.number="peakFactor" />
      </label>
      <button @click="save">保存系数</button>
      <p v-if="msg" class="ok">{{ msg }}</p>
      <p v-if="err" class="err">{{ err }}</p>
    </div>
    <ul class="panel kv">
      <li v-for="(v, k) in s" :key="k"><span class="muted">{{ k }}</span> {{ v }}</li>
    </ul>
  </div>
</template>
<style scoped>
.kv { list-style: none; padding: 1rem; margin: 0; }
.kv li { padding: 0.35rem 0; border-bottom: 1px solid color-mix(in srgb, var(--muted) 25%, transparent); }
.ok { color: var(--accent); }
.err { color: #ff8080; }
</style>
