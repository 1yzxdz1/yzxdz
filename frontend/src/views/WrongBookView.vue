<template>
  <div class="wrong-grid">
    <section class="page-card page-wrap">
      <h2 class="page-title">错题本</h2>
      <p class="page-subtitle">自动收录答错题目，支持按科目筛选，并可一键跳转继续练习。</p>

      <div class="toolbar">
        <el-select v-model="selectedSubjectId" clearable placeholder="按科目筛选" style="width: 300px" @change="loadWrongQuestions">
          <el-option v-for="subject in subjects" :key="subject.id" :label="subject.name" :value="subject.id" />
        </el-select>
        <el-button type="primary" @click="loadWrongQuestions">刷新</el-button>
      </div>
    </section>

    <section class="page-card page-wrap">
      <div v-if="!items.length" class="empty-guide">
        <el-empty description="当前没有错题记录" />
        <div class="guide-copy">先做几道题，系统会自动把答错的题加入错题本。</div>
        <div class="toolbar">
          <el-button type="primary" @click="router.push('/practice')">去练习中心</el-button>
          <el-button @click="router.push('/mock-exam')">先做一套模拟卷</el-button>
        </div>
      </div>
      <div v-else class="wrong-list">
        <div v-for="item in items" :key="item.id" class="wrong-item">
          <div>
            <strong>{{ item.question.stem }}</strong>
            <p>{{ item.question.chapter }} · 错误次数 {{ item.wrong_count }} · {{ item.resolved ? '已掌握' : '待攻克' }}</p>
          </div>
          <el-button type="primary" plain @click="retryQuestion(item.question.subject_id)">再做一遍</el-button>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { getSubjects, getWrongQuestions } from '@/api'
import type { Subject } from '@/types'

const router = useRouter()
const subjects = ref<Subject[]>([])
const items = ref<any[]>([])
const selectedSubjectId = ref<number | undefined>(undefined)

const loadWrongQuestions = async () => {
  const response = await getWrongQuestions(
    selectedSubjectId.value ? { subject_id: selectedSubjectId.value } : undefined,
  )
  items.value = response.data
}

const retryQuestion = (subjectId: number) => {
  router.push(`/practice?subjectId=${subjectId}&mode=random`)
}

onMounted(async () => {
  const subjectResp = await getSubjects()
  subjects.value = subjectResp.data
  await loadWrongQuestions()
})
</script>

<style scoped>
.wrong-grid {
  display: grid;
  gap: 22px;
}

.page-wrap {
  padding: 28px;
}

.toolbar {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-top: 18px;
}

.wrong-list {
  display: grid;
  gap: 14px;
}

.empty-guide {
  display: grid;
  justify-items: center;
  gap: 10px;
}

.guide-copy {
  color: var(--text-secondary);
}

.wrong-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 18px;
  padding: 18px;
  border: 1px solid var(--border-soft);
  border-radius: 18px;
  background: #fffaf7;
}

.wrong-item p {
  margin: 8px 0 0;
  color: var(--text-secondary);
}
</style>
