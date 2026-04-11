import { useEffect, useMemo, useState } from 'react'
import { Database, Plus, Tag, Search, BookOpen, GraduationCap, Award, Save, X } from 'lucide-react'
import { toast } from 'react-hot-toast'
import Button from '../components/common/Button'
import Input from '../components/common/Input'
import Modal from '../components/common/Modal'
import Skeleton from '../components/common/Skeleton'
import {
  fetchTaxonomyCertifications,
  fetchTaxonomyDegrees,
  fetchTaxonomySkills,
  fetchTaxonomyUniversities,
  type TaxonomyItem,
  type TaxonomySkill,
} from '../services/api/taxonomy'

export default function TaxonomyPage() {
  const [skills, setSkills] = useState<TaxonomySkill[]>([])
  const [fileInputRef, setFileInputRef] = useState<HTMLInputElement | null>(null)
  const [degrees, setDegrees] = useState<TaxonomyItem[]>([])
  const [universities, setUniversities] = useState<TaxonomyItem[]>([])
  const [certifications, setCertifications] = useState<TaxonomyItem[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [addOpen, setAddOpen] = useState(false)
  const [addType, setAddType] = useState<'skill' | 'degree' | 'university' | 'certification'>('skill')
  const [addName, setAddName] = useState('')
  const [addCategory, setAddCategory] = useState('')
  const [addSynonyms, setAddSynonyms] = useState('')

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true)
        const [skillsData, degreeData, universityData, certificationData] =
          await Promise.all([
            fetchTaxonomySkills(),
            fetchTaxonomyDegrees(),
            fetchTaxonomyUniversities(),
            fetchTaxonomyCertifications(),
          ])
        setSkills(skillsData)
        setDegrees(degreeData)
        setUniversities(universityData)
        setCertifications(certificationData)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load taxonomy')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const filteredSkills = useMemo(() => {
    if (!search) return skills
    const term = search.toLowerCase()
    return skills.filter((skill) => {
      return (
        skill.name?.toLowerCase().includes(term) ||
        skill.category?.toLowerCase().includes(term) ||
        skill.synonyms?.toLowerCase().includes(term)
      )
    })
  }, [skills, search])

  const handleAddEntry = () => {
    setAddOpen(true)
  }

  const handleSubmitAdd = () => {
    const name = addName.trim()
    if (!name) {
      toast.error('Name is required')
      return
    }

    if (addType === 'skill') {
      setSkills((prev) => [
        {
          name,
          category: addCategory.trim() || null,
          synonyms: addSynonyms.trim() || null,
          group: null,
        },
        ...prev,
      ])
    } else if (addType === 'degree') {
      setDegrees((prev) => [{ name }, ...prev])
    } else if (addType === 'university') {
      setUniversities((prev) => [{ name }, ...prev])
    } else {
      setCertifications((prev) => [{ name }, ...prev])
    }

    setAddOpen(false)
    setAddName('')
    setAddCategory('')
    setAddSynonyms('')
    toast.success('Entry added to local state')
  }
  
  const handleImportCsv = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = (e) => {
      const text = e.target?.result as string
      if (!text) return

      const lines = text.split('\n')
      const newSkills: TaxonomySkill[] = []
      
      lines.forEach((line, index) => {
        if (index === 0 && (line.toLowerCase().includes('name') || line.toLowerCase().includes('category'))) return
        const [name, category, synonyms] = line.split(',').map(s => s.trim())
        if (name) {
          newSkills.push({
            name,
            category: category || 'MISC',
            synonyms: synonyms || null,
            group: null
          })
        }
      })

      if (newSkills.length > 0) {
        setSkills(prev => [...newSkills, ...prev])
        toast.success(`Imported ${newSkills.length} skills successfully`)
      } else {
        toast.error('No valid skills found in CSV')
      }
      
      // Reset input
      event.target.value = ''
    }
    reader.readAsText(file)
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Search & Actions Bar */}
      <div className="flex flex-col sm:flex-row flex-wrap items-center justify-between gap-4 bg-white p-5 rounded-2xl shadow-xl shadow-slate-200/40 border border-slate-100/50">
        <div className="relative flex-1 min-w-[280px]">
          <Search className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            className="w-full rounded-xl border border-slate-200 bg-slate-50 py-3 pl-11 pr-4 text-sm font-medium outline-none transition-all focus:border-violet-400 focus:bg-white focus:ring-4 focus:ring-violet-50"
            placeholder="Search within taxonomy (Python, Backend, etc.)..."
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </div>
        <button
          onClick={handleAddEntry}
          className="w-full sm:w-auto flex items-center justify-center gap-2 rounded-xl bg-violet-600 px-6 py-3 text-sm font-bold text-white shadow-lg shadow-violet-200 transition-all hover:bg-violet-700 hover:-translate-y-0.5 active:scale-95 uppercase tracking-wider"
        >
          <Plus className="h-4 w-4" />
          Add New Entry
        </button>
      </div>

      <Modal open={addOpen} onClose={() => setAddOpen(false)} title="Add Taxonomy Entry">
        <div className="space-y-5 p-1">
          <div className="space-y-1.5">
            <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest ml-1">Type</label>
            <select
              className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-700 outline-none transition-all focus:border-violet-400 focus:bg-white focus:ring-4 focus:ring-violet-50"
              value={addType}
              onChange={(event) => setAddType(event.target.value as any)}
            >
              <option value="skill">Skill</option>
              <option value="degree">Degree</option>
              <option value="university">University</option>
              <option value="certification">Certification</option>
            </select>
          </div>

          <div className="space-y-1.5">
            <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest ml-1">Name</label>
            <Input
              value={addName}
              onChange={(event) => setAddName(event.target.value)}
              placeholder={addType === 'skill' ? 'e.g. Python' : 'e.g. Master of Science'}
            />
          </div>

          {addType === 'skill' && (
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest ml-1">Category</label>
                <Input
                  value={addCategory}
                  onChange={(event) => setAddCategory(event.target.value)}
                  placeholder="e.g. Programming"
                />
              </div>
              <div className="space-y-1.5">
                <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest ml-1">Synonyms</label>
                <Input
                  value={addSynonyms}
                  onChange={(event) => setAddSynonyms(event.target.value)}
                  placeholder="Comma separated"
                />
              </div>
            </div>
          )}

          <div className="flex justify-end gap-3 pt-4 border-t border-slate-50">
            <button
              onClick={() => setAddOpen(false)}
              className="px-5 py-2.5 rounded-xl text-sm font-bold text-slate-500 hover:bg-slate-50 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSubmitAdd}
              className="flex items-center gap-2 rounded-xl bg-violet-600 px-6 py-2.5 text-sm font-bold text-white shadow-md transition-all hover:bg-violet-700"
            >
              <Save className="h-4 w-4" />
              Save Entry
            </button>
          </div>
        </div>
      </Modal>

      <div className="grid gap-6 lg:grid-cols-[1fr_360px] items-start">
        {/* Main Skills Board */}
        <div className="rounded-2xl bg-white shadow-xl shadow-slate-200/40 border border-slate-100/50 overflow-hidden flex flex-col h-full ring-1 ring-slate-100/50">
          <div className="flex items-center justify-between px-6 py-5 border-b border-slate-50 bg-slate-50/20">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-violet-100 text-violet-600 shadow-sm">
                <Database className="h-5 w-5" />
              </div>
              <div>
                <h3 className="text-[15px] font-bold text-slate-700 tracking-tight">Skills Taxonomy</h3>
                <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-widest">{filteredSkills.length} Total Skills</p>
              </div>
            </div>
            <input
              type="file"
              accept=".csv"
              className="hidden"
              onChange={handleImportCsv}
              ref={(el) => setFileInputRef(el)}
            />
            <button 
              onClick={() => fileInputRef?.click()}
              className="flex items-center gap-2 text-[10px] font-bold text-violet-600 bg-violet-50 px-4 py-2 rounded-xl uppercase tracking-widest hover:bg-violet-600 hover:text-white transition-all shadow-sm"
            >
              <Tag className="h-3.5 w-3.5" />
              Import CSV
            </button>
          </div>

          <div className="flex-1 overflow-y-auto max-h-[calc(100vh-280px)] p-6 bg-slate-50/10 scrollbar-thin scrollbar-thumb-slate-200/60">
            {loading ? (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4"><Skeleton lines={8} /></div>
            ) : error ? (
              <div className="p-12 text-center text-sm font-bold text-red-500 bg-red-50 rounded-2xl mx-6 translate-y-6">{error}</div>
            ) : filteredSkills.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-24 text-center">
                <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-white shadow-lg text-slate-300 mb-4 animate-bounce-slow">
                  <Database className="h-8 w-8" />
                </div>
                <h4 className="text-base font-bold text-slate-600">No skills found</h4>
                <p className="text-xs text-slate-400 mt-1 uppercase tracking-tight">Try refining your search criteria</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 pb-4">
                {filteredSkills.map((skill) => (
                  <div
                    key={`${skill.name}-${skill.category}`}
                    className="group flex flex-col gap-3 rounded-2xl border border-slate-100 bg-white p-4 shadow-sm transition-all duration-300 hover:shadow-xl hover:shadow-indigo-50/50 hover:-translate-y-1 hover:border-violet-200"
                  >
                    <div className="flex items-start justify-between">
                      <h4 className="text-[13px] font-bold text-slate-700 tracking-tight group-hover:text-violet-700 transition-colors">
                        {skill.name ?? 'Unknown'}
                      </h4>
                      <span className="inline-flex rounded-[8px] bg-indigo-50 px-2 py-0.5 text-[8px] font-bold text-violet-600 uppercase tracking-tight shadow-sm ring-1 ring-violet-100/50">
                        {skill.category ?? skill.group ?? 'MISC'}
                      </span>
                    </div>
                    {skill.synonyms && (
                      <p className="text-[11px] text-slate-400 italic leading-snug line-clamp-2">
                        <span className="font-bold uppercase tracking-widest text-[8px] opacity-40 block mb-0.5">Synonyms</span>
                        {skill.synonyms}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Sidebar Lists */}
        <div className="space-y-6 flex flex-col">
          {/* Degrees */}
          <div className="rounded-2xl bg-white p-6 shadow-xl shadow-slate-200/40 border border-slate-100/50 flex flex-col">
            <h3 className="text-[14px] font-black text-slate-800 mb-5 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-violet-100 text-violet-600 shadow-sm border border-violet-200/50">
                  <BookOpen className="h-4 w-4" />
                </div>
                Degrees
              </div>
              <span className="text-[10px] bg-slate-100 text-slate-400 px-2.5 py-1 rounded-lg font-bold tracking-tight">{degrees.length}</span>
            </h3>
            <div className="max-h-[250px] overflow-y-auto pr-1 space-y-2.5 scrollbar-thin scrollbar-thumb-slate-200">
              {loading ? <Skeleton lines={3} /> : (degrees.length ? degrees : [{ name: 'No degrees' }]).map((degree) => (
                <div key={degree.name} className="flex items-center justify-between rounded-xl border border-slate-50 bg-slate-50/50 px-4 py-3 text-xs font-semibold text-slate-500 hover:border-violet-200 hover:bg-white hover:shadow-md transition-all duration-200 hover:-translate-x-0.5">
                  <span className="truncate">{degree.name}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Universities */}
          <div className="rounded-2xl bg-white p-6 shadow-xl shadow-slate-200/40 border border-slate-100/50 flex flex-col">
            <h3 className="text-[14px] font-black text-slate-800 mb-5 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-teal-100 text-teal-600 shadow-sm border border-teal-200/50">
                  <GraduationCap className="h-4 w-4" />
                </div>
                Universities
              </div>
              <span className="text-[10px] bg-slate-100 text-slate-400 px-2.5 py-1 rounded-lg font-bold tracking-tight">{universities.length}</span>
            </h3>
            <div className="max-h-[250px] overflow-y-auto pr-1 space-y-2.5 scrollbar-thin scrollbar-thumb-slate-200">
              {loading ? <Skeleton lines={3} /> : (universities.length ? universities : [{ name: 'No universities' }]).map((uni) => (
                <div key={uni.name} className="flex items-center justify-between rounded-xl border border-slate-50 bg-slate-50/50 px-4 py-3 text-xs font-semibold text-slate-500 hover:border-teal-200 hover:bg-white hover:shadow-md transition-all duration-200 hover:-translate-x-0.5">
                  <span className="truncate">{uni.name}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Certifications */}
          <div className="rounded-2xl bg-white p-6 shadow-xl shadow-slate-200/40 border border-slate-100/50 flex flex-col">
            <h3 className="text-[14px] font-black text-slate-800 mb-5 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-amber-100 text-amber-600 shadow-sm border border-amber-200/50">
                  <Award className="h-4 w-4" />
                </div>
                Certifications
              </div>
              <span className="text-[10px] bg-slate-100 text-slate-400 px-2.5 py-1 rounded-lg font-bold tracking-tight">{certifications.length}</span>
            </h3>
            <div className="max-h-[250px] overflow-y-auto pr-1 space-y-2.5 scrollbar-thin scrollbar-thumb-slate-200">
              {loading ? <Skeleton lines={3} /> : (certifications.length ? certifications : [{ name: 'No certifications' }]).map((cert) => (
                <div key={cert.name} className="flex items-center justify-between rounded-xl border border-slate-50 bg-slate-50/50 px-4 py-3 text-xs font-semibold text-slate-500 hover:border-amber-200 hover:bg-white hover:shadow-md transition-all duration-200 hover:-translate-x-0.5">
                  <span className="truncate">{cert.name}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
