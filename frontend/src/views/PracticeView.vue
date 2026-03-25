<template>
  <div class="practice-grid">
    <section class="page-card page-wrap">
      <h2 class="page-title">练习中心</h2>
      <p class="page-subtitle">支持章节练习和随机刷题，每题提交后立即显示正误、分值与解析，并支持收藏。</p>

      <div class="toolbar">
        <el-select v-model="selectedSubjectId" placeholder="请选择科目" style="width: 280px" @change="handleSubjectChange">
          <el-option v-for="subject in subjects" :key="subject.id" :label="subject.name" :value="subject.id" />
        </el-select>

        <el-select v-model="selectedChapterId" placeholder="章节筛选" clearable style="width: 240px" @change="loadQuestions">
          <el-option v-for="chapter in chapters" :key="chapter.id" :label="chapter.title" :value="chapter.id" />
        </el-select>

        <el-select v-model="mode" style="width: 180px" @change="loadQuestions">
          <el-option label="章节练习" value="chapter" />
          <el-option label="随机刷题" value="random" />
        </el-select>

        <el-button type="primary" @click="loadQuestions">开始练习</el-button>
      </div>
    </section>

    <section v-if="questions.length" class="page-card page-wrap">
      <div class="question-head">
        <div>
          <h3>当前题目 {{ currentIndex + 1 }} / {{ questions.length }}</h3>
          <p>{{ currentQuestion.chapter }} · {{ typeLabel(currentQuestion.question_type) }} · {{ currentQuestion.difficulty }}</p>
        </div>
        <div class="action-buttons">
          <el-button plain @click="toggleFavorite(currentQuestion)">
            {{ currentQuestion.is_favorite ? '取消收藏' : '收藏题目' }}
          </el-button>
          <el-button @click="goPrev" :disabled="currentIndex === 0">上一题</el-button>
          <el-button @click="goNext" :disabled="currentIndex === questions.length - 1">下一题</el-button>
        </div>
      </div>

      <div class="question-card">
        <h3>{{ currentQuestion.stem }}</h3>

        <el-checkbox-group
          v-if="currentQuestion.question_type === 'multiple_choice'"
          v-model="selectedAnswers"
          class="option-list"
        >
          <el-checkbox v-for="option in currentQuestion.options" :key="option.key" :label="option.key">
            {{ option.key }}. {{ option.text }}
          </el-checkbox>
        </el-checkbox-group>

        <el-radio-group
          v-else-if="currentQuestion.question_type !== 'short_answer'"
          v-model="singleAnswer"
          class="option-list"
        >
          <el-radio v-for="option in currentQuestion.options" :key="option.key" :label="option.key">
            {{ option.key }}. {{ option.text }}
          </el-radio>
        </el-radio-group>

        <el-input
          v-else
          v-model="shortAnswer"
          type="textarea"
          :rows="5"
          placeholder="请输入你的作答内容"
        />

        <div class="submit-row">
          <el-button type="primary" @click="submitCurrentQuestion">提交本题</el-button>
        </div>

        <el-alert
          v-if="feedback"
          :title="feedback.is_correct ? '回答正确' : '回答错误'"
          :type="feedback.is_correct ? 'success' : 'error'"
          show-icon
          :closable="false"
        >
          <template #default>
            <p>得分：{{ feedback.score_obtained }}</p>
            <p>正确答案：{{ feedback.correct_answer.join(', ') }}</p>
            <p>解析：{{ feedback.explanation }}</p>
          </template>
        </el-alert>
      </div>
    </section>

    <section v-else class="page-card page-wrap empty-state">
      <el-empty description="请选择科目并开始练习" />
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import { addFavorite, getChapters, getQuestions, getRandomQuestions, getSubjects, removeFavorite, submitPractice } from '@/api'
import type { Question, Subject } from '@/types'

const route = useRoute()
const subjects = ref<Subject[]>([])
const chapters = ref<any[]>([])
const questions = ref<Question[]>([])
const currentIndex = ref(0)
const selectedSubjectId = ref<number | undefined>(undefined)
const selectedChapterId = ref<number | undefined>(undefined)
const mode = ref<'chapter' | 'random'>('chapter')
const selectedAnswers = ref<string[]>([])
const singleAnswer = ref('')
const shortAnswer = ref('')
const feedback = ref<any>(null)

