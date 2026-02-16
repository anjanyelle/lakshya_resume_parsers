import axios from 'axios'

import { apiClient } from './client'

export const fetchFileAsBlobUrl = async (url: string) => {
  const baseURL = apiClient.defaults.baseURL?.toString() ?? ''
  const isAbsolute = /^https?:\/\//i.test(url)
  const isExternal = Boolean(isAbsolute && baseURL && !url.startsWith(baseURL))

  const response = isExternal
    ? await axios.get<Blob>(url, { responseType: 'blob' })
    : await apiClient.get<Blob>(url, { responseType: 'blob' })

  const blob = response.data
  const contentType =
    (response.headers?.['content-type'] as string | undefined) ?? ''

  if (contentType.includes('application/json') || contentType.includes('text/html')) {
    const text = await blob.text().catch(() => '')
    const match = text.match(/"detail"\s*:\s*"([^"]+)"/)
    const detail = match?.[1] || 'Preview unavailable'
    throw new Error(detail)
  }

  const headerBuf = await blob.slice(0, 4).arrayBuffer()
  const header = new TextDecoder().decode(headerBuf)
  if (header !== '%PDF') {
    if (header.startsWith('PK')) {
      throw new Error('Preview not supported for this file type. Please download.')
    }
    if (contentType && !contentType.includes('pdf')) {
      throw new Error('Preview unavailable for this file type. Please download.')
    }
  }

  return URL.createObjectURL(blob)
}
