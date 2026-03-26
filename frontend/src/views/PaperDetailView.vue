<template>
  <div v-if="detail" class="paper-grid">
    <section class="page-card page-wrap">
      <div class="paper-head">
        <div>
          <h2 class="page-title">{{ detail.title }}</h2>
          <p class="page-subtitle">{{ detail.description }}</p>
        </div>
        <el-button plain @click="router.back()">返回</el-button>
      </div>

      <div class="meta-row">
        <el-tag type="primary">{{ detail.year }} {{ detail.season }}</el-tag>
        <el-tag type="success">{{ detail.total_questions }} 题</el-tag>
        <el-tag type="warning">{{ detail.total_score }} 分</el-tag>
        <el-tag>{{ detail.duration_minutes }} 分钟</el-tag>
      </div>
    </section>

    <section class="page-card page-wrap">
      <div class="section-head">
        <div>
          <h3>套卷说明</h3>
          <p>当前为按年份组织的演示真题结构，后续可以继续导入更完整的历年原题和套卷答案。</p>
        </div>
        <el-button type="primary" @click="router.push(`/mock-exam?subjectId=${detail.subject_id}`)">进入模拟考试</el-button>
      </div>
    </section>

    <section class="page-card page-wrap">
      <h3>题目预览</h3>
      <div class="question-list">
        <div v-for="item in detail.questions" :key="`${item.sort_order}-${item.question.id}`" class="question-item">
          <div class="question-meta">
            <el-tag size="small" type="info">第 {{ item.sort_order }} 题</el-tag>
            <el-tag size="small">{{ item.section_name }}</el-tag>
            <el-tag size="small" type="warning">{{ item.score }} 分</el-tag>
            <el-tag size="small" :type="difficultyType(item.question.difficulty)">{{ item.question.difficulty }}</el-tag>
          </div>
          <h4>{{ item.question.stem }}</h4>
          <ul v-if="item.question.options?.length" class="option-list">
            <li v-for="option in item.question.options" :key="option.key">
              {{ option.key }}. {{ option.text }}
            </li>
          </ul>
          <p class="question-extra">章节：{{ item.question.chapter }}</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { getPaperDetail } from '@/api'
import type { PastPaperDetail } from '@/types'

const route = useRoute()
const router = useRouter()
const detail = ref<PastPaperDetail | null>(null)

const difficultyType = (difficulty: string) => {
  if (difficulty === 'hard') return 'danger'
  if (difficulty === 'medium') return 'warning'
  return 'success'
}

onMounted(async () => {
  const response = await getPaperDetail(Number(route.params.id))
  detail.value = response.data
})
</script>

<style scoped>
.paper-grid {
  display: grid;
  gap: 22px;
}

.page-wrap {
  padding: 28px;
}

.paper-head,
.meta-row,
.section-head,
.question-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.meta-row,
.question-meta {
  gap: 12px;
  flex-wrap: wrap;
}

.question-list {
  display: grid;
  gap: 16px;
  margin-top: 18px;
}

.question-item {
  padding: 18px;
  border-radius: 16px;
  border: 1px solid var(--border-soft);
  background: #fbfdff;
}

.question-item h4 {
  margin: 14px 0 12px;
  line-height: 1.7;
}

.option-list {
  margin: 0;
  padding-left: 18px;
  color: var(--text-secondary);
  line-height: 1.8;
}

.question-extra,
.section-head p {
  color: var(--text-secondary);
}

@media (max-width: 1100px) {
  .paper-head,
  .section-head {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>
