export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

export interface Subject {
  id: number
  level: string
  name: string
  code: string
  exam_duration_minutes: number
  description?: string
}

export interface SubjectDetail extends Subject {
  recommended_path?: string
  chapters: Array<{
    id: number
    code?: string
    title: string
    outline?: string
    sort_order: number
    estimated_minutes: number
  }>
  statistics: Record<string, number>
  papers: PastPaperSummary[]
}

export interface PastPaperSummary {
  id: number
  code: string
  year: number
  season: string
  title: string
  total_questions: number
  total_score: number
  duration_minutes: number
}

export interface PastPaperDetail extends PastPaperSummary {
  subject_id: number
  source_type: string
  description?: string
  questions: Array<{
    sort_order: number
    section_name?: string
    score: number
    question: Question
  }>
}

export interface Question {
  id: number
  subject_id: number
  chapter_id?: number
  chapter: string
  question_type: string
  stem: string
  options?: Array<{ key: string; text: string }>
  answer: string[]
  explanation?: string
  difficulty: string
  tags: string[]
  score: number
  is_favorite: boolean
}
