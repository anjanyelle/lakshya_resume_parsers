import type { CandidateSkill, Skill } from '../../types'

type SkillsSectionProps = {
  skills?: Skill[]
  candidateSkills?: CandidateSkill[]
}

const proficiencyValue = (level?: string | null) => {
  switch (level) {
    case 'expert':
      return 100
    case 'advanced':
      return 80
    case 'intermediate':
      return 60
    case 'beginner':
      return 40
    default:
      return 50
  }
}

export default function SkillsSection({
  skills = [],
  candidateSkills = [],
}: SkillsSectionProps) {
  const grouped = skills.reduce<Record<string, Skill[]>>((acc, skill) => {
    const category = skill.category || 'Other'
    acc[category] = acc[category] || []
    acc[category].push(skill)
    return acc
  }, {})

  const proficiencyMap = new Map(
    candidateSkills
      .filter((item) => item.skill?.id)
      .map((item) => [item.skill!.id, item.proficiency_level]),
  )

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6">
      <h2 className="text-lg font-semibold text-slate-900">Skills</h2>
      {skills.length === 0 ? (
        <p className="mt-3 text-sm text-slate-600">No skills recorded.</p>
      ) : (
        <div className="mt-4 space-y-4">
          {Object.entries(grouped).map(([category, items]) => (
            <div key={category}>
              <p className="text-xs font-semibold uppercase text-slate-500">
                {category}
              </p>
              <div className="mt-2 space-y-2">
                {items.map((skill) => {
                  const level = proficiencyMap.get(skill.id)
                  return (
                    <div key={skill.id} className="flex items-center gap-3">
                      <span className="min-w-[120px] text-sm text-slate-700">
                        {skill.name}
                      </span>
                      <div className="h-2 flex-1 rounded-full bg-slate-100">
                        <div
                          className="h-full rounded-full bg-brand-500"
                          style={{ width: `${proficiencyValue(level)}%` }}
                        />
                      </div>
                      <span className="text-xs text-slate-500">
                        {level ?? 'intermediate'}
                      </span>
                    </div>
                  )
                })}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
