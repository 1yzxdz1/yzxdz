import http from './http'
import type { ApiResponse, Question, Subject, SubjectDetail } from '@/types'

export const register = (payload: Record<string, unknown>) =>
  http.post('/auth/register', payload)

export const login = (payload: Record<string, unknown>) =>
  http.post('/auth/login', payload)

export const getCurrentUser = () => http.get('/auth/me')

export const logout = () => http.post('/auth/logout')

export const getSubjects = () => http.get<never, ApiResponse<Subject[]>>('/subjects')

export const getSubjectDetail = (id: number) =>
  http.get<never, ApiResponse<SubjectDetail>>(`/subjects/${id}`)

export const getChapters = (subjectId?: number) =>
  http.get(`/chapters${subjectId ? `?subject_id=${subjectId}` : ''}`)

export const getQuestions = (params: Record<string, string | number>) =>
  http.get<never, ApiResponse<{ items: Question[]; total: number }>>('/questions', { params })

export const getRandomQuestions = (subjectId: number, count: number) =>
  http.get<never, ApiResponse<{ items: Question[]; total: number }>>('/questions/random', {
    params: { subject_id: subjectId, count },
  })

export const submitPractice = (payload: Record<string, unknown>) =>
  http.post('/practice/submit', payload)

export const generateMockExam = (payload: Record<string, unknown>) =>
  http.post('/mock-exams/generate', payload)

export const submitMockExam = (id: number, payload: Record<string, unknown>) =>
  http.post(`/mock-exams/${id}/submit`, payload)

export const getStatisticsOverview = () => http.get('/statistics/overview')

export const getWrongQuestions = (params?: Record<string, string | number>) =>
  http.get('/wrong-questions', { params })

export const addFavorite = (questionId: number) => http.post('/favorites', { question_id: questionId })

export const removeFavorite = (questionId: number) => http.delete(`/favorites/${questionId}`)
