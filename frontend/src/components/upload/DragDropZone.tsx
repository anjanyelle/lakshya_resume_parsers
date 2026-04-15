import { useCallback, useState } from 'react'
import { FileText } from 'lucide-react'

type DragDropZoneProps = {
  onFilesSelected: (files: File[]) => void
}

export default function DragDropZone({ onFilesSelected }: DragDropZoneProps) {
  const [isDragging, setIsDragging] = useState(false)

  const handleFiles = useCallback(
    (fileList: FileList | null) => {
      if (!fileList) return
      onFilesSelected(Array.from(fileList))
    },
    [onFilesSelected],
  )

  return (
    <label
      className={`flex cursor-pointer flex-col items-center justify-center rounded-[2rem] border-2 border-dashed p-10 text-center transition-all duration-500 ${isDragging ? 'border-orange-500 bg-orange-50 shadow-orange-100' : 'border-slate-200 bg-white hover:border-orange-300 hover:bg-orange-50/20'
        }`}
      onDragOver={(event) => {
        event.preventDefault()
        setIsDragging(true)
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={(event) => {
        event.preventDefault()
        setIsDragging(false)
        handleFiles(event.dataTransfer.files)
      }}
    >
      <input
        type="file"
        className="hidden"
        multiple
        onChange={(event) => handleFiles(event.target.files)}
      />

      <div className="flex flex-col items-center justify-center text-center group">
        <div className="mb-6 relative transition-transform duration-500 group-hover:scale-110">
          <div className="flex h-16 w-16 items-center justify-center rounded-[1.2rem] bg-orange-50 dark:bg-orange-950/20 shadow-sm border border-orange-100/50">
            <FileText className="h-8 w-8 text-slate-300 dark:text-slate-600" />
          </div>
        </div>

        <h3 className="text-xl font-bold text-slate-700 dark:text-slate-100 tracking-tight mb-2">
          Upload Your Resume
        </h3>

        <p className="text-[14px] text-slate-400 dark:text-slate-500 font-medium max-w-sm mb-6 leading-relaxed">
          Drag & drop or click to browse<br />
          PDF, DOC, DOCX — Max 5MB
        </p>

        <span className="text-[14px] font-bold text-orange-500 group-hover:text-orange-600 transition-colors">
          Browse Files
        </span>
      </div>
    </label>
  )
}
