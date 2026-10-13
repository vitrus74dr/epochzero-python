/** Block-character progress: ▰▰▰▰▱▱▱▱ 50% */
export function Progress({ value, width = 8 }: { value: number; width?: number }) {
  const v = Math.min(1, Math.max(0, value))
  const on = Math.round(v * width)
  const pct = Math.round(v * 100)
  return (
    <span className="progress" role="progressbar" aria-valuenow={pct}
          aria-valuemin={0} aria-valuemax={100}>
      <span className="progress-on">{'▰'.repeat(on)}</span>
      <span className="progress-off">{'▱'.repeat(width - on)}</span>
      {` ${String(pct).padStart(3)}%`}
    </span>
  )
}
