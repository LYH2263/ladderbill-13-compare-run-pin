<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { deleteJSON, getJSON } from '../api'
import SegmentTable from '../components/SegmentTable.vue'

const route = useRoute()
const router = useRouter()
const run = ref(null)
const notFound = ref(false)

const load = async () => {
  try {
    run.value = await getJSON(`/api/compare-runs/${route.params.id}`)
  } catch {
    notFound.value = true
  }
}

const remove = async () => {
  await deleteJSON(`/api/compare-runs/${route.params.id}`)
  router.push('/compare')
}

onMounted(load)
</script>
<template>
  <div class="page">
    <p><router-link to="/compare">← 尖峰对比</router-link></p>
    <p v-if="notFound" class="err">记录不存在</p>
    <template v-else-if="run">
      <h1>
        钉选对比 #{{ run.id }}
        <span v-if="run.deleted_at" class="tag-deleted">已删除（快照仍可读）</span>
      </h1>
      <p class="muted">钉选于 {{ run.created_at }}　电量 {{ run.kwh }} kWh</p>

      <div class="compare-grid">
        <div class="panel"><h3>平段合计</h3><div class="hero-num">¥{{ run.plain_total }}</div></div>
        <div class="panel"><h3>尖峰合计 ×{{ run.peak_factor }}</h3><div class="hero-num">¥{{ run.peak_total }}</div></div>
        <div class="panel"><h3>差值</h3><div class="hero-num">¥{{ run.delta }}</div></div>
      </div>

      <div class="detail-grid">
        <div class="panel">
          <h3>平段明细</h3>
          <SegmentTable :rows="run.segments?.plain_segments || []" />
        </div>
        <div class="panel">
          <h3>尖峰明细（系数 ×{{ run.peak_factor }} 快照）</h3>
          <SegmentTable :rows="run.segments?.peak_segments || []" />
        </div>
      </div>

      <p class="muted note">
        本页合计与系数为钉选当时的快照；之后在设置中修改尖峰系数不会改变这里的数字。
      </p>
      <button v-if="!run.deleted_at" class="del-btn" @click="remove">软删除（列表中隐藏）</button>
    </template>
  </div>
</template>
<style scoped>
.compare-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.75rem; }
.detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin-top: 0.5rem; }
.tag-deleted { font-size: 0.85rem; color: #ffb86b; border: 1px solid #ffb86b; border-radius: 8px; padding: 0.1rem 0.5rem; margin-left: 0.5rem; }
.note { margin-top: 1rem; }
.del-btn { background: #b8553f; color: #fff; }
.err { color: #ff8080; }
</style>
