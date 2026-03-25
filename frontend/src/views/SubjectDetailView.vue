<template>
  <div v-if="detail" class="detail-grid">
    <section class="page-card page-wrap">
      <div class="detail-head">
        <div>
          <h2 class="page-title">{{ detail.name }}</h2>
          <p class="page-subtitle">{{ detail.description }}</p>
        </div>
        <el-tag type="primary" size="large">{{ detail.code }}</el-tag>
      </div>

      <div class="meta-row">
        <el-tag>{{ detail.level }}</el-tag>
        <el-tag type="success">考试时长 {{ detail.exam_duration_minutes }} 分钟</el-tag>
        <el-tag type="warning">题库数量 {{ detail.statistics.total_questions }}</el-tag>
      </div>
    </section>

    <section class="quick-grid">
      <div class="page-card quick-card">
        <h3>推荐复习路径</h3>
        <p>{{ detail.recommended_path }}</p>
      </div>
      <div class="page-card quick-card">
        <h3>学习统计</h3>
        <ul>
          <li>累计做题：{{ detail.statistics.total_answered }}</li>
          <li>正确率：{{ detail.statistics.accuracy_rate }}%</li>
          <li>错题数：{{ detail.statistics.wrong_count }}</li>
          <li>已完成模拟考试：{{ detail.statistics.completed_mock_exams }}</li>
        </ul>
      </div>
    </section>

    <section class="page-card page-wrap">
      <div class="action-row">
        <el-button type="primary" @click="goPractice('chapter')">章节练习</el-button>
        <el-button type="success" @click="goPractice('random')">随机刷题</el-button>
        <el-button type="warning" @click="router.push(`/mock-exam?subjectId=${detail.id}`)">模拟考试</el-button>
      </div>
    </section>

    <section class="page-card page-wrap">
      <h3>知识点大纲</h3>
      <div class="chapter-list">
        <div v-for="chapter in detail.chapters" :key="chapter.id" class="chapter-item">
          <div>
            <strong>{{ chapter.sort_order }}. {{ chapter.title }}</strong>
            <p>{{ chapter.outline }}</p>
          </div>
          <el-tag type="info">{{ chapter.estimated_minutes }} 分钟</el-tag>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { getSubjectDetail } from '@/api'
import type { SubjectDetail } from '@/types'

const route = useRoute()
const router = useRouter()
const detail = ref<SubjectDetail | null>(null)

const goPractice = (mode: 'chapter' | 'random') => {
  router.push(`/practice?subjectId=${detail.value?.id}&mode=${mode}`)
}

onMounted(async () => {
  const response = await getSubjectDetail(Number(route.params.id))
  detail.value = response.data
})
</script>

<style scoped>
.detail-grid {
  display: grid;
  gap: 22px;
}

.page-wrap {
  padding: 28px;
}

.detail-head,
.meta-row,
.action-row,
.chapter-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.meta-row,
.action-row {
  gap: 12px;
  flex-wrap: wrap;
}

.quick-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.quick-card {
  padding: 22px;
}

.quick-card h3 {
  margin: 0 0 12px;
}

.quick-card p,
.quick-card li,
.chapter-item p {
  color: var(--text-secondary);
  line-height: 1.7;
}

.chapter-list {
  display: grid;
  gap: 14px;
  margin-top: 18px;
}

.chapter-item {
  padding: 18px;
  border-radius: 16px;
  border: 1px solid var(--border-soft);
  background: #fbfdff;
}

@media (max-width: 1100px) {
  .quick-grid {
    grid-template-columns: 1fr;
  }

  .detail-head,
  .chapter-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>
