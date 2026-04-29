import api from './index'

export const generateContent = async (data: {
  topic: string
  style: string
  keywords?: string[]
  extra?: string
}) => {
  const response = await api.post('/creator/generate', data)
  return response.data
}

export const getCreatorInfo = async () => {
  const response = await api.get('/creator/info')
  return response.data
}
