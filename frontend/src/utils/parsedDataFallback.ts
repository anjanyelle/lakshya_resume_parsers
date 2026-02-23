/**
 * Transform parsed_data (from parsing job) into display shapes for UI components
 * when DB is empty. Used for read-only fallback display.
 */

import type { WorkHistory, Education, Certification, Skill, CandidateSkill } from '../types/candidate'

const _get = (obj: any, ...keys: string[]): string | undefined => {
  for (const k of keys) {
    const v = obj?.[k]
    if (v != null && typeof v === 'string' && v.trim()) return v.trim()
  }
  return undefined
}

/** Map parsed_data.work_experience to WorkHistory[] */
export function workHistoryFromParsed(
  items: any[] | undefined,
): WorkHistory[] {
  if (!Array.isArray(items)) return []
  return items.map((item, idx) => ({
    id: `parsed-we-${idx}`,
    company_name: _get(item, 'company_name', 'company') ?? null,
    client_name: _get(item, 'client_name', 'client') ?? null,
    job_title: _get(item, 'job_title', 'title', 'role') ?? null,
    start_date: _get(item, 'start_date') ?? null,
    end_date: _get(item, 'end_date') ?? null,
    is_current: Boolean(item?.is_current ?? null),
    location: _get(item, 'location') ?? null,
    description: _get(item, 'description') ?? null,
  }))
}

/** Map parsed_data.education to Education[] */
export function educationFromParsed(items: any[] | undefined): Education[] {
  if (!Array.isArray(items)) return []
  return items.map((item, idx) => ({
    id: `parsed-edu-${idx}`,
    institution: _get(item, 'institution') ?? null,
    degree: _get(item, 'degree') ?? null,
    field_of_study: _get(item, 'field_of_study') ?? null,
    start_date: _get(item, 'start_date') ?? null,
    end_date: _get(item, 'end_date') ?? null,
    description: _get(item, 'description') ?? null,
  }))
}

/** Map parsed_data.certifications to Certification[] */
export function certificationsFromParsed(
  items: any[] | undefined,
): Certification[] {
  if (!Array.isArray(items)) return []
  return items.map((item, idx) => ({
    id: `parsed-cert-${idx}`,
    name: _get(item, 'name') ?? '',
    issuing_organization: _get(item, 'issuing_organization') ?? null,
    issue_date: _get(item, 'issue_date') ?? null,
    expiry_date: _get(item, 'expiry_date') ?? null,
    credential_id: _get(item, 'credential_id') ?? null,
  }))
}

/** Map parsed_data.skills to Skill[] and CandidateSkill[] */
export function skillsFromParsed(items: any[] | undefined): {
  skills: Skill[]
  candidateSkills: CandidateSkill[]
} {
  if (!Array.isArray(items)) return { skills: [], candidateSkills: [] }
  const skills: Skill[] = []
  const candidateSkills: CandidateSkill[] = []
  items.forEach((item, idx) => {
    const name =
      typeof item === 'string'
        ? item.trim()
        : (_get(item, 'name', 'normalized_name') ?? '')
    if (!name) return
    const skill: Skill = {
      id: `parsed-skill-${idx}`,
      name,
      category: _get(item, 'category') ?? 'Other',
      normalized_name: _get(item, 'normalized_name', 'name') ?? null,
    }
    skills.push(skill)
    candidateSkills.push({
      skill,
      proficiency_level: _get(item, 'proficiency_level') ?? 'intermediate',
      years_experience: null,
    })
  })
  return { skills, candidateSkills }
}

/** Extract contact display from parsed_data.contact */
export function contactFromParsed(contact: any): {
  full_name: string | null
  email: string | null
  phone: string | null
  location: string | null
} {
  if (!contact || typeof contact !== 'object') {
    return { full_name: null, email: null, phone: null, location: null }
  }
  const name = contact?.name?.name ?? contact?.full_name ?? ''
  const email =
    contact?.emails?.[0]?.email ?? contact?.email ?? ''
  const phone =
    contact?.phones?.[0]?.phone ?? contact?.phone ?? ''
  const loc = contact?.location
  const location =
    typeof loc === 'string'
      ? loc
      : loc && typeof loc === 'object'
        ? [loc.city, loc.state, loc.country].filter(Boolean).join(', ') || null
        : null
  return {
    full_name: name?.trim() || null,
    email: email?.trim() || null,
    phone: phone?.trim() || null,
    location: location?.trim() || null,
  }
}

/** Extract summary from parsed_data.sections */
export function summaryFromParsed(parsed: any): string | null {
  const content = parsed?.sections?.summary?.content
  return typeof content === 'string' ? content.trim() || null : null
}

/** Check if we should use parsed_data fallback (DB empty but parsed has data) */
export function shouldUseParsedDataFallback(
  candidate: {
    work_history?: any[]
    education?: any[]
    certifications?: any[]
    candidate_skills?: any[]
    skills?: any[]
    full_name?: string | null
    summary?: string | null
  } | null,
  parsedData: Record<string, any>,
): boolean {
  if (!candidate || !parsedData) return false
  const hasDbWork = (candidate.work_history?.length ?? 0) > 0
  const hasDbEdu = (candidate.education?.length ?? 0) > 0
  const hasDbCerts = (candidate.certifications?.length ?? 0) > 0
  const hasDbSkills =
    (candidate.candidate_skills?.length ?? 0) > 0 ||
    (candidate.skills?.length ?? 0) > 0
  const hasDbName = Boolean(candidate.full_name?.trim())
  const hasDbSummary = Boolean(candidate.summary?.trim())

  const hasParsedWork =
    Array.isArray(parsedData.work_experience) &&
    parsedData.work_experience.length > 0
  const hasParsedEdu =
    Array.isArray(parsedData.education) && parsedData.education.length > 0
  const hasParsedCerts =
    Array.isArray(parsedData.certifications) &&
    parsedData.certifications.length > 0
  const hasParsedSkills =
    Array.isArray(parsedData.skills) && parsedData.skills.length > 0
  const contact = parsedData.contact
  const hasParsedName = Boolean(
    contact?.name?.name?.trim() || contact?.full_name?.trim(),
  )
  const hasParsedSummary = Boolean(summaryFromParsed(parsedData))

  const dbEmpty =
    !hasDbWork &&
    !hasDbEdu &&
    !hasDbCerts &&
    !hasDbSkills &&
    !hasDbName &&
    !hasDbSummary
  const parsedHasData =
    hasParsedWork ||
    hasParsedEdu ||
    hasParsedCerts ||
    hasParsedSkills ||
    hasParsedName ||
    hasParsedSummary

  return dbEmpty && parsedHasData
}
