import { useEffect, useState } from 'react'
import type { ChangeEvent, FormEvent } from 'react'
import { Link } from 'react-router-dom'

import { getAccessToken } from '../../features/auth'
import type { Classroom, ClassroomDetail, CreateClassroomRequest } from '../../models'
import { createClassroom, getProfessorClassrooms } from '../../services'
import { ApiRequestError } from '../../utils/requests'
import { ProfessorSidebar } from '../../components/ProfessorSidebar/ProfessorSidebar'
import './TurmasProfessorPage.css'

type ClassroomColor = 'cyan' | 'blue' | 'yellow'

const classroomColors: ClassroomColor[] = ['cyan', 'blue', 'yellow']

const initialClassroomForm: CreateClassroomRequest = {
  nome: '',
  descricao: '',
  criterios_avaliacao: '',
  regras: '',
}

function toClassroomListItem(classroom: ClassroomDetail): Classroom {
  return {
    id: classroom.id,
    nome: classroom.nome,
    descricao: classroom.descricao,
    codigo_acesso: classroom.codigo_acesso,
    professor_nome: classroom.professor.nome,
    ativo: classroom.ativo,
  }
}

function getClassroomColor(classroomId: number): ClassroomColor {
  return classroomColors[classroomId % classroomColors.length] ?? 'cyan'
}

