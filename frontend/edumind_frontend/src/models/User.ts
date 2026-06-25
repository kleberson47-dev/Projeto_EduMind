export type UserRole = 'professor' | 'aluno'

export interface User {
  id: number
  nome: string
  email: string
  role: UserRole
  avatar: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface CreateUserRequest {
  nome: string
  email: string
  senha: string
  role: UserRole
  avatar?: File | null
  is_active?: boolean
}

export interface UpdateUserRequest {
  nome?: string
  email?: string
  senha?: string
  role?: UserRole
  avatar?: File | null
  is_active?: boolean
}
