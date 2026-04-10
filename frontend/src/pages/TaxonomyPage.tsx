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

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Search & Actions Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-white p-4 rounded-xl shadow-card border border-slate-100">
        <div className="relative flex-1 min-w-[240px]">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            className="w-full rounded-xl border border-slate-200 bg-slate-50 py-2.5 pl-10 pr-4 text-sm outline-none transition-all focus:border-violet-400 focus:bg-white focus:ring-2 focus:ring-violet-100"
            placeholder="Search within taxonomy..."
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </div>
        <div className="flex items-center gap-2">
           <button 
             onClick={handleAddEntry}
             className="flex items-center gap-2 rounded-xl bg-violet-600 px-4 py-2.5 text-sm font-bold text-white shadow-md transition-all hover:bg-violet-700 hover:shadow-lg active:scale-95"
           >
            <Plus className="h-4 w-4" />
            Add New Entry
          </button>
        </div>
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

      <div className="grid gap-6 lg:grid-cols-[1fr_340px]">
        {/* Main Skills Card */}
        <div className="rounded-xl bg-white shadow-card border border-slate-100 overflow-hidden flex flex-col">
          <div className="flex items-center justify-between px-6 py-4 border-b border-slate-50 bg-slate-50/30">
            <div className="flex items-center gap-2">
              <Database className="h-4 w-4 text-violet-600" />
              <h3 className="text-sm font-bold text-slate-800">Skills Taxonomy</h3>
            </div>
            <button className="flex items-center gap-1.5 text-[10px] font-bold text-violet-600 bg-violet-50 px-3 py-1 rounded-full uppercase tracking-widest hover:bg-violet-600 hover:text-white transition-all">
              <Tag className="h-3 w-3" />
              Import CSV
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="bg-slate-50/50 text-[11px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-100">
                  <th className="px-6 py-3">Skill Name</th>
                  <th className="px-6 py-3">Category</th>
                  <th className="px-6 py-3">Synonyms</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {loading ? (
                  <tr>
                    <td colSpan={3} className="px-6 py-8"><Skeleton lines={4} /></td>
                  </tr>
                ) : error ? (
                  <tr>
                    <td colSpan={3} className="px-6 py-8 text-center text-sm text-red-500">{error}</td>
                  </tr>
                ) : filteredSkills.length === 0 ? (
                  <tr>
                    <td colSpan={3} className="px-6 py-20 text-center">
                       <div className="flex flex-col items-center justify-center opacity-40">
                         <Database className="h-10 w-10 text-slate-400 mb-2" />
                         <p className="text-sm text-slate-500">No skills matching your search</p>
                       </div>
                    </td>
                  </tr>
                ) : (
                  filteredSkills.map((skill) => (
                    <tr
                      key={`${skill.name}-${skill.category}`}
                      className="transition-colors hover:bg-violet-50/30"
                    >
                      <td className="px-6 py-4">
                        <span className="text-sm font-bold text-slate-700">{skill.name ?? 'Unknown'}</span>
                      </td>
                      <td className="px-6 py-4">
                        <span className="inline-flex rounded-lg bg-teal-50 px-2 py-0.5 text-[10px] font-bold text-teal-600 uppercase tracking-tight">
                          {skill.category ?? skill.group ?? 'Uncategorized'}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span className="text-xs text-slate-500 italic max-w-xs truncate block">
                          {skill.synonyms || '—'}
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Sidebar Lists */}
        <div className="space-y-6 flex flex-col">
          {/* Degrees */}
          <div className="rounded-xl bg-white p-6 shadow-card border border-slate-100">
            <h3 className="text-sm font-bold text-slate-800 mb-4 flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-violet-50 text-violet-600">
                <BookOpen className="h-4 w-4" />
              </div>
              Degrees
            </h3>
            <div className="max-h-[300px] overflow-y-auto pr-1 space-y-2 scrollbar-thin scrollbar-thumb-slate-100">
              {loading ? <Skeleton lines={3} /> : (degrees.length ? degrees : [{ name: 'No degrees' }]).map((degree) => (
                <div key={degree.name} className="flex items-center justify-between rounded-xl border border-slate-100 bg-slate-50/50 px-3 py-2.5 text-xs font-semibold text-slate-600 hover:border-violet-200 transition-colors">
                  <span className="truncate">{degree.name}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Universities */}
          <div className="rounded-xl bg-white p-6 shadow-card border border-slate-100">
            <h3 className="text-sm font-bold text-slate-800 mb-4 flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-teal-50 text-teal-600">
                <GraduationCap className="h-4 w-4" />
              </div>
              Universities
            </h3>
            <div className="max-h-[300px] overflow-y-auto pr-1 space-y-2 scrollbar-thin scrollbar-thumb-slate-100">
              {loading ? <Skeleton lines={3} /> : (universities.length ? universities : [{ name: 'No universities' }]).map((uni) => (
                <div key={uni.name} className="flex items-center justify-between rounded-xl border border-slate-100 bg-slate-50/50 px-3 py-2.5 text-xs font-semibold text-slate-600 hover:border-teal-200 transition-colors">
                  <span className="truncate">{uni.name}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Certifications */}
          <div className="rounded-xl bg-white p-6 shadow-card border border-slate-100">
            <h3 className="text-sm font-bold text-slate-800 mb-4 flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-50 text-amber-600">
                <Award className="h-4 w-4" />
              </div>
              Certifications
            </h3>
            <div className="max-h-[300px] overflow-y-auto pr-1 space-y-2 scrollbar-thin scrollbar-thumb-slate-100">
              {loading ? <Skeleton lines={3} /> : (certifications.length ? certifications : [{ name: 'No certifications' }]).map((cert) => (
                <div key={cert.name} className="flex items-center justify-between rounded-xl border border-slate-100 bg-slate-50/50 px-3 py-2.5 text-xs font-semibold text-slate-600 hover:border-amber-200 transition-colors">
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
