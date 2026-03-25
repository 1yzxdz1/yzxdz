<template>
  <div v-if="overview" class="stats-layout">
    <section class="page-card page-wrap">
      <h2 class="page-title">学习统计</h2>
      <p class="page-subtitle">基于当前登录用户的真实练习记录生成七日趋势、章节正确率和高频错误知识点分析。</p>
    </section>

    <section class="stats-grid">
      <StatCard label="累计学习时长" :value="`${overview.total_study_minutes} 分钟`" extra="本地练习时长近似统计" />
      <StatCard label="累计做题" :value="overview.total_answered" extra="含章节练习、随机刷题、模拟考试" />
      <StatCard label="正确率" :value="`${overview.accuracy_rate}%`" extra="自动按提交记录汇总" />
      <StatCard label="待攻克错题" :value="overview.wrong_count" extra="可前往错题本继续练习" />
    </section>

    <section v-if="overview.total_answered > 0" class="chart-grid">
      <ChartPanel title="章节正确率" subtitle="按章节展示当前掌握度" :option="chapterOption" />
      <ChartPanel title="高频错误知识点" subtitle="基于错题标签统计薄弱点" :option="weakTagOption" />
    </section>

    <section v-else class="page-card page-wrap empty-guide">
      <el-empty description="当前还没有学习统计数据" />
      <div class="guide-actions">
        <el-button type="primary" @click="router.push('/practice')">开始第一轮练习</el-button>
        <el-button @click="router.push('/subjects')">先去看科目大纲</el-button>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import ChartPanel from '@/components/ChartPanel.vue'
import StatCard from '@/components/StatCard.vue'
import { getStatisticsOverview } from '@/api'

const router = useRouter()
const overview = ref<any>(null)

const chapterOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  xAxis: {
    type: 'category',
    axisLabel: { rotate: 18 },
    data: (overview.value?.chapter_accuracy ?? []).map((item: any) => item.chapter_title),
  },
  yAxis: { type: 'value', max: 100 },
  series: [
    {
      type: 'bar',
      data: (overview.value?.chapter_accuracy ?? []).map((item: any) => item.accuracy_rate),
      itemStyle: { color: '#22a06b', borderRadius: [8, 8, 0, 0] },
    },
  ],
}))

const weakTagOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  xAxis: {
    type: 'category',
    data: (overview.value?.weak_tags ?? []).map((item: any) => item.tag),
  },
  yAxis: { type: 'value' },
  series: [
    {
      type: 'bar',
      data: (overview.value?.weak_tags ?? []).map((item: any) => item.count),
      itemStyle: { color: '#ff7d45', borderRadius: [8, 8, 0, 0] },
    },
  ],
}))

onMounted(async () => {
  const response = await getStatisticsOverview()
  overview.value = response.data
})
</script>

<style scoped>
.stats-layout {
  display: grid;
  gap: 22px;
}

.page-wrap {
  padding: 28px;
}

.stats-grid,
.chart-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.empty-guide {
  display: grid;
  justify-items: center;
  gap: 12px;
}

.guide-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

@media (max-width: 1100px) {
  .stats-grid,
  .chart-grid {
    grid-template-columns: 1fr;
  }
}
</style>
