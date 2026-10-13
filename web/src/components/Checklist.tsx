import type { Item } from '../types'
import { Inline } from './Inline'

type Props = {
  items: Item[]
  currentId?: string
  locked?: boolean
  onToggle: (item: Item) => void
}

/** [x] / [ ] rendered literally. A box is clickable when it's ticked (to untick)
 *  or when the item has a passing verification; otherwise it explains why not. */
export function Checklist({ items, currentId, locked, onToggle }: Props) {
  return (
    <ul className="checklist">
      {items.map((item) => {
        const canTick = !locked && item.verified
        const enabled = item.checked || canTick
        const title = item.checked
          ? 'Untick'
          : locked
            ? 'Week is locked'
            : item.verified
              ? 'Verified: click to tick'
              : 'Needs a passing verification first'
        return (
          <li key={item.id} className={item.id === currentId ? 'checklist-current' : undefined}>
            <button
              className={`checklist-box ${item.checked ? 'is-checked' : ''} ${canTick && !item.checked ? 'is-ready' : ''}`}
              disabled={!enabled}
              onClick={() => onToggle(item)}
              title={title}
              aria-label={`${item.checked ? 'Untick' : 'Tick'} ${item.id}`}
              aria-pressed={item.checked}
            >
              {item.checked ? '[x]' : '[ ]'}
            </button>
            <span className="checklist-id">[{item.id}]</span>
            <span className="checklist-text"><Inline text={item.text} /></span>
          </li>
        )
      })}
    </ul>
  )
}
