import { defineStore } from 'pinia'

import { getCurrentUser, login, logout, register } from '@/api'

type AuthUser = {
  id: number
  username: string
  nickname?: string
}

const TOKEN_KEY = 'ncre-auth-token'
const USER_KEY = 'ncre-auth-user'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem(TOKEN_KEY) || '',
    user: (() => {
      const raw = localStorage.getItem(USER_KEY)
      return raw ? (JSON.parse(raw) as AuthUser) : null
    })(),
  }),
  getters: {
    isLoggedIn: (state) => Boolean(state.token),
    displayName: (state) => state.user?.nickname || state.user?.username || '未登录',
  },
  actions: {
    persist(token: string, user: AuthUser) {
      this.token = token
      this.user = user
      localStorage.setItem(TOKEN_KEY, token)
      localStorage.setItem(USER_KEY, JSON.stringify(user))
    },
    clear() {
      this.token = ''
      this.user = null
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(USER_KEY)
    },
    async login(payload: { username: string; password: string }) {
      const response = await login(payload)
      this.persist(response.data.token, response.data.user)
      return response
    },
    async register(payload: { username: string; password: string; nickname?: string }) {
      const response = await register(payload)
      this.persist(response.data.token, response.data.user)
      return response
    },
    async fetchMe() {
      if (!this.token) return null
      const response = await getCurrentUser()
      this.user = response.data
      localStorage.setItem(USER_KEY, JSON.stringify(response.data))
      return response.data
    },
    async logout() {
      if (this.token) {
        try {
          await logout()
        } catch {
        }
      }
      this.clear()
    },
  },
})
