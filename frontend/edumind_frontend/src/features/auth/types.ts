export interface LoginPayload {
  email: string
  password: string
}

export interface CadastroUsuarioPayload {
  nome: string
  email: string
  senha: string
  role: 'professor' | 'aluno'
}
