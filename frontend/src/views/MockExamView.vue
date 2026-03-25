<template>
  <div class="exam-grid">
    <section v-if="!exam" class="page-card page-wrap">
      <div class="setup-head">
        <div>
          <h2 class="page-title">模拟考试</h2>
          <p class="page-subtitle">
            生成模拟卷后将进入考场模式：顶部倒计时、右侧答题卡、逐题作答、标记状态和统一交卷，更贴近真实考试氛围。
          </p>
        </div>
        <el-tag type="danger" size="large">Exam Mode</el-tag>
      </div>

      <div class="setup-grid">
        <div class="page-card setup-card">
          <h3>考试设置</h3>
          <div class="form-stack">
            <el-select v-model="selectedSubjectId" placeholder="请选择科目">
              <el-option v-for="subject in subjects" :key="subject.id" :label="subject.name" :value="subject.id" />
            </el-select>
            <el-input-number v-model="questionCount" :min="10" :max="40" />
            <el-button type="primary" size="large" @click="generateExam">开始模拟考试</el-button>
          </div>
        </div>

        <div class="page-card setup-card">
          <h3>考试说明</h3>
          <ul class="rule-list">
            <li>系统将根据所选科目自动随机组卷。</li>
            <li>支持单选、多选、判断和简答题。</li>
            <li>考试开始后显示倒计时，时间到会自动交卷。</li>
            <li>可通过答题卡查看未作答、已作答和已标记状态。</li>
          </ul>
        </div>
      </div>
    </section>

    <section v-else class="exam-mode">
      <div class="exam-topbar page-card">
        <div>
          <h2>{{ exam.title }}</h2>
          <p>{{ exam.total_questions }} 题 · 总分 {{ exam.total_score }} · {{ currentQuestion.chapter }}</p>
        </div>
        <div class="exam-top-actions">
          <div class="timer-box" :class="{ danger: remainingSeconds <= 300 }">
            剩余时间 {{ formattedTime }}
          </div>
          <el-button plain @click="toggleMarkCurrent">
            {{ markedQuestionIds.has(currentQuestion.id) ? '取消标记' : '标记本题' }}
          </el-button>
          <el-button type="warning" @click="confirmSubmit">交卷</el-button>
        </div>
      </div>

      <div class="exam-main">
        <section class="page-card question-panel">
          <div class="question-header">
            <div>
              <div class="question-index">第 {{ activeIndex + 1 }} 题 / 共 {{ exam.questions.length }} 题</div>
              <h3>{{ currentQuestion.stem }}</h3>
              <p>{{ typeLabel(currentQuestion.question_type) }} · {{ currentQuestion.chapter }} · {{ currentQuestion.score }} 分</p>
            </div>
            <div class="status-tags">
              <el-tag v-if="markedQuestionIds.has(currentQuestion.id)" type="warning">已标记</el-tag>
              <el-tag :type="questionStatus(currentQuestion.id) === 'answered' ? 'success' : 'info'">
                {{ questionStatusText(questionStatus(currentQuestion.id)) }}
              </el-tag>
            </div>
          </div>

          <el-checkbox-group
            v-if="currentQuestion.question_type === 'multiple_choice'"
            v-model="answers[currentQuestion.id]"
            class="option-list"
          >
            <el-checkbox v-for="option in currentQuestion.options" :key="option.key" :label="option.key">
              {{ option.key }}. {{ option.text }}
            </el-checkbox>
          </el-checkbox-group>

          <el-radio-group
            v-else-if="currentQuestion.question_type !== 'short_answer'"
            v-model="singleAnswerMap[currentQuestion.id]"
            class="option-list"
          >
            <el-radio v-for="option in currentQuestion.options" :key="option.key" :label="option.key">
              {{ option.key }}. {{ option.text }}
            </el-radio>
          </el-radio-group>

          <el-input
            v-else
            v-model="shortAnswerMap[currentQuestion.id]"
            type="textarea"
            :rows="6"
            placeholder="请输入简答题答案"
          />

          <div class="question-actions">
            <el-button @click="goPrev" :disabled="activeIndex === 0">上一题</el-button>
            <el-button type="primary" @click="saveAndNext">
              {{ activeIndex === exam.questions.length - 1 ? '保存作答' : '保存并下一题' }}
            </el-button>
          </div>
        </section>

        <aside class="page-card answer-card-panel">
          <div class="card-head">
            <h3>答题卡</h3>
            <p>已答 {{ answeredCount }} / {{ exam.questions.length }}</p>
          </div>

          <div class="card-grid">
            <button
              v-for="(question, index) in exam.questions"
              :key="question.id"
              class="card-item"
              :class="questionStatus(question.id)"
              type="button"
              @click="activeIndex = Number(index)"
            >
              {{ Number(index) + 1 }}
            </button>
          </div>

          <div class="card-legend">
            <span><i class="legend-dot unanswered"></i>未作答</span>
            <span><i class="legend-dot answered"></i>已作答</span>
            <span><i class="legend-dot marked"></i>已标记</span>
          </div>
        </aside>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'

