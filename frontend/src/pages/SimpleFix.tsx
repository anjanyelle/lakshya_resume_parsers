// Simple fix to add type property to field mappings
const fieldMappingsFix = [
    { id: 'full_name', value: displayCandidate.full_name ?? '', label: 'Candidate Name', type: 'personal' },
    { id: 'email', value: displayCandidate.email ?? '', label: 'Candidate Email', type: 'contact' },
    { id: 'phone', value: displayCandidate.phone ?? '', label: 'Candidate Phone', type: 'contact' },
    { id: 'location', value: displayCandidate.location ?? '', label: 'Location', type: 'personal' },
    { id: 'linkedin_url', value: displayCandidate.linkedin_url ?? '', label: 'LinkedIn', type: 'personal' },
    { id: 'github_url', value: displayCandidate.github_url ?? '', label: 'GitHub', type: 'personal' },
    ...(summaryExcerpt
      ? [{ id: 'summary' as const, value: summaryExcerpt, label: 'Summary', type: 'personal' as const }]
      : []),
    ...displaySkills
      .filter((s) => s.name?.trim().length > 2)
      .map((s) => ({ id: 'skills' as const, value: s.name, label: 'Skills', type: 'skills' as const })),
    ...displayWorkHistory
      .filter((wh) => (wh.company_name ?? '').trim().length > 2)
      .map((wh) => ({ id: 'experience' as const, value: wh.company_name ?? '', label: 'Experience', type: 'experience' as const })),
    ...displayWorkHistory
      .filter((wh) => (wh.job_title ?? '').trim().length > 2)
      .map((wh) => ({ id: 'experience' as const, value: wh.job_title ?? '', label: 'Experience', type: 'experience' as const })),
    ...displayEducation
      .filter((e) => (e.institution ?? '').trim().length > 2)
      .map((e) => ({ id: 'education' as const, value: e.institution ?? '', label: 'Education', type: 'education' as const })),
    ...displayEducation
      .filter((e) => (e.degree ?? '').trim().length > 2)
      .map((e) => ({ id: 'education' as const, value: e.degree ?? '', label: 'Education', type: 'education' as const })),
  ]
