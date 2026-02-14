import { apiClient } from './client'

export const fetchFileAsBlobUrl = async (url: string) => {
  const response = await apiClient.get<Blob>(url, { responseType: 'blob' })
  return URL.createObjectURL(response.data)
}