const currentQuestion = computed(() => questions.value[currentIndex.value])

const resetAnswer = () => {
  selectedAnswers.value = []
  singleAnswer.value = ''
  shortAnswer.value = ''
  feedback.value = null
}

const typeLabel = (type: string) => {
  const map: Record<string, string> = {
    single_choice: '单选题',
    multiple_choice: '多选题',
    true_false: '判断题',
    short_answer: '简答题',
  }
  return map[type] ?? type
}

const syncAnswerFromQuestionType = () => {
  resetAnswer()
}

const handleSubjectChange = async () => {
  selectedChapterId.value = undefined
  const chapterResp = await getChapters(selectedSubjectId.value)
  chapters.value = chapterResp.data
  await loadQuestions()
}

const loadQuestions = async () => {
  if (!selectedSubjectId.value) return

  const response =
    mode.value === 'random'
      ? await getRandomQuestions(selectedSubjectId.value, 10)
      : await getQuestions({
          subject_id: selectedSubjectId.value,
          ...(selectedChapterId.value ? { chapter_id: selectedChapterId.value } : {}),
          page_size: 10,
        })

  questions.value = response.data.items
  currentIndex.value = 0
  syncAnswerFromQuestionType()
}

const getCurrentUserAnswer = () => {
  if (!currentQuestion.value) return []
  if (currentQuestion.value.question_type === 'multiple_choice') return selectedAnswers.value
  if (currentQuestion.value.question_type === 'short_answer') return [shortAnswer.value]
  return singleAnswer.value ? [singleAnswer.value] : []
}

const submitCurrentQuestion = async () => {
  if (!currentQuestion.value) return
  feedback.value = (
    await submitPractice({
      question_id: currentQuestion.value.id,
      user_answer: getCurrentUserAnswer(),
      mode: mode.value === 'random' ? 'random_practice' : 'chapter_practice',
      duration_seconds: 120,
    })
  ).data
}

const toggleFavorite = async (question: Question) => {
  if (question.is_favorite) {
    await removeFavorite(question.id)
    question.is_favorite = false
  } else {
    await addFavorite(question.id)
    question.is_favorite = true
  }
}

const goPrev = () => {
  if (currentIndex.value > 0) {
    currentIndex.value -= 1
    syncAnswerFromQuestionType()
  }
}

const goNext = () => {
  if (currentIndex.value < questions.value.length - 1) {
    currentIndex.value += 1
    syncAnswerFromQuestionType()
  }
}

watch(currentQuestion, () => syncAnswerFromQuestionType())

onMounted(async () => {
  const subjectResp = await getSubjects()
  subjects.value = subjectResp.data

  const routeSubjectId = Number(route.query.subjectId)
  const routeMode = String(route.query.mode || 'chapter')

  selectedSubjectId.value = routeSubjectId || subjects.value[0]?.id
  mode.value = routeMode === 'random' ? 'random' : 'chapter'

  if (selectedSubjectId.value) {
    await handleSubjectChange()
  }
})
</script>

<style scoped>
.practice-grid {
  display: grid;
  gap: 22px;
}

.page-wrap {
  padding: 28px;
}

.toolbar,
.question-head,
.action-buttons,
.submit-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.toolbar {
  margin-top: 18px;
}

.question-head {
  justify-content: space-between;
}

.question-head h3 {
  margin: 0;
}

.question-head p {
  margin: 8px 0 0;
  color: var(--text-secondary);
}

.question-card {
  margin-top: 20px;
  padding: 22px;
  border-radius: 20px;
  border: 1px solid var(--border-soft);
  background: #fbfdff;
}

.option-list {
  display: grid;
  gap: 14px;
  margin-top: 18px;
}

.submit-row {
  margin-top: 22px;
}

.empty-state {
  min-height: 260px;
  display: grid;
  place-items: center;
}
</style>
