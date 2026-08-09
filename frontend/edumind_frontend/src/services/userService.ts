import type { CreateUserRequest, UpdateUserRequest, User } from '../models/User'
import { API_ENDPOINTS } from '../utils/api'
import { requestJson } from '../utils/requests'

function appendOptionalField(formData: FormData, key: string, value: unknown) {
  if (value === undefined || value === null) {
    return
  }

  if (value instanceof File) {
    formData.append(key, value)
    return
  }

  formData.append(key, String(value))
}

function buildUserFormData(payload: CreateUserRequest | UpdateUserRequest): FormData {
  const formData = new FormData()

  appendOptionalField(formData, 'nome', payload.nome)
  appendOptionalField(formData, 'email', payload.email)
  appendOptionalField(formData, 'senha', payload.senha)
  appendOptionalField(formData, 'role', payload.role)
  appendOptionalField(formData, 'is_active', payload.is_active)

  if ('avatar' in payload && payload.avatar !== undefined) {
    appendOptionalField(formData, 'avatar', payload.avatar)
  }

  return formData
}

export async function getCurrentUser(token: string): Promise<User> {
  return requestJson<User>(API_ENDPOINTS.accounts.me, {
    method: 'GET',
    token,
  })
}

export async function createUser(
  payload: CreateUserRequest,
): Promise<User> {
  return requestJson<User>(API_ENDPOINTS.accounts.criarUsuario, {
    method: 'POST',
    body: {
      nome: payload.nome,
      email: payload.email,
      senha: payload.senha,
      role: payload.role,
    },
  })
}

export async function updateUser(
  id: number,
  payload: UpdateUserRequest,
  token: string,
): Promise<User> {
  return requestJson<User>(API_ENDPOINTS.accounts.editarUsuario(id), {
    method: 'PATCH',
    body: buildUserFormData(payload),
    token,
  })
}

export async function deleteUser(id: number, token: string): Promise<void> {
  return requestJson<void>(API_ENDPOINTS.accounts.excluirUsuario(id), {
    method: 'DELETE',
    token,
  })
}
