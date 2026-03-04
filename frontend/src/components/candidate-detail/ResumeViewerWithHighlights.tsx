import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { scrollToResumeSpan } from '../../hooks/useScrollToField'

export type FieldMapping = {
  id: string
  value: string
  label: string
  type?: 'personal' | 'skills' | 'experience' | 'education' | 'contact'
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
  activeFieldId: string | null,
): string {
  let result = html
  
  // Ensure HTML is not double-escaped
  if (result.includes('&lt;') || result.includes('&gt;')) {
    // Unescape HTML if it's already escaped
    result = result.replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&')
  }
  
  // Sort by value length descending so longer values get replaced first (e.g. full email before substring)
  const sorted = [...fieldMappings].filter((f) => f.value && f.value.trim().length > 2)
  sorted.sort((a, b) => (b.value?.length ?? 0) - (a.value?.length ?? 0))

  // Process each field type separately to avoid cross-type overlaps
  const fieldTypes = ['personal', 'skills', 'experience', 'education', 'contact', 'default']
  
  for (const fieldType of fieldTypes) {
    const fieldsByType = sorted.filter(f => (f.type || 'default') === fieldType)
    
    for (const { id, value, label, type } of fieldsByType) {
      const cleanValue = value.trim()
      if (!cleanValue) continue
      
      const isActive = activeFieldId === id
      
      // Define color schemes for different field types
      const fieldColors = {
        personal: {
          active: 'bg-orange-50 border-l-4 border-orange-300 rounded-md pl-1.5 transition-all duration-200',
          inactive: 'bg-orange-50 border-l-4 border-orange-300 rounded-md pl-1.5 transition-all duration-200'
        },
        skills: {
          active: 'bg-blue-50 border-l-4 border-blue-300 rounded-md pl-1.5 transition-all duration-200',
          inactive: 'bg-blue-50 border-l-4 border-blue-300 rounded-md pl-1.5 transition-all duration-200'
        },
        experience: {
          active: 'bg-green-200 border-l-4 border-green-500 rounded-md pl-1.5 transition-all duration-200',
          inactive: 'bg-green-100 border-l-4 border-green-400 rounded-md pl-1.5 transition-all duration-200'
        },
        education: {
          active: 'bg-yellow-50 border-l-4 border-yellow-300 rounded-md pl-1.5 transition-all duration-200',
          inactive: 'bg-yellow-50 border-l-4 border-yellow-300 rounded-md pl-1.5 transition-all duration-200'
        },
        contact: {
          active: 'bg-pink-200 border-l-4 border-pink-500 rounded-md pl-1.5 transition-all duration-200',
          inactive: 'bg-pink-100 border-l-4 border-pink-400 rounded-md pl-1.5 transition-all duration-200'
        },
        default: {
          active: 'bg-blue-200 border-l-4 border-blue-500 rounded-md pl-1.5 transition-all duration-200',
          inactive: 'bg-yellow-100 border-l-4 border-yellow-400 rounded-md pl-1.5 transition-all duration-200'
        }
      }
      
      // Get color scheme for field type, fallback to default
      const colorScheme = fieldColors[type || 'default']
      const { active: activeClasses, inactive: inactiveClasses } = colorScheme
      
      const dynamicClasses = isActive ? activeClasses : inactiveClasses
      
      // Create clean span with proper attributes
      const span = `<span data-resume-field="${id}" data-value="${value.replace(/"/g, '&quot;')}" data-label="${label.replace(/"/g, '&quot;')}" data-field-type="${type || 'default'}" class="resume-field-span cursor-pointer px-1 ${dynamicClasses}">${value}</span>`
      
      // Strict regex that matches complete standalone words only
      const escaped = escapeRegex(cleanValue)
      
      // Use word boundaries with context checking to prevent partial matches
      // This approach checks character before and after to ensure complete word matching
      const wordBoundaryRegex = new RegExp(`\\b${escaped}\\b`, 'gi')
      
      // Phrase-based matching to prevent partial matches completely
      const phrasesToMatch = cleanValue.split(' ').filter(p => p.trim().length > 0)
      phrasesToMatch.sort((a, b) => b.length - a.length)
      
      // Match each phrase separately with strict word boundaries
      for (const phrase of phrasesToMatch) {
        const phraseRegex = new RegExp(`\\b${escapeRegex(phrase)}\\b`, 'gi')
        
        result = result.replace(phraseRegex, (match) => {
          // Check character context to ensure proper word boundaries
          const matchIndex = result.indexOf(match)
          const beforeChar = matchIndex > 0 ? result[matchIndex - 1] : ' '
          const afterChar = result[matchIndex + match.length]
          
          // Only highlight if properly surrounded by word boundaries
          const isProperBoundary = (
            (beforeChar === undefined || beforeChar === ' ' || beforeChar === '\n' || beforeChar === '\t' || beforeChar === '.' || beforeChar === ',' || beforeChar === ';' || beforeChar === '(' || beforeChar === '[') &&
            (afterChar === undefined || afterChar === ' ' || afterChar === '\n' || afterChar === '\t' || afterChar === '.' || afterChar === ',' || afterChar === ';' || afterChar === ')' || afterChar === ']')
          )
          
          if (!isProperBoundary) {
            return match // Don't highlight partial matches
          }
          
          // Check if already inside a span
          const beforeMatch = result.substring(0, matchIndex)
          const openSpans = (beforeMatch.match(/<span/g) || []).length
          const closeSpans = (beforeMatch.match(/<\/span>/g) || []).length
          
          // If we're inside an unclosed span, don't replace
          if (openSpans > closeSpans) {
            return match
          }
          
          return span
        })
      }
    }
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
    
    // Always return html to prevent blank page
    if (!html || html.trim() === '') return html
    
    // Debug: log the input
    if (import.meta.env.DEV) {
      console.log('[ResumeViewer] Input HTML:', html?.substring(0, 200))
      console.log('[ResumeViewer] FieldMappings count:', fieldMappings.length)
    }
    
    // Only highlight if we have fieldMappings (important skills)
    if (fieldMappings.length === 0) return html
    
    // Highlight important skills with appropriate colors while preserving HTML structure
    let highlightedHtml = html
    
    try {
      for (const { value, type } of fieldMappings) {
        const skillName = value.trim()
        if (skillName.length > 2) {
          // Create regex for exact phrase matching only (no partial matches)
          const escapedSkill = skillName.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
          // Match exact phrase with word boundaries, but not partial matches within larger phrases
          const regex = new RegExp(`\\b${escapedSkill}\\b`, 'gi')
          highlightedHtml = highlightedHtml.replace(regex, (match) => {
            // Skip if already wrapped in mark tag to prevent double highlighting
            if (match.includes('data-resume-field') || match.includes('style=')) {
              return match
            }
            
            // Set color based on field type
            let bgColor = '#eff6ff' // Default light blue
            let textColor = '#1e40af' // Default blue text
            
            if (type === 'education') {
              bgColor = '#fef3c7' // Light yellow
              textColor = '#92400e' // Yellow text
            } else if (type === 'personal') {
              bgColor = '#dcfce7' // Light green
              textColor = '#166534' // Green text
            } else if (type === 'skills') {
              bgColor = '#eff6ff' // Light blue
              textColor = '#1e40af' // Blue text
            } else if (type === 'experience') {
              bgColor = '#f3e8ff' // Light purple
              textColor = '#6b21a8' // Purple text
            }
            
            return `<mark data-resume-field="${type}" data-value="${value}" data-field-type="${type}" style="background-color: ${bgColor}; color: ${textColor}; padding: 2px 4px; border-radius: 3px; cursor: pointer;">${match}</mark>`
          })
        }
      }
    } catch (error) {
      console.error('[ResumeViewer] Error in highlighting:', error)
      return html // Return original HTML on error
    }
    
    return highlightedHtml
  }, [html, fieldMappings])

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
    (e: React.MouseEvent) => {
      const target = e.target as HTMLElement
      const markElement = target.closest('mark') as HTMLElement | null
      if (markElement) {
        e.preventDefault()
        
        // Get the field type from the mark element's parent or data
        const fieldType = markElement.getAttribute('data-field-type') || 'skills'
        const fieldId = markElement.getAttribute('data-resume-field') || 'skills'
        const value = markElement.textContent || ''
        
        // Navigate to appropriate section based on field type
        if (fieldType === 'skills' || fieldId.includes('skill')) {
          onFieldClick('skills', value, 'Skills') // Go to skills section
        } else if (fieldType === 'personal' && fieldId === 'location') {
          onFieldClick('work_history', value, 'Experience') // Go to work history section for locations
        } else if (fieldType === 'personal') {
          onFieldClick('full_name', value, 'Candidate Details') // Go to candidate details section
        } else if (fieldType === 'experience') {
          onFieldClick('work_history', value, 'Experience') // Go to work history section
        } else if (fieldType === 'education') {
          onFieldClick('education', value, 'Education') // Go to education section
        }
      }
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
