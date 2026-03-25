<template>
  <div class="dashboard">
    <section class="page-card hero">
      <div>
        <h2 class="page-title">全国计算机等级考试复习平台</h2>
        <p class="page-subtitle">
          面向课程设计、比赛展示和个人作品集的 NCRE 复习系统，已接入真实后端数据、章节题库、模拟考试和学习统计。
        </p>
      </div>
      <el-button type="primary" size="large" @click="router.push('/subjects')">开始选择科目</el-button>
    </section>

    <section class="stats-grid">
      <StatCard label="总做题数" :value="overview?.total_answered ?? 0" extra="基于当前登录用户记录" />
      <StatCard label="正确率" :value="`${overview?.accuracy_rate ?? 0}%`" extra="练习与模拟考试自动统计" />
      <StatCard label="错题数" :value="overview?.wrong_count ?? 0" extra="支持错题再练" />
      <StatCard label="已完成模拟考试数" :value="overview?.completed_mock_exams ?? 0" extra="支持自动生成成绩单" />
    </section>

    <section v-if="hasStudyData" class="content-grid">
      <ChartPanel
        title="最近 7 天学习趋势"
        subtitle="展示近 7 天练习题量与答对题量变化"
        :option="trendOption"
      />
      <ChartPanel
        title="知识点掌握情况"
        subtitle="基于章节正确率生成掌握度柱状图"
        :option="masteryOption"
      />
    </section>

    <section v-else class="page-card onboarding-panel">
      <div class="onboarding-copy">
        <h3>欢迎来到你的专属复习空间</h3>
        <p>
          当前账号还没有学习记录。先选一个科目开始第一轮练习，系统会自动生成你的统计、错题本、收藏和模拟考试成绩。
        </p>
      </div>
      <div class="onboarding-actions">
        <el-button type="primary" size="large" @click="router.push('/subjects')">去选科目</el-button>
        <el-button size="large" @click="router.push('/practice')">直接开始练习</el-button>
        <el-button size="large" @click="router.push('/mock-exam')">进入模拟考试</el-button>
      </div>
    </section>

    <section class="panel-grid">
      <div class="page-card panel">
        <div class="panel-head">
          <h3>可选科目</h3>
          <el-button text @click="router.push('/subjects')">查看全部</el-button>
        </div>
        <div class="subject-list">
          <div v-for="subject in subjects" :key="subject.id" class="subject-item">
            <div>
              <strong>{{ subject.name }}</strong>
              <p>{{ subject.level }} · {{ subject.code }} · {{ subject.exam_duration_minutes }} 分钟</p>
            </div>
            <el-button link type="primary" @click="router.push(`/subjects/${subject.id}`)">进入</el-button>
          </div>
        </div>
      </div>

      <div class="page-card panel">
        <div class="panel-head">
          <h3>最近学习记录</h3>
        </div>
        <el-empty v-if="!overview?.recent_records?.length" description="暂无记录" />
        <div v-else class="record-list">
          <div v-for="record in overview.recent_records" :key="record.id" class="record-item">
            <div>
              <strong>题目 #{{ record.question_id }}</strong>
              <p>{{ formatMode(record.mode) }} · {{ formatTime(record.practiced_at) }}</p>
            </div>
            <el-tag :type="record.is_correct ? 'success' : 'danger'">
              {{ record.is_correct ? '答对' : '答错' }}
            </el-tag>
          </div>
        </div>
      </div>
    </section>

    <section v-if="errorMessage" class="page-card panel">
      <el-alert :title="errorMessage" type="error" show-icon :closable="false" />
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import ChartPanel from '@/components/ChartPanel.vue'
import StatCard from '@/components/StatCard.vue'
import { getStatisticsOverview, getSubjects } from '@/api'
import type { Subject } from '@/types'

const router = useRouter()
const subjects = ref<Subject[]>([])
const overview = ref<any>(null)
const errorMessage = ref('')
const hasStudyData = computed(() => (overview.value?.total_answered ?? 0) > 0)

const trendOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  legend: { data: ['做题数', '答对数'] },
  xAxis: {
    type: 'category',
    data: (overview.value?.seven_day_trend ?? []).map((item: any) => item.date.slice(5)),
  },
  yAxis: { type: 'value' },
  series: [
    {
      name: '做题数',
      type: 'line',
      smooth: true,
      data: (overview.value?.seven_day_trend ?? []).map((item: any) => item.answered),
      itemStyle: { color: '#1f6feb' },
    },
    {
      name: '答对数',
      type: 'line',
      smooth: true,
      data: (overview.value?.seven_day_trend ?? []).map((item: any) => item.correct),
      itemStyle: { color: '#39a96b' },
    },
  ],
}))

const masteryOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  xAxis: {
    type: 'category',
    axisLabel: { rotate: 18 },
    data: (overview.value?.knowledge_mastery ?? []).map((item: any) => item.name),
  },
  yAxis: { type: 'value', max: 100 },
  series: [
    {
      type: 'bar',
      barWidth: 28,
      data: (overview.value?.knowledge_mastery ?? []).map((item: any) => item.value),
      itemStyle: {
        color: '#ff9f43',
        borderRadius: [8, 8, 0, 0],
      },
    },
  ],
}))

const formatMode = (mode: string) => {
  const map: Record<string, string> = {
    chapter_practice: '章节练习',
    random_practice: '随机刷题',
    mock_exam: '模拟考试',
  }
  return map[mode] ?? mode
}

const formatTime = (value: string) => new Date(value).toLocaleString('zh-CN')

const loadData = async () => {
  try {
    const [subjectResp, overviewResp] = await Promise.all([getSubjects(), getStatisticsOverview()])
    subjects.value = subjectResp.data
    overview.value = overviewResp.data
    errorMessage.value = ''
  } catch (error) {
    console.error(error)
    errorMessage.value = '首页数据加载失败。请确认后端运行中，并允许 127.0.0.1:5173 跨域访问。'
  }
}

onMounted(loadData)
</script>

<style scoped>
.dashboard {
  display: grid;
  gap: 22px;
}

.hero {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 28px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 18px;
}

.content-grid,
.panel-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.onboarding-panel {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  padding: 28px;
  border: 1px solid #dfe9fb;
  background: linear-gradient(135deg, #f8fbff 0%, #eef5ff 100%);
}

.onboarding-copy h3 {
  margin: 0 0 10px;
  font-size: 24px;
}

.onboarding-copy p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.8;
}

.onboarding-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.panel {
  padding: 22px;
}

.panel-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

.panel-head h3 {
  margin: 0;
}

.subject-list,
.record-list {
  display: grid;
  gap: 14px;
}

.subject-item,
.record-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border: 1px solid var(--border-soft);
  border-radius: 16px;
  background: #fbfdff;
}

.subject-item p,
.record-item p {
  margin: 6px 0 0;
  color: var(--text-secondary);
  font-size: 13px;
}

@media (max-width: 1100px) {
  .stats-grid,
  .content-grid,
  .panel-grid {
    grid-template-columns: 1fr;
  }

  .hero {
    flex-direction: column;
    align-items: flex-start;
    gap: 18px;
  }

  .onboarding-panel {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
