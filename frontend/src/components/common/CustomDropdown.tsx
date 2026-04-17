import React, { useState, useRef, useEffect } from 'react'
import { ChevronDown, Check } from 'lucide-react'

interface Option {
  label: string
  value: string
  icon?: React.ElementType
  iconColor?: string
}

interface CustomDropdownProps {
  options: Option[]
  value: string
  onChange: (value: string) => void
  placeholder?: string
  className?: string
  icon?: React.ElementType
}

export default function CustomDropdown({
  options,
  value,
  onChange,
  className = '',
  icon: HeaderIcon,
}: CustomDropdownProps) {
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  const selectedOption = options.find((opt) => opt.value === value) || options[0]

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  return (
    <div className={`relative min-w-[160px] ${className}`} ref={dropdownRef}>
      {/* Trigger */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className={`flex w-full items-center justify-between gap-3 rounded-xl border border-slate-100 bg-white px-4 py-2.5 text-xs font-bold transition-all duration-300 hover:border-orange-200 hover:shadow-lg hover:shadow-orange-50/50 ${isOpen ? 'ring-2 ring-orange-100 border-orange-300' : 'shadow-sm shadow-slate-100/50'
          }`}
      >
        <div className="flex items-center gap-2.5 overflow-hidden">
          {HeaderIcon && <HeaderIcon className="h-4 w-4 text-slate-500 flex-shrink-0" />}
          <span className="truncate text-slate-500 uppercase tracking-widest leading-none">
            {selectedOption.label}
          </span>
        </div>
        <ChevronDown
          className={`h-4 w-4 text-slate-500 transition-transform duration-300 flex-shrink-0 ${isOpen ? 'rotate-180 text-orange-500' : ''}`}
        />
      </button>

      {/* Menu */}
      {isOpen && (
        <div className="absolute top-full left-0 mt-2 z-50 w-full min-w-[200px] overflow-hidden rounded-2xl border border-slate-100 bg-white/95 backdrop-blur-xl p-1.5 shadow-2xl shadow-slate-200/50 animate-in fade-in zoom-in-95 slide-in-from-top-2 duration-200">
          <div className="space-y-0.5">
            {options.map((option) => {
              const isSelected = option.value === value
              const Icon = option.icon
              return (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => {
                    onChange(option.value)
                    setIsOpen(false)
                  }}
                  className={`flex w-full items-center justify-between rounded-[10px] px-3 py-2.5 text-left text-[13px] font-bold transition-all duration-200 ${isSelected
                    ? 'bg-orange-50 text-orange-600'
                    : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                    }`}
                >
                  <div className="flex items-center gap-2.5">
                    {Icon && (
                      <div className={`p-1 rounded-md bg-white shadow-sm ring-1 ring-slate-100`}>
                        <Icon className={`h-3.5 w-3.5 ${option.iconColor || 'text-slate-400'}`} />
                      </div>
                    )}
                    <span className="truncate uppercase tracking-tighter italic-placeholder">{option.label}</span>
                  </div>
                  {isSelected && (
                    <div className="flex h-5 w-5 items-center justify-center rounded-full bg-orange-600 shadow-sm shadow-orange-200">
                      <Check className="h-2.5 w-2.5 text-white stroke-[4]" />
                    </div>
                  )}
                </button>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
