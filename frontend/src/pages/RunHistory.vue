<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { deleteJSON, getJSON, postJSON } from '../api'

const items = ref([])
const recent = ref([])
const page = ref(1)
const pageSize = 20
const total = ref(0)
const loading = ref(false)

const totalPages = () => Math.max(1, Math.ceil(total.value / pageSize))

const load = async () => {
  loading.value = true
  try {
    const [cmp, all] = await Promise.all([
      getJSON(`/api/compare/runs?page=${page.value}&page_size=${pageSize}`),
      getJSON('/api/history?limit=20'),
    ])
    items.value = cmp.items
    total.value = cmp.total
    recent.value = all.items
  } finally {
    loading.value = false
  }
}
onMounted(load)

const go = async (p) => {
  page.value = Math.min(Math.max(1, p), totalPages())
  await load()
}

const pin = async (id, pinned) => {
  await (pinned ? deleteJSON(`/api/compare/runs/${id}/pin`) : postJSON(`/api/compare/runs/${id}/pin`))
  await load()
}
const remove = async (id) => {
  await deleteJSON(`/api/compare/runs/${id}`)
  await load()
}

const summary = (row) => {
  try {
    const r = JSON.parse(row.result_json)
    return r.total != null ? `¥${r.total}` : `平${r.plain_total}/尖${r.peak_total}`
  } catch { return '—' }
}
</script>
<template>
  <div class="page">
    <h1>测算记录</h1>

    <h2>尖峰对比运行</h2>
    <table>
      <thead>
        <tr><th>#</th><th>钉选</th><th>电量</th><th>结果摘要</th><th>系数快照</th><th>时间</th><th></th></tr>
      </thead>
      <tbody>
        <tr v-for="h in items" :key="h.id">
          <td><RouterLink :to="`/compare/runs/${h.id}`">#{{ h.id }}</RouterLink></td>
          <td><span v-if="h.pinned">📌</span><span v-else class="muted">—</span></td>
          <td>{{ JSON.parse(h.input_json).kwh }}</td>
          <td>{{ summary(h) }}</td>
          <td class="muted">×{{ JSON.parse(h.input_json).peak_factor ?? '—' }}</td>
          <td class="muted">{{ h.created_at }}</td>
          <td class="actions">
            <RouterLink :to="`/compare/runs/${h.id}`">详情</RouterLink>
            <button @click="pin(h.id, h.pinned)">{{ h.pinned ? '取消钉选' : '钉选' }}</button>
            <button @click="remove(h.id)">删除</button>
          </td>
        </tr>
        <tr v-if="!loading && !items.length"><td colspan="7" class="muted">暂无对比记录</td></tr>
      </tbody>
    </table>
    <div class="pager">
      <button :disabled="page <= 1" @click="go(page - 1)">上一页</button>
      <span class="muted">第 {{ page }} / {{ totalPages() }} 页（共 {{ total }} 条）</span>
      <button :disabled="page >= totalPages()" @click="go(page + 1)">下一页</button>
    </div>

    <h2>全部类型 · 最近 20 条</h2>
    <table>
      <thead><tr><th>#</th><th>类型</th><th>户号</th><th>结果摘要</th><th>时间</th></tr></thead>
      <tbody>
        <tr v-for="h in recent" :key="h.id">
          <td>{{ h.id }}</td><td>{{ h.kind }}</td><td>{{ h.account_id ?? '—' }}</td>
          <td>{{ summary(h) }}</td><td class="muted">{{ h.created_at }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
<style scoped>
.pager { display: flex; gap: 0.75rem; align-items: center; margin: 0.75rem 0 1.5rem; }
.actions { display: flex; gap: 0.5rem; white-space: nowrap; }
h2 { font-size: 1rem; margin: 1.25rem 0 0.5rem; }
</style>
