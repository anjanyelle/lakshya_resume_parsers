import { useEffect, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'react-hot-toast'
import DragDropZone from '../components/upload/DragDropZone'
import FileValidator from '../components/upload/FileValidator'
import BatchUpload from '../components/upload/BatchUpload'
import UploadHistory from '../components/upload/UploadHistory'
import InlineScanningView from '../components/upload/InlineScanningView'
import { useUploadStore } from '../store/uploadStore'

export default function UploadPage() {
  const navigate = useNavigate()
  const { queue, addFiles, uploadAll, pollStatuses, activePreviewId, setActivePreviewId } = useUploadStore()

  const files = useMemo(() => queue.map((item) => item.file), [queue])
  const activeItem = useMemo(() => queue.find(it => it.id === activePreviewId), [queue, activePreviewId])

  useEffect(() => {
    const interval = window.setInterval(() => {
      pollStatuses()
    }, 3000)
    return () => window.clearInterval(interval)
  }, [pollStatuses])

  useEffect(() => {
    if (activeItem?.status === 'success' && activeItem.jobId) {
      toast.success('Resume processed successfully!')
      setActivePreviewId(null)
      navigate('/candidates')
    }
  }, [activeItem?.status, activeItem?.jobId, navigate, setActivePreviewId])

  const handleFilesSelected = (selected: File[]) => {
    const allowed = [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'text/plain',
      'application/rtf',
    ]
    const maxBytes = 10 * 1024 * 1024
    const valid = selected.filter(
      (file) => allowed.includes(file.type) && file.size <= maxBytes,
    )

    if (valid.length !== selected.length) {
      toast.error('Some files were rejected due to type or size')
    }

    if (valid.length) {
      const newItems = addFiles(valid)
      if (newItems.length > 0) {
        setActivePreviewId(newItems[0].id)
        uploadAll()
      }
    }
  }

  return (
    <section className="space-y-6">
      {activeItem && (
        <div className="flex justify-center items-start pt-4">
          <div className="w-full max-w-5xl h-[calc(100vh-16rem)] min-h-[700px]">
            <InlineScanningView
              file={activeItem.file}
              isProcessing={activeItem.status === 'uploading' || activeItem.status === 'processing'}
              onClose={() => setActivePreviewId(null)}
            />
          </div>
        </div>
      )}

      {!activeItem && (
        <>
          <div>
            <h1 className="text-2xl font-semibold text-slate-900">
              Upload resumes
            </h1>
            <p className="mt-2 text-sm text-slate-600">
              Drag, drop, and manage resume uploads in one place.
            </p>
          </div>

          <DragDropZone onFilesSelected={handleFilesSelected} />
          <FileValidator files={files} />

          <div className="grid gap-6 lg:grid-cols-[2fr,1fr]">
            <BatchUpload queue={queue} onUpload={uploadAll} />
            <UploadHistory items={queue} />
          </div>
        </>
      )}
    </section>
  )
}
