import ReactMarkdown from 'react-markdown'
import rehypeHighlight from 'rehype-highlight'
import remarkGfm from 'remark-gfm'

/** Rendered markdown for plans, walkthroughs and (later) lessons. Raw HTML is
 *  not rendered. Syntax colours come from tokens via the .hljs-* rules in app.css. */
export function Markdown({ text, compact }: { text: string; compact?: boolean }) {
  return (
    <div className={compact ? 'md md-compact' : 'md'}>
      <ReactMarkdown remarkPlugins={[remarkGfm]}
                     rehypePlugins={[[rehypeHighlight, { detect: false, ignoreMissing: true }]]}
                     components={{ a: ({ href, children }) => (
                       <a href={href} target={href?.startsWith('#') ? undefined : '_blank'}
                          rel="noreferrer">{children}</a>
                     ) }}>
        {text}
      </ReactMarkdown>
    </div>
  )
}
