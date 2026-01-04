import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { z } from 'zod'
import { api } from '../lib/api'

export const profileUpdateSchema = z.object({
  name: z.string().min(1, 'Name is required').optional(),
  mobile: z.string().regex(/^[0-9+\-\s()]+$/, 'Invalid mobile number').optional(),
  date_of_birth: z.string().optional(),
})

export type ProfileUpdate = z.infer<typeof profileUpdateSchema>

export interface UserProfile {
  id: string
  email: string
  name: string
  mobile?: string
  date_of_birth?: string
  avatar_url?: string
  created_at?: string
}

export interface AvatarUploadResponse {
  avatar_url: string
}

export function useProfile() {
  return useQuery<UserProfile>({
    queryKey: ['profile'],
    queryFn: async () => {
      const { data } = await api.get('/users/profile')
      return data
    },
  })
}

export function useUpdateProfile() {
  const queryClient = useQueryClient()
  return useMutation<UserProfile, Error, ProfileUpdate>({
    mutationFn: async (updateData) => {
      const { data } = await api.patch('/users/profile', updateData)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile'] })
    },
  })
}

export function useUploadAvatar() {
  const queryClient = useQueryClient()
  return useMutation<AvatarUploadResponse, Error, File>({
    mutationFn: async (file) => {
      const formData = new FormData()
      formData.append('file', file)
      const { data } = await api.post('/users/profile/avatar', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile'] })
    },
  })
}
