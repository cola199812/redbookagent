import api from './index'

export interface SearchResult {
  content: string
  metadata: Record<string, any>
}

export const searchKnowledge = async (query: string, k: number = 5) => {
  const response = await api.post('/knowledge/search', { query, k })
  return response.data
}

export const listDocuments = async () => {
  const response = await api.get('/knowledge/list')
  return response.data
}

export const addDocuments = async (files: FileList) => {
  const formData = new FormData()
  for (let i = 0; i < files.length; i++) {
    formData.append('files', files[i])
  }
  const response = await api.post('/knowledge/add', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  return response.data
}
