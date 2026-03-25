<template>
  <el-container class="app-shell">
    <el-aside width="260px" class="aside-panel">
      <div class="brand-block">
        <div class="brand-badge">NCRE</div>
        <div>
          <h2>Review System</h2>
          <p>全国计算机等级考试复习平台</p>
        </div>
      </div>

      <el-menu :default-active="activePath" router class="nav-menu">
        <el-menu-item v-for="item in menus" :key="item.path" :index="item.path">
          <span>{{ item.label }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="topbar">
        <div>
          <h1>{{ currentTitle }}</h1>
          <p>{{ authStore.displayName }} · 个人学习空间</p>
        </div>
        <div class="topbar-actions">
          <el-tag type="primary" round>FastAPI + Vue 3 MVP</el-tag>
          <el-button @click="handleLogout">退出登录</el-button>
        </div>
      </el-header>

      <el-main class="main-panel">
        <RouterView />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute } from 'vue-router'
import { useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const menus = [
  { path: '/', label: '首页 Dashboard' },
  { path: '/subjects', label: '科目列表' },
  { path: '/practice', label: '练习中心' },
  { path: '/mock-exam', label: '模拟考试' },
  { path: '/analysis', label: '成绩分析' },
  { path: '/wrong-book', label: '错题本' },
  { path: '/statistics', label: '学习统计' },
]

const activePath = computed(() => route.path)
const currentTitle = computed(() => menus.find((item) => item.path === route.path)?.label ?? 'NCRE Review System')

const handleLogout = async () => {
  await authStore.logout()
  ElMessage.success('已退出登录')
  router.push('/login')
}
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
}

.aside-panel {
  padding: 24px 18px;
  border-right: 1px solid var(--border-soft);
  background: linear-gradient(180deg, #12325f 0%, #173f78 100%);
  color: #fff;
}

.brand-block {
  display: flex;
  gap: 14px;
  align-items: center;
  margin-bottom: 28px;
}

.brand-badge {
  display: grid;
  place-items: center;
  width: 56px;
  height: 56px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.18);
  font-weight: 800;
  letter-spacing: 1px;
}

.brand-block h2 {
  margin: 0;
  font-size: 22px;
}

.brand-block p {
  margin: 6px 0 0;
  color: rgba(255, 255, 255, 0.72);
  font-size: 13px;
}

.nav-menu {
  border-right: none;
  background: transparent;
}

:deep(.nav-menu .el-menu-item) {
  margin-bottom: 8px;
  border-radius: 14px;
  color: rgba(255, 255, 255, 0.78);
}

:deep(.nav-menu .el-menu-item.is-active) {
  color: #12325f;
  background: #eff5ff;
}

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 28px 32px 8px;
  background: transparent;
}

.topbar-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.topbar h1 {
  margin: 0;
  font-size: 26px;
}

.topbar p {
  margin: 8px 0 0;
  color: var(--text-secondary);
}

.main-panel {
  padding: 16px 32px 32px;
}

@media (max-width: 960px) {
  .aside-panel {
    display: none;
  }

  .topbar,
  .main-panel {
    padding-left: 18px;
    padding-right: 18px;
  }
}
</style>
