import { apiClient } from './client'

export type TaxonomySkill = {
  name: string | null
  category: string | null
  synonyms: string | null
  group?: string | null
}

export type TaxonomyItem = {
  name: string
}

export const fetchTaxonomySkills = async (limit = 200) => {
  const response = await apiClient.get<TaxonomySkill[]>(
    `/api/v1/taxonomy/skills?limit=${limit}`,
  )
  return response.data
}

export const fetchTaxonomyDegrees = async (limit = 200) => {
  const response = await apiClient.get<TaxonomyItem[]>(
    `/api/v1/taxonomy/degrees?limit=${limit}`,
  )
  return response.data
}

export const fetchTaxonomyUniversities = async (limit = 200) => {
  const response = await apiClient.get<TaxonomyItem[]>(
    `/api/v1/taxonomy/universities?limit=${limit}`,
  )
  return response.data
}

export const fetchTaxonomyCertifications = async (limit = 200) => {
  const response = await apiClient.get<TaxonomyItem[]>(
    `/api/v1/taxonomy/certifications?limit=${limit}`,
  )
  return response.data
}
