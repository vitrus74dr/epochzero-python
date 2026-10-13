export type VerifyKind = 'pytest' | 'quiz' | 'tutor' | 'artifact'
/** `verify` is the only kind of record that can verify this item. */
export type Item = { id: string; text: string; checked: boolean; verified: boolean; verify: VerifyKind }
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
  kind: VerifyKind
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

export type TestCase = {
  id: string
  name: string
  classname: string
  outcome: 'passed' | 'failed' | 'error' | 'skipped'
  message: string
  detail: string
  time: number
}
export type TestResult = {
  passed: boolean
  summary: string
  counts: Record<'passed' | 'failed' | 'error' | 'skipped', number>
  tests: TestCase[]
  exit_code: number | null
  record: Verification | null
  error: string | null
}
export type TestEvent =
  | { type: 'start'; argv: string[]; cwd: string; item: string | null }
  | { type: 'output'; data: string }
  | ({ type: 'result' } & TestResult)

export type Attempt = { score: number; total: number; pass_mark: number; passed: boolean; at: string; by: string }
export type QuizSummary = {
  id: string
  title: string
  item: string | null
  unlocked: boolean
  questions: number
  pass_mark: number
  last: Attempt | null
  problem: string | null
}
export type QuizList = { quizzes: QuizSummary[]; errors: { file: string; error: string }[] }
export type QuizSpec = {
  id: string
  title: string
  pass_mark: number
  questions: { id: string; prompt: string; choices: string[] }[]
}
export type QuizResult = {
  item: string
  score: number
  total: number
  pass_mark: number
  passed: boolean
  at: string
  results: { id: string; choice: number; correct: boolean; explain: string }[]
}
