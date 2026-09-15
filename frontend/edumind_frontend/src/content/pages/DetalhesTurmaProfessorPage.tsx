import { useEffect, useState } from 'react'
import type { ChangeEvent, FormEvent } from 'react'
import { Link, useParams } from 'react-router-dom'

import {
  ProfessorSidebar,
  TemporaryMessage,
} from '../../components'
import { getAccessToken } from '../../features/auth'
import type {
  ClassroomDetail,
  UpdateClassroomRequest,
} from '../../models'
import {
  getProfessorClassroomDetail,
  updateProfessorClassroom,
} from '../../services'
import { ApiRequestError } from '../../utils/requests'
import {
  createTemporaryMessage,
  TEMPORARY_MESSAGE_DURATION,
  type TemporaryMessage as TemporaryMessageData,
} from '../../utils'

import './DetalhesTurmaProfessorPage.css'

const emptyFormState: UpdateClassroomRequest = {
  nome: '',
  descricao: '',
  criterios_avaliacao: '',
  regras: '',
  ativo: true,
}

export default function DetalhesTurmaProfessorPage() {
  const { classroomId } = useParams()
  const [classroom, setClassroom] = useState<ClassroomDetail | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [isEditing, setIsEditing] = useState(false)
  const [formState, setFormState] = useState<UpdateClassroomRequest>(emptyFormState)
  const [isSaving, setIsSaving] = useState(false)
  const [formErrorMessage, setFormErrorMessage] = useState<string | null>(null)
  const [temporaryMessage, setTemporaryMessage] = useState<TemporaryMessageData | null>(null)

  useEffect(() => {
    let isCurrentRequest = true
    const parsedClassroomId = Number(classroomId)

    async function loadClassroom() {
      if (!Number.isInteger(parsedClassroomId) || parsedClassroomId <= 0) {
        setErrorMessage('Turma não encontrada.')
        setIsLoading(false)
        return
      }

      const token = getAccessToken()
      if (!token) {
        setErrorMessage('Sua sessão expirou. Entre novamente para acessar a turma.')
        setIsLoading(false)
        return
      }

      try {
        setIsLoading(true)
        setErrorMessage(null)
        const response = await getProfessorClassroomDetail(parsedClassroomId, token)

        if (isCurrentRequest) {
          setClassroom(response)
        }
      } catch (error) {
        if (isCurrentRequest) {
          const message = error instanceof ApiRequestError
            ? error.message
            : 'Não foi possível carregar a turma. Tente novamente.'
          setErrorMessage(message)
        }
      } finally {
        if (isCurrentRequest) {
          setIsLoading(false)
        }
      }
    }

    void loadClassroom()

    return () => {
      isCurrentRequest = false
    }
  }, [classroomId])

  useEffect(() => {
    if (!temporaryMessage) {
      return undefined
    }

    const timeoutId = window.setTimeout(() => {
      setTemporaryMessage(null)
    }, TEMPORARY_MESSAGE_DURATION)

    return () => {
      window.clearTimeout(timeoutId)
    }
  }, [temporaryMessage])

  const openEditForm = () => {
    if (!classroom) {
      return
    }

    setFormState({
      nome: classroom.nome,
      descricao: classroom.descricao,
      criterios_avaliacao: classroom.criterios_avaliacao,
      regras: classroom.regras,
      ativo: classroom.ativo,
    })
    setFormErrorMessage(null)
    setIsEditing(true)
  }

  const cancelEditing = () => {
    if (isSaving) {
      return
    }

    setIsEditing(false)
    setFormState(emptyFormState)
    setFormErrorMessage(null)
  }

  const handleFieldChange = (
    event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
  ) => {
    const { name, value } = event.target

    setFormState((currentState) => ({
      ...currentState,
      [name]: value,
    }))
  }

  const handleActiveChange = (event: ChangeEvent<HTMLInputElement>) => {
    setFormState((currentState) => ({
      ...currentState,
      ativo: event.target.checked,
    }))
  }

  const handleEditSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    if (!classroom || isSaving) {
      return
    }

    const parsedClassroomId = Number(classroomId)
    if (!Number.isInteger(parsedClassroomId) || parsedClassroomId <= 0) {
      setFormErrorMessage('Turma não encontrada.')
      return
    }

    const token = getAccessToken()
    if (!token) {
      setFormErrorMessage('Sua sessão expirou. Entre novamente para salvar as alterações.')
      return
    }

    const nome = formState.nome?.trim() ?? ''
    if (!nome) {
      setFormErrorMessage('Informe o nome da turma.')
      return
    }

    try {
      setIsSaving(true)
      setFormErrorMessage(null)

      const updatedClassroom = await updateProfessorClassroom(
        parsedClassroomId,
        { ...formState, nome },
        token,
      )

      setClassroom((currentClassroom) => currentClassroom
        ? { ...currentClassroom, ...updatedClassroom }
        : currentClassroom)
      setIsEditing(false)
      setFormState(emptyFormState)
      setTemporaryMessage(createTemporaryMessage('success', 'Alterações salvas com sucesso.'))
    } catch (error) {
      const message = error instanceof ApiRequestError
        ? error.message
        : 'Não foi possível salvar as alterações. Tente novamente.'
      setFormErrorMessage(message)
      setTemporaryMessage(createTemporaryMessage('error', message))
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <div className="detalhes-turma-professor-layout">
      <ProfessorSidebar activeItem="turmas" />

      <main className="detalhes-turma-professor-page">
        <header className="detalhes-turma-header">
          <div>
            <p className="detalhes-turma-eyebrow">Área do professor</p>
            <h1>{classroom?.nome ?? 'Turma'}</h1>
            <p className="detalhes-turma-subtitle">
              {classroom?.descricao || 'Organize as informações, conteúdos e acompanhamentos desta sala.'}
            </p>
          </div>
        </header>

        <TemporaryMessage message={temporaryMessage} />

        {isLoading && <p className="detalhes-turma-feedback" role="status">Carregando turma...</p>}

        {errorMessage && (
          <div className="detalhes-turma-feedback detalhes-turma-feedback-error" role="alert">
            <p>{errorMessage}</p>
            <Link to="/app/turmas-professor">Voltar para minhas turmas</Link>
          </div>
        )}

        {!isLoading && !errorMessage && classroom && (
          <>
            <section className="detalhes-turma-overview" aria-labelledby="detalhes-turma-overview-title">
              <div>
                <p className="detalhes-turma-label">Informações da turma</p>
                <h2 id="detalhes-turma-overview-title">Detalhes principais</h2>
                <p>{classroom.criterios_avaliacao || 'Nenhum critério de avaliação informado.'}</p>
                <p className="detalhes-turma-rules"><strong>Regras:</strong> {classroom.regras || 'Nenhuma regra informada.'}</p>
                <p className="detalhes-turma-members">Professor: {classroom.professor.nome} · {classroom.numero_alunos} alunos matriculados</p>
              </div>

              <div className="detalhes-turma-code">
                <span>Código de acesso</span>
                <strong>{classroom.codigo_acesso}</strong>
                <small>{classroom.ativo ? 'Turma ativa' : 'Turma inativa'}</small>
              </div>
            </section>

            <section className="detalhes-turma-edit" aria-labelledby="detalhes-turma-edit-title">
              <div className="detalhes-turma-edit-heading">
                <div>
                  <p className="detalhes-turma-label">Configurações</p>
                  <h2 id="detalhes-turma-edit-title">Dados da turma</h2>
                </div>

                {!isEditing && (
                  <button type="button" className="detalhes-turma-edit-button" onClick={openEditForm}>
                    Editar informações
                  </button>
                )}
              </div>

              {isEditing && (
                <form className="detalhes-turma-edit-form" onSubmit={handleEditSubmit}>
                  <label>
                    <span>Nome da turma</span>
                    <input name="nome" value={formState.nome ?? ''} onChange={handleFieldChange} />
                  </label>

                  <label>
                    <span>Descrição</span>
                    <textarea name="descricao" value={formState.descricao ?? ''} onChange={handleFieldChange} rows={3} />
                  </label>

                  <label>
                    <span>Critérios de avaliação</span>
                    <textarea name="criterios_avaliacao" value={formState.criterios_avaliacao ?? ''} onChange={handleFieldChange} rows={3} />
                  </label>

                  <label>
                    <span>Regras da turma</span>
                    <textarea name="regras" value={formState.regras ?? ''} onChange={handleFieldChange} rows={3} />
                  </label>

                  <label className="detalhes-turma-active-field">
                    <input type="checkbox" checked={formState.ativo ?? false} onChange={handleActiveChange} />
                    <span>Turma ativa</span>
                  </label>

                  {formErrorMessage && (
                    <p className="detalhes-turma-form-error" role="alert">{formErrorMessage}</p>
                  )}

                  <div className="detalhes-turma-edit-actions">
                    <button type="button" className="detalhes-turma-cancel-button" onClick={cancelEditing} disabled={isSaving}>
                      Cancelar
                    </button>
                    <button type="submit" className="detalhes-turma-save-button" disabled={isSaving}>
                      {isSaving ? 'Salvando...' : 'Salvar alterações'}
                    </button>
                  </div>
                </form>
              )}
            </section>

            <section className="detalhes-turma-lessons" aria-labelledby="detalhes-turma-lessons-title">
              <div className="detalhes-turma-lessons-heading">
                <div>
                  <p className="detalhes-turma-label">Conteúdos</p>
                  <h2 id="detalhes-turma-lessons-title">Aulas</h2>
                  <p>Organize as aulas e os materiais desta turma.</p>
                </div>
                <Link
                  to={`/app/turmas-professor/${classroom.id}/aulas`}
                  className="detalhes-turma-add-lesson-button"
                >
                  Ver aulas
                </Link>
              </div>

              <div className="detalhes-turma-lessons-empty">
                <span className="detalhes-turma-section-icon" aria-hidden="true">▤</span>
                <div>
                  <h3>Organize os conteúdos em aulas</h3>
                  <p>Acesse a página de aulas para criar e organizar os conteúdos desta turma.</p>
                </div>
              </div>
            </section>

            <section className="detalhes-turma-sections" aria-label="Gestão da turma">

              <article className="detalhes-turma-section-card">
                <span className="detalhes-turma-section-icon" aria-hidden="true">≋</span>
                <div>
                  <h2>Atividades</h2>
                  <p>Prepare tarefas, trabalhos e avaliações para esta turma.</p>
                </div>
              </article>

              <article className="detalhes-turma-section-card">
                <span className="detalhes-turma-section-icon" aria-hidden="true">◎</span>
                <div>
                  <h2>Alunos e notas</h2>
                  <p>Acompanhe matrículas, desempenho e registros de avaliação.</p>
                </div>
              </article>
            </section>
          </>
        )}
      </main>
    </div>
  )
}