import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { scrollToResumeSpan } from '../../hooks/useScrollToField'

export type FieldMapping = {
  id: string
  value: string
  label: string
}

type ResumeViewerWithHighlightsProps = {
  /** Rendered HTML from DOCX (mammoth) or other source */
  html?: string | null
  /** PDF blob URL - shown when html is empty (click-to-highlight not supported for PDF) */
  pdfUrl?: string | null
  /** Shown when both html and pdfUrl are empty */
  emptyMessage?: string
  /** Fields to make clickable in HTML (name, email, phone, location) */
  fieldMappings: FieldMapping[]
  /** Currently active field id */
  activeFieldId: string | null
  /** When user clicks text in resume */
  onFieldClick: (fieldId: string, value: string, label: string) => void
  /** Scroll to this field when selected from right panel */
  scrollToFieldId: string | null
  /** Callback when scroll completed */
  onScrollComplete?: () => void
}

function escapeRegex(str: string): string {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

/** Inject clickable spans into HTML for known field values */
function injectFieldSpans(
  html: string,
  fieldMappings: FieldMapping[],
  activeFieldId: string | null
): string {
  let result = html
  // Sort by value length descending so longer values get replaced first (e.g. full email before substring)
  const sorted = [...fieldMappings].filter((f) => f.value && f.value.trim().length > 2)
  sorted.sort((a, b) => (b.value?.length ?? 0) - (a.value?.length ?? 0))

  for (const { id, value, label } of sorted) {
    const escaped = escapeRegex(value.trim())
    if (!escaped) continue
    const isActive = activeFieldId === id
    const activeClasses =
      'bg-blue-200 border-l-4 border-blue-500 rounded-md pl-1.5 transition-all duration-200'
    const inactiveClasses =
      'bg-yellow-100 border-l-4 border-yellow-400 rounded-md pl-1.5 transition-all duration-200'
    const dynamicClasses = isActive ? activeClasses : inactiveClasses
    const span = `<span data-resume-field="${id}" data-value="${value.replace(/"/g, '&quot;')}" data-label="${label.replace(/"/g, '&quot;')}" class="resume-field-span cursor-pointer px-1 ${dynamicClasses}">${value}</span>`
    const re = new RegExp(escaped.replace(/\s+/g, '\\s*'), 'g')
    result = result.replace(re, span)
  }
  return result
}

export default function ResumeViewerWithHighlights({
  html,
  pdfUrl = null,
  emptyMessage = 'Loading resume…',
  fieldMappings,
  activeFieldId,
  onFieldClick,
  scrollToFieldId,
  onScrollComplete,
}: ResumeViewerWithHighlightsProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [tooltip, setTooltip] = useState<{
    x: number
    y: number
    value: string
    label: string
  } | null>(null)

  const processedHtml = useMemo(() => {
    if (!html) return ''
    return injectFieldSpans(html, fieldMappings, activeFieldId)
  }, [html, fieldMappings, activeFieldId])

  useEffect(() => {
    if (!scrollToFieldId || !containerRef.current) return
    const el = containerRef.current.querySelector(
      `[data-resume-field="${scrollToFieldId}"]`
    ) as HTMLElement | null
    if (el) {
      el.classList.add('resume-field-highlight-animate')
      scrollToResumeSpan(containerRef.current, scrollToFieldId)
      const t = setTimeout(() => {
        el.classList.remove('resume-field-highlight-animate')
        onScrollComplete?.()
      }, 1500)
      return () => clearTimeout(t)
    }
    onScrollComplete?.()
  }, [scrollToFieldId, onScrollComplete])

  const handleClick = useCallback(
    (e: React.MouseEvent<HTMLDivElement>) => {
      const target = (e.target as HTMLElement).closest('[data-resume-field]') as
        | HTMLElement
        | null
      if (!target) {
        setTooltip(null)
        return
      }
      e.preventDefault()
      const fieldId = target.dataset.resumeField ?? ''
      const value = target.dataset.value ?? ''
      const label = target.dataset.label ?? ''
      onFieldClick(fieldId, value, label)
      setTooltip({
        x: e.clientX,
        y: e.clientY,
        value,
        label,
      })
      const hideTooltip = (e: Event) => {
        const target = e.target as HTMLElement
        if (target.closest('[data-resume-tooltip]')) return
        setTooltip(null)
        window.removeEventListener('click', hideTooltip)
        window.removeEventListener('scroll', hideTooltip)
      }
      requestAnimationFrame(() => {
        window.addEventListener('click', hideTooltip)
        window.addEventListener('scroll', hideTooltip)
      })
    },
    [onFieldClick]
  )

  if (pdfUrl && !html) {
    return (
      <div className="flex h-full min-h-[400px] flex-col">
        <p className="mb-2 text-xs text-slate-500">
          PDF viewer: Click-to-highlight works best with DOCX. Use Download to save.
        </p>
        <iframe
          src={pdfUrl}
          className="min-h-[500px] flex-1 rounded-lg border-0"
          title="Resume PDF"
        />
      </div>
    )
  }

  if (!processedHtml) {
    return (
      <div className="flex h-full min-h-[400px] items-center justify-center rounded-lg border border-dashed border-slate-200 bg-slate-50 p-6 text-center text-sm text-slate-500">
        {emptyMessage}
      </div>
    )
  }

  return (
    <div className="relative h-full">
      <div
        ref={containerRef}
        onClick={handleClick}
        className="resume-viewer-content h-full overflow-auto rounded-lg border border-slate-200 bg-white p-6"
      >
        <div
          className="prose prose-slate max-w-none prose-p:text-slate-700 prose-headings:text-slate-900"
          dangerouslySetInnerHTML={{ __html: processedHtml }}
        />
      </div>

      {tooltip && (
        <div
          data-resume-tooltip
          className="pointer-events-none fixed z-50 rounded-lg border border-slate-200 bg-slate-800 px-3 py-2 shadow-lg transition-opacity duration-200"
          style={{
            left: Math.min(Math.max(tooltip.x - 100, 8), window.innerWidth - 220),
            top: Math.max(tooltip.y - 56, 8),
          }}
        >
          <p className="text-sm font-medium text-white">{tooltip.value}</p>
          <p className="text-xs text-slate-300">{tooltip.label}</p>
        </div>
      )}
    </div>
  )
}