import { generateMockExam, getSubjects, submitMockExam } from '@/api'
import type { Question, Subject } from '@/types'

const route = useRoute()
const router = useRouter()

const subjects = ref<Subject[]>([])
const selectedSubjectId = ref<number | undefined>(undefined)
const questionCount = ref(20)
const exam = ref<any>(null)
const activeIndex = ref(0)
const answers = ref<Record<number, string[]>>({})
const singleAnswerMap = ref<Record<number, string>>({})
const shortAnswerMap = ref<Record<number, string>>({})
const markedQuestionIds = ref<Set<number>>(new Set())
const remainingSeconds = ref(0)
let timer: number | null = null

const currentQuestion = computed<Question>(() => exam.value.questions[activeIndex.value])

const normalizeAnswers = (question: Question): string[] => {
  if (question.question_type === 'multiple_choice') {
    return answers.value[question.id] ?? []
  }
  if (question.question_type === 'short_answer') {
    return shortAnswerMap.value[question.id]?.trim() ? [shortAnswerMap.value[question.id].trim()] : []
  }
  return singleAnswerMap.value[question.id] ? [singleAnswerMap.value[question.id]] : []
}

const questionStatus = (questionId: number): 'unanswered' | 'answered' | 'marked' => {
  const question = exam.value.questions.find((item: Question) => item.id === questionId)
  if (!question) return 'unanswered'
  const answered = normalizeAnswers(question).length > 0
  if (markedQuestionIds.value.has(questionId)) return 'marked'
  return answered ? 'answered' : 'unanswered'
}

const questionStatusText = (status: 'unanswered' | 'answered' | 'marked') => {
  const map = {
    unanswered: '未作答',
    answered: '已作答',
    marked: '已标记',
  }
  return map[status]
}

const answeredCount = computed(() => {
  if (!exam.value) return 0
  return exam.value.questions.filter((question: Question) => normalizeAnswers(question).length > 0).length
})

const formattedTime = computed(() => {
  const minutes = Math.floor(remainingSeconds.value / 60)
  const seconds = remainingSeconds.value % 60
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
})

const typeLabel = (type: string) => {
  const map: Record<string, string> = {
    single_choice: '单选题',
    multiple_choice: '多选题',
    true_false: '判断题',
    short_answer: '简答题',
  }
  return map[type] ?? type
}

const startTimer = (minutes: number) => {
  if (timer) {
    window.clearInterval(timer)
  }
  remainingSeconds.value = minutes * 60
  timer = window.setInterval(() => {
    remainingSeconds.value -= 1
    if (remainingSeconds.value <= 0) {
      if (timer) {
        window.clearInterval(timer)
      }
      ElMessage.warning('考试时间已到，系统将自动交卷。')
      submitExam(true)
    }
  }, 1000)
}

const generateExam = async () => {
  if (!selectedSubjectId.value) {
    ElMessage.warning('请先选择科目。')
    return
  }
  const response = await generateMockExam({
    subject_id: selectedSubjectId.value,
    question_count: questionCount.value,
  })
  exam.value = response.data
  activeIndex.value = 0
  answers.value = {}
  singleAnswerMap.value = {}
  shortAnswerMap.value = {}
  markedQuestionIds.value = new Set()
  startTimer(response.data.duration_minutes)
}

const submitExam = async (isAuto = false) => {
  if (!exam.value) return
  if (timer) {
    window.clearInterval(timer)
  }

  const payload = {
    answers: exam.value.questions.map((question: Question) => ({
      question_id: question.id,
      user_answer: normalizeAnswers(question),
    })),
  }
  const response = await submitMockExam(exam.value.id, payload)
  localStorage.setItem('ncre-last-analysis', JSON.stringify(response.data))
  ElMessage.success(isAuto ? '已自动交卷。' : '交卷成功，正在跳转成绩分析页。')
  router.push('/analysis')
}

