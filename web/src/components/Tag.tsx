export type TagKind = 'pass' | 'fail' | 'locked' | 'quiz' | 'project' | 'accent'

/** Bracketed mono tag, e.g. [ PASS ]. */
export function Tag({ kind, children }: { kind: TagKind; children?: string }) {
  const label = (children ?? kind).toUpperCase()
  return <span className={`tag tag--${kind}`}>[ {label} ]</span>
}
