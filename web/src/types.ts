export type Item = { id: string; text: string; checked: boolean; verified: boolean }
export type Task = { id: string; title: string; kind: 'PROJECT' | 'QUIZ' | null; items: Item[] }
export type Week = {
  n: number
  title: string
  focus: string
  pitfalls: string
  unlocked: boolean
  done: number
  total: number
  tasks: Task[]
}
export type Verification = {
  item: string
  kind: 'pytest' | 'quiz' | 'tutor' | 'artifact'
  passed: boolean
  summary: string
  at: string
  by: string
}
export type TrackerData = {
  weeks: Week[]
  completion: { unlocked: boolean; items: Item[] }
  current: { week: number | null; task: string | null; task_title: string; item: Item } | null
  recent: Verification[]
}
