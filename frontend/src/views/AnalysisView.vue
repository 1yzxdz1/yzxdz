<template>
  <div class="analysis-grid" v-if="analysis">
    <section class="page-card page-wrap">
      <h2 class="page-title">成绩分析</h2>
      <p class="page-subtitle">{{ analysis.title }} · 本次得分 {{ analysis.obtained_score }} / {{ analysis.total_score }}</p>

      <div class="score-grid">
        <div class="score-card">
          <span>正确题数</span>
          <strong>{{ analysis.correct_count }}</strong>
        </div>
        <div class="score-card">
          <span>总题数</span>
          <strong>{{ analysis.total_questions }}</strong>
        </div>
        <div class="score-card">
          <span>正确率</span>
          <strong>{{ analysis.accuracy_rate }}%</strong>
        </div>
      </div>
    </section>

    <section class="page-card page-wrap">
      <h3>错题与解析</h3>
      <div class="answer-list">
        <div v-for="item in wrongAnswers" :key="item.question_id" class="answer-item">
          <strong>题目 #{{ item.question_id }}</strong>
          <p>正确答案：{{ item.correct_answer.join(', ') }}</p>
          <p>解析：{{ item.explanation }}</p>
        </div>
      </div>
      <el-empty v-if="wrongAnswers.length === 0" description="本次模拟卷全部答对" />
    </section>
  </div>

  <section v-else class="page-card page-wrap">
    <h2 class="page-title">成绩分析</h2>
    <p class="page-subtitle">当前还没有可分析的成绩单。先去模拟考试页完成一套试卷，系统会自动生成成绩分析。</p>
    <div class="analysis-actions">
      <el-button type="primary" @click="router.push('/mock-exam')">去模拟考试</el-button>
      <el-button @click="router.push('/practice')">先做章节练习</el-button>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const analysis = ref<any>(null)

const raw = localStorage.getItem('ncre-last-analysis')
if (raw) {
  analysis.value = JSON.parse(raw)
}

const wrongAnswers = computed(() => (analysis.value?.answers ?? []).filter((item: any) => !item.is_correct))
</script>

<style scoped>
.analysis-grid {
  display: grid;
  gap: 22px;
}

.page-wrap {
  padding: 28px;
}

.score-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
  margin-top: 22px;
}

.score-card {
  padding: 20px;
  border-radius: 18px;
  background: #f7faff;
  border: 1px solid var(--border-soft);
}

.score-card span {
  color: var(--text-secondary);
}

.score-card strong {
  display: block;
  margin-top: 12px;
  font-size: 32px;
}

.answer-list {
  display: grid;
  gap: 14px;
  margin-top: 18px;
}

.answer-item {
  padding: 18px;
  border-radius: 16px;
  border: 1px solid var(--border-soft);
  background: #fff8f6;
}

.answer-item p {
  color: var(--text-secondary);
  line-height: 1.7;
}

.analysis-actions {
  display: flex;
  gap: 12px;
  margin-top: 18px;
  flex-wrap: wrap;
}
</style>
