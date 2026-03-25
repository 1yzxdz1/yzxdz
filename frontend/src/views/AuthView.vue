<template>
  <div class="auth-page">
    <div class="auth-shell page-card">
      <div class="auth-hero">
        <div class="hero-badge">NCRE</div>
        <h1>全国计算机等级考试复习平台</h1>
        <p>登录后即可拥有独立的学习记录、错题本、收藏夹和模拟考试成绩。</p>
      </div>

      <div class="auth-form">
        <el-tabs v-model="activeTab" stretch>
          <el-tab-pane label="登录" name="login">
            <el-form @submit.prevent>
              <el-form-item label="用户名">
                <el-input v-model="loginForm.username" placeholder="请输入用户名" />
              </el-form-item>
              <el-form-item label="密码">
                <el-input v-model="loginForm.password" type="password" show-password placeholder="请输入密码" />
              </el-form-item>
              <el-button type="primary" size="large" class="full-btn" @click="handleLogin">登录</el-button>
              <el-alert
                title="没有账号也没关系，直接注册后即可拥有独立学习空间"
                type="info"
                :closable="false"
                show-icon
              />
            </el-form>
          </el-tab-pane>

          <el-tab-pane label="注册" name="register">
            <el-form @submit.prevent>
              <el-form-item label="用户名">
                <el-input v-model="registerForm.username" placeholder="3-50 位用户名" />
              </el-form-item>
              <el-form-item label="昵称">
                <el-input v-model="registerForm.nickname" placeholder="可选，展示名" />
              </el-form-item>
              <el-form-item label="密码">
                <el-input v-model="registerForm.password" type="password" show-password placeholder="至少 6 位" />
              </el-form-item>
              <el-button type="primary" size="large" class="full-btn" @click="handleRegister">注册并进入</el-button>
            </el-form>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const activeTab = ref<'login' | 'register'>('login')
const loginForm = ref({
  username: '',
  password: '',
})
const registerForm = ref({
  username: '',
  nickname: '',
  password: '',
})

const handleLogin = async () => {
  try {
    await authStore.login(loginForm.value)
    ElMessage.success('登录成功')
    router.push('/')
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.message || '登录失败')
  }
}

const handleRegister = async () => {
  try {
    await authStore.register(registerForm.value)
    ElMessage.success('注册成功，已为你创建独立学习空间')
    router.push('/')
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.message || '注册失败')
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
  background: radial-gradient(circle at top, #e8f0ff 0%, #f4f7fc 50%, #ecf2fb 100%);
}

.auth-shell {
  width: min(1080px, 100%);
  display: grid;
  grid-template-columns: 1.15fr 0.85fr;
  overflow: hidden;
}

.auth-hero {
  padding: 56px;
  background: linear-gradient(160deg, #173f78 0%, #12325f 100%);
  color: #fff;
}

.hero-badge {
  width: 72px;
  height: 72px;
  border-radius: 22px;
  display: grid;
  place-items: center;
  background: rgba(255, 255, 255, 0.15);
  font-size: 24px;
  font-weight: 800;
}

.auth-hero h1 {
  margin: 24px 0 14px;
  font-size: 36px;
  line-height: 1.3;
}

.auth-hero p {
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.8;
}

.auth-form {
  padding: 44px;
  background: #fff;
}

.full-btn {
  width: 100%;
  margin-bottom: 16px;
}

@media (max-width: 960px) {
  .auth-shell {
    grid-template-columns: 1fr;
  }

  .auth-hero,
  .auth-form {
    padding: 28px;
  }
}
</style>
