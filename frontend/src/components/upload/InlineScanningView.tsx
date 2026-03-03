import { useEffect, useState, useMemo } from 'react'
import * as mammoth from 'mammoth'
import { X } from 'lucide-react'
import ResumePreviewSection from '../candidate-detail/ResumePreviewSection'

interface InlineScanningViewProps {
    file: File
    isProcessing: boolean
    onClose: () => void
}

export default function InlineScanningView({ file, isProcessing, onClose }: InlineScanningViewProps) {
    const [pdfUrl, setPdfUrl] = useState<string | null>(null)
    const [docxHtml, setDocxHtml] = useState<string | null>(null)
    const [error, setError] = useState<string | null>(null)

    const filename = file.name
    const ext = useMemo(() => filename.split('.').pop()?.toLowerCase() || '', [filename])

    useEffect(() => {
        let active = true
        const loadPreview = async () => {
            try {
                if (ext === 'doc') {
                    setError('Preview not supported for this file type.')
                    return
                }

                if (ext === 'docx') {
                    const buf = await file.arrayBuffer()
                    const result = await mammoth.convertToHtml({ arrayBuffer: buf })
                    if (active) setDocxHtml(result.value)
                    return
                }

                if (ext === 'pdf') {
                    const url = URL.createObjectURL(file)
                    if (active) setPdfUrl(url)
                    return
                }

                setError('Preview unavailable for this format.')
            } catch (err) {
                if (active) setError('Failed to load preview.')
            }
        }

        loadPreview()
        return () => {
            active = false
            if (pdfUrl) URL.revokeObjectURL(pdfUrl)
        }
    }, [file, ext])

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center">
            {/* Background Overlay Layer - Only this blurs */}
            <div className="absolute inset-0 bg-white/40 backdrop-blur-md z-0" />

            {/* Centered Resume Container - Kept perfectly sharp */}
            <div className="relative z-50 w-full max-w-4xl h-[90vh] transition-transform duration-500 transform scale-[1.08] flex flex-col items-center justify-center opacity-100">

                {/* Resume Page with strong Shadow and sharp borders */}
                <div className="relative w-full h-full bg-white rounded-xl shadow-[0_20px_60px_-15px_rgba(0,0,0,0.3)] overflow-hidden ring-1 ring-slate-200">
                    <div className="h-full overflow-auto scrollbar-hide bg-white">
                        <ResumePreviewSection
                            pdfUrl={pdfUrl}
                            docxHtml={docxHtml}
                            error={error}
                            filename={filename}
                            hideHeader={true}
                        />
                    </div>

                    {/* Premium Scanning Animation Overlay */}
                    {isProcessing && (
                        <div className="pointer-events-none absolute inset-0 z-[100]">
                            {/* Scanning Indicator Text */}
                            <div className="absolute top-6 left-1/2 -translate-x-1/2 px-4 py-1.5 bg-brand-600 text-white text-[10px] font-bold tracking-[0.2em] uppercase rounded-full shadow-lg z-50">
                                Scanning Resume
                            </div>

                            {/* The Scanning Line - Vertical Bar */}
                            <div
                                className="absolute top-0 h-full w-[4px] bg-brand-500 shadow-[0_0_30px_8px_rgba(37,99,235,0.7)] animate-scan z-40"
                                style={{ left: '-10%' }}
                            >
                                {/* Glow and gradient trailing the line */}
                                <div className="absolute right-0 top-0 h-full w-[500px] bg-gradient-to-l from-brand-500/20 via-brand-500/5 to-transparent" />
                            </div>

                            {/* Subtle dark overlay for contrast against the scanner bar */}
                            <div className="absolute inset-0 bg-slate-900/[0.03] pointer-events-none z-30" />
                        </div>
                    )}
                </div>

                {/* Close action */}
                <button
                    onClick={onClose}
                    className="absolute -top-12 right-0 p-2 text-slate-500 hover:text-slate-800 transition-colors bg-white/80 hover:bg-white rounded-full shadow-sm z-[60]"
                    title="Close preview"
                >
                    <X className="h-6 w-6" />
                </button>
            </div>
        </div>
    )
}
