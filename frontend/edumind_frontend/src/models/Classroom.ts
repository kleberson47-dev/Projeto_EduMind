export type ActivityType = 'atividade' | 'trabalho' | 'prova' | 'material'

export type LessonBlockType = 'texto' | 'imagem' | 'video' | 'tabela' | 'lista'

export interface ProfessorSummary {
  id: number
  nome: string
  email: string
}

export interface Classroom {
  id: number
  nome: string
  descricao: string
  codigo_acesso: string
  professor_nome: string
  ativo: boolean
}

export interface ClassroomDetail {
  id: number
  nome: string
  descricao: string
  codigo_acesso: string
  criterios_avaliacao: string
  regras: string
  professor: ProfessorSummary
  numero_alunos: number
  ativo: boolean
  created_at: string
  updated_at: string
}

export interface CreateClassroomRequest {
  nome: string
  descricao?: string
  criterios_avaliacao?: string
  regras?: string
}

export interface UpdateClassroomRequest {
  nome?: string
  descricao?: string
  criterios_avaliacao?: string
  regras?: string
  ativo?: boolean
}

export interface JoinClassroomRequest {
  codigo_acesso: string
}

export interface JoinClassroomResponse {
  message: string
  classroom_id: number
  classroom_name: string
}

export interface Activity {
  id: number
  turma: number
  titulo: string
  descricao: string
  tipo: ActivityType
  data_entrega: string | null
  ativo: boolean
  created_at: string
  updated_at: string
}

export interface CreateActivityRequest {
  titulo: string
  descricao?: string
  tipo?: ActivityType
  data_entrega?: string | null
  ativo?: boolean
}

export interface Grade {
  id: number
  aluno: number
  turma: number
  atividade: number
  valor: string
  observacao: string
  ativo: boolean
  created_at: string
  updated_at: string
}

export interface CreateGradeRequest {
  aluno: number
  atividade: number
  valor: number
  observacao?: string
  ativo?: boolean
}

export interface LessonBlock {
  id: number
  secao: number
  tipo: LessonBlockType
  titulo: string
  conteudo: string
  url_imagem: string
  url_video: string
  tabela_json: unknown
  ordem: number
  ativo: boolean
  created_at: string
  updated_at: string
}

export interface LessonSection {
  id: number
  aula: number
  titulo: string
  descricao: string
  ordem: number
  ativo: boolean
  blocos: LessonBlock[]
  created_at: string
  updated_at: string
}

export interface Lesson {
  id: number
  turma: number
  titulo: string
  descricao: string
  ordem: number
  ativo: boolean
  secoes: LessonSection[]
  created_at: string
  updated_at: string
}

export interface CreateLessonRequest {
  titulo: string
  descricao?: string
  ordem?: number
  ativo?: boolean
}

export interface CreateLessonSectionRequest {
  titulo: string
  descricao?: string
  ordem?: number
  ativo?: boolean
}

export interface CreateLessonBlockRequest {
  tipo: LessonBlockType
  titulo?: string
  conteudo?: string
  url_imagem?: string
  url_video?: string
  tabela_json?: unknown
  ordem?: number
  ativo?: boolean
}