const confirmSubmit = async () => {
  if (!exam.value) return
  const unanswered = exam.value.questions.filter((question: Question) => normalizeAnswers(question).length === 0).length
  await ElMessageBox.confirm(
    `当前还有 ${unanswered} 题未作答，确认现在交卷吗？`,
    '交卷确认',
    {
      confirmButtonText: '确认交卷',
      cancelButtonText: '继续作答',
      type: 'warning',
    },
  )
  await submitExam(false)
}

const toggleMarkCurrent = () => {
  if (!currentQuestion.value) return
  const next = new Set(markedQuestionIds.value)
  if (next.has(currentQuestion.value.id)) {
    next.delete(currentQuestion.value.id)
  } else {
    next.add(currentQuestion.value.id)
  }
  markedQuestionIds.value = next
}

const goPrev = () => {
  if (activeIndex.value > 0) activeIndex.value -= 1
}

const saveAndNext = () => {
  ElMessage.success('当前题目已保存。')
  if (activeIndex.value < exam.value.questions.length - 1) {
    activeIndex.value += 1
  }
}

onMounted(async () => {
  const response = await getSubjects()
  subjects.value = response.data
  const routeSubjectId = Number(route.query.subjectId)
  selectedSubjectId.value = routeSubjectId || subjects.value[0]?.id
})

onBeforeUnmount(() => {
  if (timer) {
    window.clearInterval(timer)
  }
})
</script>

<style scoped>
.exam-grid {
  display: grid;
  gap: 22px;
}

.page-wrap {
  padding: 28px;
}

.setup-head,
.setup-grid,
.exam-main,
.exam-topbar,
.exam-top-actions,
.question-header,
.question-actions {
  display: flex;
  gap: 18px;
}

.setup-head,
.exam-topbar,
.question-header,
.question-actions {
  justify-content: space-between;
  align-items: center;
}

.setup-grid {
  margin-top: 22px;
  align-items: stretch;
}

.setup-card {
  flex: 1;
  padding: 24px;
}

.setup-card h3 {
  margin-top: 0;
}

.form-stack {
  display: grid;
  gap: 16px;
}

.rule-list {
  margin: 0;
  padding-left: 18px;
  color: var(--text-secondary);
  line-height: 1.9;
}

.exam-mode {
  display: grid;
  gap: 18px;
}

.exam-topbar {
  padding: 18px 22px;
}

.exam-topbar h2 {
  margin: 0;
}

.exam-topbar p {
  margin: 8px 0 0;
  color: var(--text-secondary);
}

.exam-top-actions {
  align-items: center;
}

.timer-box {
  padding: 12px 18px;
  border-radius: 999px;
  background: #eff5ff;
  color: var(--brand-deep);
  font-weight: 700;
}

.timer-box.danger {
  background: #fff0ee;
  color: #c0392b;
}

.exam-main {
  align-items: flex-start;
}

.question-panel {
  flex: 1;
  padding: 24px;
}

.answer-card-panel {
  width: 320px;
  padding: 22px;
  position: sticky;
  top: 12px;
}

.question-index {
  color: var(--brand);
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 10px;
}

.question-header h3 {
  margin: 0;
  font-size: 24px;
  line-height: 1.5;
}

.question-header p {
  margin: 10px 0 0;
  color: var(--text-secondary);
}

.status-tags {
  display: flex;
  gap: 10px;
}

.option-list {
  display: grid;
  gap: 14px;
  margin-top: 24px;
}

.question-actions {
  margin-top: 26px;
}

.card-head h3 {
  margin: 0;
}

.card-head p {
  margin: 8px 0 0;
  color: var(--text-secondary);
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 10px;
  margin-top: 18px;
}

.card-item {
  height: 42px;
  border: 1px solid var(--border-soft);
  border-radius: 12px;
  background: #f7faff;
  cursor: pointer;
  font-weight: 700;
}

.card-item.answered {
  background: #e9f8ef;
  border-color: #62be8a;
  color: #1f7a4d;
}

.card-item.marked {
  background: #fff4dd;
  border-color: #ffb648;
  color: #9c5a00;
}

.card-item.unanswered {
  color: #607084;
}

.card-legend {
  display: grid;
  gap: 8px;
  margin-top: 20px;
  color: var(--text-secondary);
  font-size: 13px;
}

.legend-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  margin-right: 8px;
  border-radius: 999px;
}

.legend-dot.unanswered {
  background: #b6c3d5;
}

.legend-dot.answered {
  background: #62be8a;
}

.legend-dot.marked {
  background: #ffb648;
}

@media (max-width: 1180px) {
  .setup-grid,
  .exam-main {
    flex-direction: column;
  }

  .answer-card-panel {
    width: 100%;
    position: static;
  }

  .exam-topbar,
  .question-header,
  .question-actions {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
