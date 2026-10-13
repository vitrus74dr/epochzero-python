import { useState } from 'react'
import type { TreeNode } from '../api'

type Props = {
  nodes: TreeNode[]
  current: string | null
  onOpen: (path: string) => void
}

function Node({ node, depth, current, onOpen }: { node: TreeNode; depth: number } & Omit<Props, 'nodes'>) {
  const [open, setOpen] = useState(() => current?.startsWith(node.path + '/') ?? depth === 0)
  const pad = { paddingLeft: `${depth * 2 + 1}ch` }
  if (node.type === 'dir') {
    return (
      <li>
        <button className="tree-row tree-dir" style={pad} onClick={() => setOpen(!open)}
                aria-expanded={open}>
          <span className="tree-glyph">{open ? '▾' : '▸'}</span> {node.name}/
        </button>
        {open && node.children && node.children.length > 0 && (
          <ul>{node.children.map((c) => (
            <Node key={c.path} node={c} depth={depth + 1} current={current} onOpen={onOpen} />
          ))}</ul>
        )}
      </li>
    )
  }
  const active = node.path === current
  return (
    <li>
      <button className={`tree-row tree-file ${active ? 'is-active' : ''}`} style={pad}
              onClick={() => onOpen(node.path)} aria-current={active ? 'true' : undefined}>
        <span className="tree-glyph">{node.name.endsWith('.py') ? '·' : ' '}</span> {node.name}
      </button>
    </li>
  )
}

export function FileTree({ nodes, current, onOpen }: Props) {
  if (nodes.length === 0) {
    return <p className="muted tree-empty">workspace/ is empty.</p>
  }
  return (
    <ul className="tree">
      {nodes.map((n) => <Node key={n.path} node={n} depth={0} current={current} onOpen={onOpen} />)}
    </ul>
  )
}
