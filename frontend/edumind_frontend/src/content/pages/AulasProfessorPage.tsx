import { useEffect, useState } from 'react'
import type { ChangeEvent, FormEvent } from 'react'
import { Link, useParams } from 'react-router-dom'

import { ProfessorSidebar, TemporaryMessage } from '../../components'
import { getAccessToken } from '../../features/auth'
import type { CreateLessonRequest, Lesson } from '../../models'
import { createLesson, getProfessorLessons } from '../../services'
import {
  createTemporaryMessage,
  TEMPORARY_MESSAGE_DURATION,
  type TemporaryMessage as TemporaryMessageData,
} from '../../utils'
import { ApiRequestError } from '../../utils/requests'

import './AulasProfessorPage.css'

const initialLessonForm: CreateLessonRequest = {
  titulo: '',
  descricao: '',
  ordem: 1,
  ativo: true,
}

export default function AulasProfessorPage() {
  const { classroomId } = useParams()
  const [lessons, setLessons] = useState<Lesson[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [isCreateFormOpen, setIsCreateFormOpen] = useState(false)
  const [lessonForm, setLessonForm] = useState<CreateLessonRequest>(initialLessonForm)
  const [formErrorMessage, setFormErrorMessage] = useState<string | null>(null)
  const [isCreating, setIsCreating] = useState(false)
  const [temporaryMessage, setTemporaryMessage] = useState<TemporaryMessageData | null>(null)

  const openCreateForm = () => {
    setLessonForm({
      ...initialLessonForm,
      ordem: lessons.length + 1,
    })
    setFormErrorMessage(null)
    setIsCreateFormOpen(true)
  }

  const closeCreateForm = () => {
    if (isCreating) {
      return
    }

    setIsCreateFormOpen(false)
    setLessonForm(initialLessonForm)
    setFormErrorMessage(null)
  }

  const handleFormChange = (
    event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
  ) => {
    const { name, value } = event.target

    setLessonForm((currentForm) => ({
      ...currentForm,
      [name]: name === 'ordem' ? Number(value) : value,
    }))
  }

  const handleActiveChange = (event: ChangeEvent<HTMLInputElement>) => {
    setLessonForm((currentForm) => ({
      ...currentForm,
      ativo: event.target.checked,
    }))
  }

  const handleCreateLesson = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    if (isCreating) {
      return
    }

    if (!lessonForm.titulo?.trim()) {
      setFormErrorMessage('Informe o título da aula.')
      return
    }

    if (!Number.isInteger(lessonForm.ordem) || (lessonForm.ordem ?? 0) < 1) {
      setFormErrorMessage('A ordem da aula deve ser um número inteiro maior que zero.')
      return
    }

    const parsedClassroomId = Number(classroomId)
    if (!Number.isInteger(parsedClassroomId) || parsedClassroomId <= 0) {
      setFormErrorMessage('A turma informada é inválida.')
      return
    }

    const token = getAccessToken()
    if (!token) {
      setFormErrorMessage('Sua sessão expirou. Entre novamente para criar a aula.')
      return
    }

    try {
      setIsCreating(true)
      setFormErrorMessage(null)

      const createdLesson = await createLesson(
        parsedClassroomId,
        { ...lessonForm, titulo: lessonForm.titulo.trim() },
        token,
      )

      setLessons((currentLessons) => [...currentLessons, createdLesson].sort(
        (firstLesson, secondLesson) => firstLesson.ordem - secondLesson.ordem,
      ))
      setIsCreateFormOpen(false)
      setLessonForm(initialLessonForm)
      setTemporaryMessage(createTemporaryMessage('success', 'Aula criada com sucesso.'))
    } catch (error) {
      const message = error instanceof ApiRequestError
        ? error.message
        : 'Não foi possível criar a aula. Tente novamente.'
      setFormErrorMessage(message)
      setTemporaryMessage(createTemporaryMessage('error', message))
    } finally {
      setIsCreating(false)
    }
  }

  useEffect(() => {
    const parsedClassroomId = Number(classroomId)
    const token = getAccessToken()

    if (!Number.isInteger(parsedClassroomId) || parsedClassroomId <= 0) {
      setErrorMessage('A turma informada é inválida.')
      setIsLoading(false)
      return
    }

    if (!token) {
      setErrorMessage('Sua sessão expirou. Entre novamente para ver as aulas.')
      setIsLoading(false)
      return
    }

    const accessToken = token
    let isActive = true

    async function loadLessons() {
      try {
        setIsLoading(true)
        setErrorMessage(null)
        const response = await getProfessorLessons(parsedClassroomId, accessToken)

        if (isActive) {
          setLessons(response)
        }
      } catch (error) {
        if (!isActive) {
          return
        }

        const message = error instanceof ApiRequestError
          ? error.message
          : 'Não foi possível carregar as aulas. Tente novamente.'
        setErrorMessage(message)
      } finally {
        if (isActive) {
          setIsLoading(false)
        }
      }
    }

    void loadLessons()

    return () => {
      isActive = false
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

  return (
    <div className="aulas-professor-layout">
      <ProfessorSidebar activeItem="turmas" />

      <main className="aulas-professor-page">
        <header className="aulas-professor-header">
          <div>
            <p className="aulas-professor-eyebrow">Conteúdos da turma</p>
            <h1>Aulas</h1>
            <p className="aulas-professor-subtitle">
              Organize as aulas e materiais para os alunos acompanharem a disciplina.
            </p>
          </div>
        </header>

        <TemporaryMessage message={temporaryMessage} />

        <section className="aulas-professor-summary" aria-label="Organização das aulas">
          <div className="aulas-professor-summary-icon" aria-hidden="true">▤</div>
          <div>
            <strong>Conteúdos organizados por aula</strong>
            <p>Em cada aula, você poderá reunir seções e blocos de conteúdo.</p>
          </div>
        </section>

        <section className="aulas-professor-list-section" aria-labelledby="aulas-professor-list-title">
          <div className="aulas-professor-list-heading">
            <h2 id="aulas-professor-list-title">Aulas da turma</h2>
            <span>{lessons.length} aulas</span>
          </div>

          {isLoading && (
            <div className="aulas-professor-feedback" role="status">
              Carregando aulas...
            </div>
          )}

          {errorMessage && (
            <div className="aulas-professor-feedback aulas-professor-feedback-error" role="alert">
              {errorMessage}
            </div>
          )}

          {!isLoading && !errorMessage && (
            <div className="aulas-professor-grid">
              {lessons.map((lesson) => (
                <Link
                  key={lesson.id}
                  to={`/app/turmas-professor/${classroomId}/aulas/${lesson.id}`}
                  className="aula-professor-card aula-professor-card-link"
                >
                  <div className="aula-professor-card-banner">
                    <span>Aula {lesson.ordem}</span>
                    <span className={lesson.ativo ? 'aula-professor-status' : 'aula-professor-status inactive'}>
                      {lesson.ativo ? 'Ativa' : 'Inativa'}
                    </span>
                  </div>
                  <div className="aula-professor-card-content">
                    <h3>{lesson.titulo}</h3>
                    <p>{lesson.descricao || 'Sem descrição cadastrada.'}</p>
                  </div>
                </Link>
              ))}

              <article className="aula-professor-card aula-professor-card-empty">
                <div className="aula-professor-empty-icon" aria-hidden="true">+</div>
                <h3>{lessons.length === 0 ? 'Nenhuma aula criada' : 'Nova aula'}</h3>
                <p>
                  {lessons.length === 0
                    ? 'Crie uma aula para começar a organizar os conteúdos da turma.'
                    : 'Adicione uma nova aula à organização desta turma.'}
                </p>
                <button type="button" className="aula-professor-empty-button" onClick={openCreateForm}>
                  Criar aula
                </button>
              </article>
            </div>
          )}
        </section>

        <footer className="aulas-professor-footer">
          <Link to={`/app/turmas-professor/${classroomId}`}>Voltar para a turma</Link>
        </footer>
      </main>

      {isCreateFormOpen && (
        <div className="aula-create-overlay" role="presentation">
          <section
            className="aula-create-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="aula-create-title"
          >
            <div className="aula-create-heading">
              <div>
                <p>Nova aula</p>
                <h2 id="aula-create-title">Organize o conteúdo da turma</h2>
              </div>
              <button
                type="button"
                className="aula-create-close"
                onClick={closeCreateForm}
                aria-label="Fechar formulário"
                disabled={isCreating}
              >
                ×
              </button>
            </div>

            <form className="aula-create-form" onSubmit={handleCreateLesson}>
              <label>
                <span>Título da aula</span>
                <input
                  type="text"
                  name="titulo"
                  value={lessonForm.titulo}
                  onChange={handleFormChange}
                  placeholder="Ex.: Introdução ao conteúdo"
                  autoFocus
                />
              </label>

              <label>
                <span>Descrição</span>
                <textarea
                  name="descricao"
                  value={lessonForm.descricao}
                  onChange={handleFormChange}
                  placeholder="Descreva brevemente o objetivo desta aula."
                  rows={4}
                />
              </label>

              <div className="aula-create-options">
                <label>
                  <span>Ordem</span>
                  <input
                    type="number"
                    name="ordem"
                    value={lessonForm.ordem}
                    onChange={handleFormChange}
                    min="1"
                    step="1"
                  />
                </label>

                <label className="aula-create-checkbox">
                  <input
                    type="checkbox"
                    checked={lessonForm.ativo}
                    onChange={handleActiveChange}
                  />
                  <span>Aula ativa para os alunos</span>
                </label>
              </div>

              {formErrorMessage && <p className="aula-create-error" role="alert">{formErrorMessage}</p>}

              <div className="aula-create-actions">
                <button
                  type="button"
                  className="aula-create-cancel"
                  onClick={closeCreateForm}
                  disabled={isCreating}
                >
                  Cancelar
                </button>
                <button type="submit" className="aula-create-submit" disabled={isCreating}>
                  {isCreating ? 'Salvando...' : 'Salvar aula'}
                </button>
              </div>
            </form>
          </section>
        </div>
      )}
    </div>
  )
}