export default function TurmasProfessorPage() {
  const [classrooms, setClassrooms] = useState<Classroom[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [isCreateFormOpen, setIsCreateFormOpen] = useState(false)
  const [classroomForm, setClassroomForm] = useState<CreateClassroomRequest>(initialClassroomForm)
  const [formErrorMessage, setFormErrorMessage] = useState<string | null>(null)
  const [isCreatingClassroom, setIsCreatingClassroom] = useState(false)

  useEffect(() => {
    async function loadClassrooms() {
      const token = getAccessToken()
      if (!token) {
        setErrorMessage('Sua sessão expirou. Entre novamente para ver suas turmas.')
        setIsLoading(false)
        return
      }

      try {
        setIsLoading(true)
        setErrorMessage(null)
        const response = await getProfessorClassrooms(token)
        setClassrooms(response)
      } catch (error) {
        const message = error instanceof ApiRequestError
          ? error.message
          : 'Não foi possível carregar suas turmas. Tente novamente.'
        setErrorMessage(message)
      } finally {
        setIsLoading(false)
      }
    }

    void loadClassrooms()
  }, [])

  const activeClassrooms = classrooms.filter((classroom) => classroom.ativo)

  const openCreateForm = () => {
    setFormErrorMessage(null)
    setIsCreateFormOpen(true)
  }

  const closeCreateForm = () => {
    setClassroomForm(initialClassroomForm)
    setFormErrorMessage(null)
    setIsCreateFormOpen(false)
  }

  const handleClassroomFormChange = (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = event.target
    setFormErrorMessage(null)
    setClassroomForm((currentForm) => ({
      ...currentForm,
      [name]: value,
    }))
  }

  const handleClassroomFormSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    if (isCreatingClassroom) {
      return
    }

    const classroomName = classroomForm.nome?.trim()
    if (!classroomName) {
      setFormErrorMessage('Informe o nome da turma.')
      return
    }

    const token = getAccessToken()
    if (!token) {
      setFormErrorMessage('Sua sessão expirou. Entre novamente para criar uma turma.')
      return
    }

    try {
      setIsCreatingClassroom(true)
      setFormErrorMessage(null)

      const createdClassroom = await createClassroom(
        {
          ...classroomForm,
          nome: classroomName,
        },
        token,
      )
      const classroomForList = toClassroomListItem(createdClassroom)

      setClassrooms((currentClassrooms) => [...currentClassrooms, classroomForList])
      closeCreateForm()
    } catch (error) {
      const message = error instanceof ApiRequestError
        ? error.message
        : 'Não foi possível criar a turma. Tente novamente.'
      setFormErrorMessage(message)
    } finally {
      setIsCreatingClassroom(false)
    }
  }

  return (
    <div className="turmas-professor-layout">
      <ProfessorSidebar activeItem="turmas" />
      <main className="turmas-professor-page">
      <header className="turmas-professor-header">
        <div>
          <p className="turmas-professor-eyebrow">Área do professor</p>
          <h1>Minhas turmas</h1>
          <p className="turmas-professor-subtitle">
            Organize suas disciplinas e acompanhe cada sala de aula.
          </p>
        </div>
      </header>

      <section className="classroom-summary" aria-label="Resumo das turmas">
        <div className="summary-icon" aria-hidden="true">▦</div>
        <div>
          <strong>Suas turmas em um só lugar</strong>
          <p>Compartilhe o código de acesso com os alunos para iniciar uma nova turma.</p>
        </div>
      </section>

      <section className="classroom-list-section" aria-labelledby="classroom-list-title">
        <div className="classroom-list-heading">
          <h2 id="classroom-list-title">Turmas ativas</h2>
          <span>{activeClassrooms.length} turmas</span>
        </div>

        {isLoading && (
          <div className="classroom-feedback" role="status">
            Carregando suas turmas...
          </div>
        )}

        {errorMessage && (
          <div className="classroom-feedback classroom-feedback-error" role="alert">
            {errorMessage}
          </div>
        )}

        {!isLoading && !errorMessage && (
          <div className="classroom-grid">
            {activeClassrooms.map((classroom) => (
            <article key={classroom.id} className="classroom-card">
              <div className={`classroom-card-banner ${getClassroomColor(classroom.id)}`}>
                <span className="classroom-card-symbol" aria-hidden="true">▣</span>
                <span className="classroom-active-label">Ativa</span>
              </div>

              <div className="classroom-card-content">
                <div>
                  <h3>{classroom.nome}</h3>
                  <p>{classroom.descricao}</p>
                </div>

                <div className="classroom-card-meta">
                  <span>Código: {classroom.codigo_acesso}</span>
                </div>

                <button type="button" className="open-classroom-button">
                  Abrir turma
                  <span aria-hidden="true">→</span>
                </button>
              </div>
            </article>
            ))}

            <article className="classroom-card classroom-card-empty">
              <div className="empty-classroom-icon" aria-hidden="true">+</div>
              <h3>{activeClassrooms.length === 0 ? 'Nenhuma turma ativa' : 'Nova turma'}</h3>
              <p>
                {activeClassrooms.length === 0
                  ? 'Crie uma sala para reunir aulas, atividades e seus alunos.'
                  : 'Crie uma nova sala para organizar outra disciplina.'}
              </p>
              <button type="button" className="empty-classroom-button" onClick={openCreateForm}>
                Criar turma
              </button>
            </article>
          </div>
        )}
      </section>

      {isCreateFormOpen && (
        <div className="classroom-modal-backdrop" role="presentation" onMouseDown={closeCreateForm}>
          <section
            className="classroom-create-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="classroom-create-title"
            onMouseDown={(event) => event.stopPropagation()}
          >
            <div className="classroom-create-header">
              <div>
                <p>Nova turma</p>
                <h2 id="classroom-create-title">Criar turma</h2>
              </div>
              <button
                type="button"
                className="close-classroom-modal-button"
                onClick={closeCreateForm}
                aria-label="Fechar formulário de criação de turma"
              >
                ×
              </button>
            </div>

            <form className="classroom-create-form" onSubmit={handleClassroomFormSubmit}>
              <label>
                <span>Nome da turma</span>
                <input
                  type="text"
                  name="nome"
                  value={classroomForm.nome}
                  onChange={handleClassroomFormChange}
                  placeholder="Ex.: Matemática - 2º ano"
                  autoFocus
                />
              </label>

              <label>
                <span>Descrição</span>
                <textarea
                  name="descricao"
                  value={classroomForm.descricao}
                  onChange={handleClassroomFormChange}
                  placeholder="Apresente brevemente a disciplina para seus alunos."
                  rows={3}
                />
              </label>

              <label>
                <span>Critérios de avaliação</span>
                <textarea
                  name="criterios_avaliacao"
                  value={classroomForm.criterios_avaliacao}
                  onChange={handleClassroomFormChange}
                  placeholder="Ex.: atividades, provas e participação"
                  rows={3}
                />
              </label>

              <label>
                <span>Regras da turma</span>
                <textarea
                  name="regras"
                  value={classroomForm.regras}
                  onChange={handleClassroomFormChange}
                  placeholder="Defina os combinados para a sala de aula."
                  rows={3}
                />
              </label>

              {formErrorMessage && <p className="classroom-form-error" role="alert">{formErrorMessage}</p>}

              <div className="classroom-create-actions">
                <button type="button" className="cancel-classroom-button" onClick={closeCreateForm}>
                  Cancelar
                </button>
                <button type="submit" className="submit-classroom-button">
                  Criar turma
                </button>
              </div>
            </form>
          </section>
        </div>
      )}

      <footer className="turmas-professor-footer">
        <Link to="/app/inicio_professor">Voltar ao início</Link>
      </footer>
      </main>
    </div>
  )
}