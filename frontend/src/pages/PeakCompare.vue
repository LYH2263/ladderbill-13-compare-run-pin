<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'

const kwh = ref(400)
const cmp = ref(null)
const pinError = ref('')

const runs = ref([])
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const totalPages = () => Math.max(1, Math.ceil(total.value / pageSize.value))

const run = async () => {
  cmp.value = await postJSON('/api/compare', { kwh: kwh.value, persist: false })
}

const loadRuns = async () => {
  const data = await getJSON(`/api/compare-runs?page=${page.value}&page_size=${pageSize.value}`)
  runs.value = data.items
  total.value = data.total
  pageSize.value = data.page_size
}

const pin = async () => {
  pinError.value = ''
  try {
    const pinned = await postJSON('/api/compare-runs', { kwh: kwh.value })
    cmp.value = { ...(cmp.value || {}), pinned_id: pinned.id }
    page.value = 1
    await loadRuns()
  } catch (e) {
    pinError.value = '钉选失败'
  }
}

onMounted(async () => {
  await run()
  await loadRuns()
})
</script>
<template>
  <div class="page">
    <h1>平段 vs 尖峰</h1>
    <div class="panel">
      <label>电量 <input type="number" v-model.number="kwh" /></label>
      <button @click="run">对比</button>
      <button class="pin-btn" @click="pin" :disabled="!cmp">📌 钉选当前结果</button>
      <span v-if="cmp?.pinned_id" class="muted">已钉选为 #{{ cmp.pinned_id }}</span>
      <span v-if="pinError" class="err">{{ pinError }}</span>
    </div>
    <div v-if="cmp" class="compare-grid">
      <div class="panel"><h3>平段</h3><div class="hero-num">¥{{ cmp.plain_total }}</div></div>
      <div class="panel"><h3>尖峰 ×{{ cmp.peak_factor }}</h3><div class="hero-num">¥{{ cmp.peak_total }}</div></div>
      <div class="panel"><h3>差额</h3><div class="hero-num">¥{{ cmp.delta }}</div></div>
    </div>

    <h2>已钉选的对比</h2>
    <table>
      <thead><tr><th>#</th><th>电量</th><th>平段合计</th><th>尖峰合计</th><th>差额</th><th>系数快照</th><th>钉选时间</th><th></th></tr></thead>
      <tbody>
        <tr v-for="r in runs" :key="r.id">
          <td>{{ r.id }}</td>
          <td>{{ r.kwh }}</td>
          <td>¥{{ r.plain_total }}</td>
          <td>¥{{ r.peak_total }}</td>
          <td>¥{{ r.delta }}</td>
          <td>×{{ r.peak_factor }}</td>
          <td class="muted">{{ r.created_at }}</td>
          <td><router-link :to="`/compare/runs/${r.id}`">详情</router-link></td>
        </tr>
        <tr v-if="!runs.length"><td colspan="8" class="muted">暂无钉选记录</td></tr>
      </tbody>
    </table>
    <div class="pager">
      <button :disabled="page <= 1" @click="page--; loadRuns()">上一页</button>
      <span class="muted">第 {{ page }} / {{ totalPages() }} 页（共 {{ total }} 条）</span>
      <button :disabled="page >= totalPages()" @click="page++; loadRuns()">下一页</button>
    </div>
  </div>
</template>
<style scoped>
.compare-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.75rem; }
.pin-btn { margin-left: 0.5rem; }
.pager { display: flex; align-items: center; gap: 0.75rem; margin-top: 0.75rem; }
.err { color: #ff8080; margin-left: 0.5rem; }
</style>
