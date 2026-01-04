import { useState, useRef } from 'react'
import { useProfile, useUpdateProfile, useUploadAvatar, profileUpdateSchema } from '../hooks/useProfile'
import Card from '../components/Card'
import Button from '../components/Button'
import Input from '../components/Input'
import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'

export default function Profile() {
  const { data: profile, isLoading, error } = useProfile()
  const updateProfile = useUpdateProfile()
  const uploadAvatar = useUploadAvatar()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [preview, setPreview] = useState<string>('')

  const {
    register,
    handleSubmit,
    formState: { errors, isDirty },
    reset,
  } = useForm({
    resolver: zodResolver(profileUpdateSchema),
    defaultValues: {
      name: profile?.name || '',
      mobile: profile?.mobile || '',
      date_of_birth: profile?.date_of_birth?.split('T')[0] || '',
    },
    values: profile ? {
      name: profile.name || '',
      mobile: profile.mobile || '',
      date_of_birth: profile.date_of_birth?.split('T')[0] || '',
    } : undefined,
  })

  const onSubmit = (data: any) => {
    updateProfile.mutate(data, {
      onSuccess: () => {
        reset(data)
      }
    })
  }

  const handleAvatarChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      if (file.size > 5 * 1024 * 1024) {
        alert('File size must be less than 5MB')
        return
      }
      const reader = new FileReader()
      reader.onloadend = () => {
        setPreview(reader.result as string)
      }
      reader.readAsDataURL(file)
      uploadAvatar.mutate(file)
    }
  }

  if (isLoading) return <div className="min-h-[60vh] flex items-center justify-center"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div></div>
  if (error) return <div className="text-center py-12 text-red-400">Failed to load profile</div>
  if (!profile) return null

  return (
    <div className="py-2 sm:py-4">
      <div className="mx-auto max-w-2xl">
        <Card className="p-6 sm:p-8">
          <h1 className="text-2xl font-bold text-white mb-8">Profile</h1>

          {/* Avatar Section */}
          <div className="flex flex-col items-center mb-8">
            <div className="relative group">
              <div className="w-32 h-32 rounded-full overflow-hidden bg-gradient-to-br from-indigo-500 to-purple-600 p-1">
                <div className="w-full h-full rounded-full overflow-hidden bg-slate-900 flex items-center justify-center">
                  {(preview || profile.avatar_url) ? (
                    <img
                      src={preview || profile.avatar_url}
                      alt="Avatar"
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="text-3xl font-bold text-white">
                      {profile.name.charAt(0).toUpperCase()}
                    </div>
                  )}
                </div>
              </div>
              <button
                onClick={() => fileInputRef.current?.click()}
                className="absolute bottom-0 right-0 bg-indigo-600 text-white p-2 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </button>
            </div>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleAvatarChange}
              className="hidden"
            />
            <p className="text-sm text-slate-400 mt-3">Click to change avatar</p>
            {uploadAvatar.isPending && <p className="text-xs text-indigo-400 mt-1">Uploading...</p>}
          </div>

          {/* Profile Form */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Email</label>
              <Input
                type="email"
                value={profile.email}
                disabled
                className="bg-slate-800/50"
              />
              <p className="text-xs text-slate-500 mt-1">Email cannot be changed</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Name</label>
              <Input
                {...register('name')}
                placeholder="Your name"
                error={errors.name?.message}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Mobile Number</label>
              <Input
                {...register('mobile')}
                placeholder="+1 (555) 123-4567"
                error={errors.mobile?.message}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Date of Birth</label>
              <Input
                type="date"
                {...register('date_of_birth')}
                error={errors.date_of_birth?.message}
              />
            </div>

            <div className="flex gap-3 pt-4">
              <Button
                type="submit"
                disabled={!isDirty || updateProfile.isPending}
                className="flex-1"
              >
                {updateProfile.isPending ? 'Saving...' : 'Save Changes'}
              </Button>
              <Button
                type="button"
                variant="secondary"
                onClick={() => reset()}
                disabled={!isDirty}
              >
                Reset
              </Button>
            </div>
          </form>
        </Card>
      </div>
    </div>
  )
}
