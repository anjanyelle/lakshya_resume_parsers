import { useState, useMemo, useEffect } from 'react'
import { Plus, X, Edit2, Check } from 'lucide-react'
import type { CandidateSkill, Skill } from '../../types/candidate'

type SkillsSectionProps = {
  skills?: Skill[]
  candidateSkills?: CandidateSkill[]
  onUpdate?: (skills: Skill[]) => void
}

const SUGGESTED_SKILLS_LIST = [
  'Selenium IDE', 'Selenium RC', 'POM', 'Cucumber', 'Selenium Webdriver',
  'JUnit', 'Webdriver', 'Bdd', 'Rest Assured', 'Selenium Grid'
]

const ALL_SKILLS_DATABASE = [
  'Java', 'Core Java', 'Javascript', 'J2Ee', 'Japanese', 'Spring Boot',
  'React.js', 'MySQL', 'Python', 'Machine Learning', 'Docker', 'Kubernetes'
]

export default function SkillsSection({
  skills: initialSkills = [],
  onUpdate,
}: SkillsSectionProps) {
  const [editing, setEditing] = useState(false)
  const [skills, setSkills] = useState<Skill[]>(initialSkills)
  const [newSkill, setNewSkill] = useState('')
  const [suggestedSkills, setSuggestedSkills] = useState(SUGGESTED_SKILLS_LIST)
  const [showDropdown, setShowDropdown] = useState(false)

  const filteredDatabase = useMemo(() => {
    if (!newSkill.trim()) return []
    return ALL_SKILLS_DATABASE.filter(s =>
      s.toLowerCase().includes(newSkill.toLowerCase()) &&
      !skills.some(active => active.name.toLowerCase() === s.toLowerCase())
    ).slice(0, 8)
  }, [newSkill, skills])

  // STEP 7 — Clean rendering: sort by name, never raw JSON; render as skill badges only
  const sortedSkills = useMemo(
    () => [...skills].sort((a, b) => (a.name || '').localeCompare(b.name || '')),
    [skills]
  )

  useEffect(() => {
    if (initialSkills.length > 0) {
      setSkills(initialSkills)
    }
  }, [initialSkills])

  const handleAddSkill = (e?: React.FormEvent) => {
    if (e) e.preventDefault()
    if (!newSkill.trim()) return

    const id = `new-${Date.now()}`
    const addedSkill: Skill = {
      id,
      name: newSkill.trim(),
      category: null,
    }

    setSkills((prev) => [...prev, addedSkill])
    setNewSkill('')
    setShowDropdown(false)
  }

  const addSpecificSkill = (skillName: string) => {
    const id = `db-${Date.now()}`
    const addedSkill: Skill = { id, name: skillName, category: null }
    setSkills((prev) => [...prev, addedSkill])
    setNewSkill('')
    setShowDropdown(false)
  }

  const removeSkill = (id: string) => {
    setSkills((prev) => prev.filter((s) => s.id !== id))
  }

  const addSuggestedSkill = (skillName: string) => {
    const id = `sug-${Date.now()}`
    const addedSkill: Skill = {
      id,
      name: skillName,
      category: null,
    }
    setSkills((prev) => [...prev, addedSkill])
    setSuggestedSkills((prev) => prev.filter(s => s !== skillName))
  }

  return (
    <div className="bg-white rounded-[20px] shadow-lg border border-slate-100 p-10 max-w-4xl mx-auto font-sans">
      {/* Header Description */}
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h2 className="text-[20px] font-bold text-[#1E293B] mb-2">Key skills</h2>
          <p className="text-[13px] text-[#64748B]">
            Add skills that best define your expertise, for e.g. Direct Marketing, Oracle, Java, etc. (Minimum 1)
          </p>
        </div>
        {!editing ? (
          <button
            onClick={() => setEditing(true)}
            className="rounded-lg border border-slate-200 p-1.5 text-slate-500 hover:text-slate-700 transition-colors"
          >
            <Edit2 className="h-4 w-4" />
          </button>
        ) : (
          <div className="flex items-center gap-2">
            <button
              onClick={() => {
                onUpdate?.(skills)
                setEditing(false)
              }}
              className="rounded-lg border border-emerald-200 p-1.5 text-emerald-600 hover:text-emerald-700 transition-colors"
            >
              <Check className="h-4 w-4" />
            </button>
            <button
              onClick={() => {
                setSkills(initialSkills)
                setEditing(false)
              }}
              className="rounded-lg border border-slate-200 p-1.5 text-slate-500 hover:text-slate-700 transition-colors"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        )}
      </div>

      {/* Main Heading */}
      <div className="mb-4">
        <h3 className="text-[14px] font-bold text-[#1E293B]">Skills</h3>
      </div>

      {/* Active Skills Cloud — sorted, cleaned array; badge for LLM-added */}
      <div className="flex flex-wrap gap-3 mb-8">
        {sortedSkills.map((skill) => (
          <div
            key={skill.id}
            className="flex items-center gap-2 rounded-full border border-[#2D3E50] bg-white px-4 py-2 hover:bg-slate-50 transition-colors"
          >
            <span className="text-[14px] font-medium text-[#2D3E50]">
              {skill.name}
            </span>
            {skill.source === 'llm' && (
              <span
                className="text-[10px] font-medium px-1.5 py-0.5 rounded bg-amber-100 text-amber-800"
                title="Added via LLM"
              >
                Added via LLM
              </span>
            )}
            {editing && (
              <button
                onClick={() => removeSkill(skill.id)}
                className="text-[#64748B] hover:text-[#2D3E50] transition-colors"
              >
                <X size={16} />
              </button>
            )}
          </div>
        ))}
      </div>

      {editing && (
        <>
          {/* Input Field with Dropdown */}
          <div className="mb-10 relative">
            <div className="relative border-b border-slate-200 py-3">
              <input
                type="text"
                value={newSkill}
                onChange={(e) => {
                  setNewSkill(e.target.value)
                  setShowDropdown(true)
                }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleAddSkill()
                  if (e.key === 'Escape') setShowDropdown(false)
                }}
                onFocus={() => setShowDropdown(true)}
                placeholder="Add skills"
                className="w-full text-[15px] outline-none placeholder:text-slate-300 bg-transparent"
              />
            </div>

            {/* Autocomplete Dropdown */}
            {showDropdown && filteredDatabase.length > 0 && (
              <div className="absolute top-full left-0 w-full bg-white border border-slate-200 shadow-[0_10px_40px_-10px_rgba(0,0,0,0.15)] rounded-b-[15px] z-50 overflow-hidden mt-[-1px]">
                {filteredDatabase.map((s) => (
                  <button
                    key={s}
                    onClick={() => addSpecificSkill(s)}
                    className="w-full text-left px-5 py-3.5 text-[14px] hover:bg-slate-50 transition-colors border-b border-slate-50 last:border-b-0 group"
                  >
                    <span className="font-bold text-[#1E293B] group-hover:text-[#4A90E2]">
                      {s.substring(0, newSkill.length)}
                    </span>
                    <span className="text-[#64748B]">
                      {s.substring(newSkill.length)}
                    </span>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Suggestions Section */}
          <div className="mb-12">
            <p className="text-[14px] font-bold text-[#1E293B] mb-5">
              Or you can select from the suggested set of skills
            </p>
            <div className="flex flex-wrap gap-3">
              {suggestedSkills.map((skillName) => (
                <button
                  key={skillName}
                  onClick={() => addSuggestedSkill(skillName)}
                  className="group flex items-center gap-2 rounded-full border border-[#E2E8F0] bg-white px-4 py-1.5 hover:border-[#CBD5E1] transition-all"
                >
                  <span className="text-[13px] text-[#64748B] group-hover:text-[#1E293B]">
                    {skillName}
                  </span>
                  <Plus size={14} className="text-[#94A3B8] group-hover:text-[#64748B]" />
                </button>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  )
}
