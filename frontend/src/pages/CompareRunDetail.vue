<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { deleteJSON, getJSON, postJSON } from '../api'
import TierLadder from '../components/TierLadder.vue'
import SegmentTable from '../components/SegmentTable.vue'

const route = useRoute()
const row = ref(null)
const result = ref(null)
const input = ref(null)
const notFound = ref(false)
const error = ref('')

const load = async () => {
  try {
    row.value = await getJSON(`/api/compare/runs/${route.params.id}`)
    result.value = JSON.parse(row.value.result_json)
    input.value = JSON.parse(row.value.input_json)
  } catch (e) {
    notFound.value = true
    error.value = String(e.message || e)
  }
}
onMounted(load)

const togglePin = async () => {
  if (!row.value) return
  if (row.value.pinned) {
    row.value = await deleteJSON(`/api/compare/runs/${row.value.id}/pin`)
  } else {
    row.value = await postJSON(`/api/compare/runs/${row.value.id}/pin`)
  }
}
</script>
<template>
  <div class="page">
    <p class="muted"><RouterLink to="/history">← 返回记录</RouterLink></p>

    <div v-if="notFound" class="panel">
      <h1>记录不存在</h1>
      <p class="muted">#{{ route.params.id }} 无法读取。</p>
    </div>

    <template v-else-if="row && result">
      <h1>
        对比详情 #{{ row.id }}
        <span v-if="row.pinned" class="tag">📌 已钉选 {{ row.pinned_at?.slice(0, 19).replace('T', ' ') }}</span>
        <span v-if="row.deleted_at" class="tag tag-del">已删除（详情仍可读）</span>
      </h1>
      <p class="muted">
        运行时间 {{ row.created_at?.slice(0, 19).replace('T', ' ') }} ·
        电量 {{ input.kwh }} kWh ·
        系数快照 <strong>×{{ result.peak_factor }}</strong>
        <span v-if="input.peak_factor !== undefined" class="muted">（钉选/运行当时的全局系数）</span>
      </p>

      <div class="compare-grid">
        <div class="panel"><h3>平段合计</h3><div class="hero-num">¥{{ result.plain_total }}</div></div>
        <div class="panel"><h3>尖峰合计 ×{{ result.peak_factor }}</h3><div class="hero-num">¥{{ result.peak_total }}</div></div>
        <div class="panel"><h3>差值</h3><div class="hero-num">¥{{ result.delta }}</div></div>
      </div>

      <div class="panel">
        <h3>尖峰分段</h3>
        <TierLadder :segments="result.peak_segments" />
        <SegmentTable :rows="result.peak_segments" />
      </div>
      <div class="panel">
        <h3>平段分段</h3>
        <SegmentTable :rows="result.plain_segments" />
      </div>

      <div class="panel actions">
        <button @click="togglePin">{{ row.pinned ? '取消钉选' : '钉选此运行' }}</button>
        <RouterLink to="/compare">再做一次对比</RouterLink>
      </div>
    </template>
  </div>
</template>
<style scoped>
.compare-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.75rem; }
.tag { font-size: 0.8rem; font-weight: 400; padding: 0.1rem 0.5rem; border-radius: 999px;
       background: color-mix(in srgb, var(--accent) 20%, var(--panel)); margin-left: 0.5rem; }
.tag-del { background: color-mix(in srgb, #c0392b 20%, var(--panel)); }
.actions { display: flex; gap: 1rem; align-items: center; margin-top: 0.75rem; }
</style>
