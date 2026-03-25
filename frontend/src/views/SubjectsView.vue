<template>
  <div class="page-grid">
    <section class="page-card page-wrap">
      <h2 class="page-title">科目选择页</h2>
      <p class="page-subtitle">按考试级别分类展示所有演示科目，点击即可进入科目详情、查看大纲并开始练习。</p>
    </section>

    <section v-for="group in groupedSubjects" :key="group.level" class="page-card page-wrap">
      <div class="level-head">
        <h3>{{ group.level }}</h3>
        <el-tag>{{ group.items.length }} 门科目</el-tag>
      </div>

      <div class="subject-grid">
        <div v-for="subject in group.items" :key="subject.id" class="subject-card">
          <div class="subject-top">
            <span class="subject-code">{{ subject.code }}</span>
            <el-tag type="info">{{ subject.exam_duration_minutes }} 分钟</el-tag>
          </div>
          <h4>{{ subject.name }}</h4>
          <p>{{ subject.description }}</p>
          <el-button type="primary" plain @click="router.push(`/subjects/${subject.id}`)">查看详情</el-button>
        </div>
      </div>
    </section>

    <section v-if="errorMessage" class="page-card page-wrap error-panel">
      <el-alert :title="errorMessage" type="error" show-icon :closable="false" />
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { getSubjects } from '@/api'
import type { Subject } from '@/types'

const router = useRouter()
const subjects = ref<Subject[]>([])
const errorMessage = ref('')

const groupedSubjects = computed(() => {
  const groups = new Map<string, Subject[]>()
  subjects.value.forEach((subject: Subject) => {
    if (!groups.has(subject.level)) {
      groups.set(subject.level, [])
    }
    groups.get(subject.level)?.push(subject)
  })
  return Array.from(groups.entries()).map(([level, items]) => ({ level, items }))
})

onMounted(async () => {
  try {
    const response = await getSubjects()
    subjects.value = response.data
    errorMessage.value = response.data.length ? '' : '接口已连接，但当前没有返回科目数据。'
  } catch (error) {
    console.error(error)
    errorMessage.value = '科目数据加载失败。请确认后端已启动，并允许 http://127.0.0.1:5173 访问。'
  }
})
</script>

<style scoped>
.page-grid {
  display: grid;
  gap: 22px;
}

.error-panel {
  border-color: #ffd2cc;
}

.page-wrap {
  padding: 28px;
}

.level-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}

.level-head h3,
.subject-card h4 {
  margin: 0;
}

.subject-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 18px;
}

.subject-card {
  padding: 20px;
  border-radius: 18px;
  border: 1px solid var(--border-soft);
  background: linear-gradient(180deg, #ffffff 0%, #f7faff 100%);
}

.subject-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.subject-code {
  color: var(--brand);
  font-size: 13px;
  font-weight: 700;
}

.subject-card p {
  min-height: 66px;
  color: var(--text-secondary);
  line-height: 1.7;
}
</style>
