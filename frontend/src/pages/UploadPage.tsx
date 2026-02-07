import { useEffect, useMemo } from 'react'
import { toast } from 'react-hot-toast'
import DragDropZone from '../components/upload/DragDropZone'
import FileValidator from '../components/upload/FileValidator'
import BatchUpload from '../components/upload/BatchUpload'
import UploadHistory from '../components/upload/UploadHistory'
import { useUploadStore } from '../store/uploadStore'

export default function UploadPage() {
  const { queue, addFiles, uploadAll, pollStatuses } = useUploadStore()
  const files = useMemo(() => queue.map((item) => item.file), [queue])

  useEffect(() => {
    const interval = window.setInterval(() => {
      pollStatuses()
    }, 8000)
    return () => window.clearInterval(interval)
  }, [pollStatuses])

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
      addFiles(valid)
    }
  }

  return (
    <section className="space-y-6">
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
    </section>
  )
}
