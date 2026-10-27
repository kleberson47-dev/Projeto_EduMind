import { useEffect, useState } from 'react'
import type { ChangeEvent, FormEvent } from 'react'
import { Link, useParams } from 'react-router-dom'

import { ProfessorSidebar, TemporaryMessage } from '../../components'
import { getAccessToken } from '../../features/auth'
import type { CreateLessonSectionRequest, LessonSection } from '../../models'
import {
  createLessonSection,
  deleteLessonSection,
  getProfessorLessonSections,
  updateLessonSection,
} from '../../services'
import {
  createTemporaryMessage,
  readTemporaryMessageAfterReload,
  saveTemporaryMessageAfterReload,
  TEMPORARY_MESSAGE_DURATION,
  type TemporaryMessage as TemporaryMessageData,
} from '../../utils'
import { ApiRequestError } from '../../utils/requests'

import './DetalhesAulaProfessorPage.css'

const initialSectionForm: CreateLessonSectionRequest = {
  titulo: '',
  descricao: '',
  ordem: 1,
  ativo: true,
}

export default function DetalhesAulaProfessorPage() {
  const { classroomId } = useParams()
  const { lessonId } = useParams()
  const [sections, setSections] = useState<LessonSection[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [isSectionFormOpen, setIsSectionFormOpen] = useState(false)
  const [editingSection, setEditingSection] = useState<LessonSection | null>(null)
  const [sectionForm, setSectionForm] = useState<CreateLessonSectionRequest>(
    initialSectionForm,
  )
  const [sectionFormError, setSectionFormError] = useState<string | null>(null)
  const [isCreatingSection, setIsCreatingSection] = useState(false)
  const [temporaryMessage, setTemporaryMessage] =
    useState<TemporaryMessageData | null>(() => readTemporaryMessageAfterReload())

  useEffect(() => {
    const parsedClassroomId = Number(classroomId)
    const parsedLessonId = Number(lessonId)
    const token = getAccessToken()

    if (!Number.isInteger(parsedClassroomId) || parsedClassroomId <= 0) {
      setErrorMessage('A turma informada é inválida.')
      setIsLoading(false)
      return
    }

    if (!Number.isInteger(parsedLessonId) || parsedLessonId <= 0) {
      setErrorMessage('A aula informada é inválida.')
      setIsLoading(false)
      return
    }

    if (!token) {
      setErrorMessage('Sua sessão expirou. Entre novamente para ver as seções.')
      setIsLoading(false)
      return
    }

    const accessToken = token
    let isActive = true

    async function loadSections() {
      try {
        setIsLoading(true)
        setErrorMessage(null)
        const response = await getProfessorLessonSections(
          parsedClassroomId,
          parsedLessonId,
          accessToken,
        )

        if (isActive) {
          setSections(response)
        }
      } catch (error) {
        if (!isActive) {
          return
        }

        setErrorMessage(
          error instanceof ApiRequestError
            ? error.message
            : 'Não foi possível carregar as seções. Tente novamente.',
        )
      } finally {
        if (isActive) {
          setIsLoading(false)
        }
      }
    }

    void loadSections()

    return () => {
      isActive = false
    }
  }, [classroomId, lessonId])

  const maxSectionOrder = editingSection ? sections.length : sections.length + 1

  const openSectionForm = () => {
    setEditingSection(null)
    setSectionForm({
      ...initialSectionForm,
      ordem: sections.length + 1,
    })
    setSectionFormError(null)
    setIsSectionFormOpen(true)
  }

  const openEditSectionForm = (section: LessonSection) => {
    setEditingSection(section)
    setSectionForm({
      titulo: section.titulo,
      descricao: section.descricao,
      ordem: section.ordem,
      ativo: section.ativo,
    })
    setSectionFormError(null)
    setIsSectionFormOpen(true)
  }

  const closeSectionForm = () => {
    if (isCreatingSection) {
      return
    }

    setIsSectionFormOpen(false)
    setEditingSection(null)
    setSectionForm(initialSectionForm)
    setSectionFormError(null)
  }

  const handleSectionFieldChange = (
    event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
  ) => {
    const { name, value } = event.target
    const fieldValue = name === 'ordem' ? Number(value) : value

    setSectionForm((currentForm) => ({
      ...currentForm,
      [name]: fieldValue,
    }))
  }

  const handleSectionStatusChange = (event: ChangeEvent<HTMLInputElement>) => {
    setSectionForm((currentForm) => ({
      ...currentForm,
      ativo: event.target.checked,
    }))
  }

  const handleSectionSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    if (isCreatingSection) {
      return
    }

    if (!sectionForm.titulo?.trim()) {
      setSectionFormError('Informe o título da seção.')
      return
    }

    if (!sectionForm.ordem || sectionForm.ordem < 1) {
      setSectionFormError('A ordem da seção deve ser maior que zero.')
      return
    }

    if (sectionForm.ordem > maxSectionOrder) {
      setSectionFormError(`A ordem da seção não pode ultrapassar ${maxSectionOrder}.`)
      return
    }

    const parsedClassroomId = Number(classroomId)
    const parsedLessonId = Number(lessonId)
    const token = getAccessToken()

    if (!Number.isInteger(parsedClassroomId) || parsedClassroomId <= 0) {
      setSectionFormError('A turma informada é inválida.')
      return
    }

    if (!Number.isInteger(parsedLessonId) || parsedLessonId <= 0) {
      setSectionFormError('A aula informada é inválida.')
      return
    }

    if (!token) {
      setSectionFormError('Sua sessão expirou. Entre novamente para salvar a seção.')
      return
    }

    try {
      setIsCreatingSection(true)
      setSectionFormError(null)

      const payload = {
        ...sectionForm,
        titulo: sectionForm.titulo.trim(),
      }

      if (editingSection) {
        const updatedSection = await updateLessonSection(
          parsedClassroomId,
          parsedLessonId,
          editingSection.id,
          payload,
          token,
        )

        setSections((currentSections) => currentSections
          .map((section) => section.id === updatedSection.id ? updatedSection : section)
          .sort((firstSection, secondSection) => firstSection.ordem - secondSection.ordem))
        if (payload.ordem !== undefined && payload.ordem !== editingSection.ordem) {
          saveTemporaryMessageAfterReload(
            createTemporaryMessage('success', 'Seção atualizada com sucesso.'),
          )
          window.location.reload()
        }
      } else {
        const createdSection = await createLessonSection(
          parsedClassroomId,
          parsedLessonId,
          payload,
          token,
        )

        setSections((currentSections) =>
          [...currentSections, createdSection].sort((firstSection, secondSection) =>
            firstSection.ordem - secondSection.ordem,
          ),
        )
        setTemporaryMessage(
          createTemporaryMessage('success', 'Seção criada com sucesso.'),
        )
      }

      setIsSectionFormOpen(false)
      setEditingSection(null)
      setSectionForm(initialSectionForm)
    } catch (error) {
      const message =
        error instanceof ApiRequestError
          ? error.message
          : 'Não foi possível salvar a seção. Tente novamente.'

      setSectionFormError(message)
      setTemporaryMessage(createTemporaryMessage('error', message))
    } finally {
      setIsCreatingSection(false)
    }
  }

  const handleDeleteSection = async (section: LessonSection) => {
    const confirmed = window.confirm(`Tem certeza que deseja excluir a seção "${section.titulo}"?`)

    if (!confirmed) {
      return
    }

    const parsedClassroomId = Number(classroomId)
    const parsedLessonId = Number(lessonId)
    const token = getAccessToken()

    if (!Number.isInteger(parsedClassroomId) || parsedClassroomId <= 0) {
      setErrorMessage('A turma informada é inválida.')
      return
    }

    if (!Number.isInteger(parsedLessonId) || parsedLessonId <= 0) {
      setErrorMessage('A aula informada é inválida.')
      return
    }

    if (!token) {
      setErrorMessage('Sua sessão expirou. Entre novamente para excluir a seção.')
      return
    }

    try {
      await deleteLessonSection(parsedClassroomId, parsedLessonId, section.id, token)
      setSections((currentSections) => currentSections.filter((currentSection) => currentSection.id !== section.id))
      saveTemporaryMessageAfterReload(
        createTemporaryMessage('success', 'Seção excluída com sucesso.'),
      )
      window.location.reload()
    } catch (error) {
      const message = error instanceof ApiRequestError
        ? error.message
        : 'Não foi possível excluir a seção. Tente novamente.'
      setErrorMessage(message)
      setTemporaryMessage(createTemporaryMessage('error', message))
    }
  }

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
    <div className="detalhes-aula-professor-layout">
      <ProfessorSidebar activeItem="turmas" />
      <TemporaryMessage message={temporaryMessage} />

      <main className="detalhes-aula-professor-page">
        <header className="detalhes-aula-professor-header">
          <p className="detalhes-aula-professor-eyebrow">Conteúdo da aula</p>
          <div className="detalhes-aula-professor-header-heading">
            <h1>Organize sua aula</h1>
            <Link
              to={`/app/turmas-professor/${classroomId}/aulas/${lessonId}/visualizar`}
              className="detalhes-aula-professor-preview-link"
            >
              Visualizar aula
            </Link>
          </div>
          <p>
            Crie seções para estruturar o conteúdo e adicione blocos de texto,
            imagens, vídeos ou tabelas em cada uma delas.
          </p>
        </header>

        <section className="detalhes-aula-professor-summary" aria-label="Estrutura da aula">
          <div className="detalhes-aula-professor-summary-icon" aria-hidden="true">▤</div>
          <div>
            <strong>Conteúdo dividido em seções</strong>
            <p>Organize o material em uma sequência clara para seus alunos.</p>
          </div>
        </section>

        <section className="detalhes-aula-professor-sections" aria-labelledby="detalhes-aula-sections-title">
          <div className="detalhes-aula-professor-sections-heading">
            <div>
              <p className="detalhes-aula-professor-label">Estrutura da aula</p>
              <h2 id="detalhes-aula-sections-title">Seções</h2>
              <p>Adicione seções para separar os temas e materiais desta aula.</p>
            </div>
            <span>{sections.length} seções</span>
          </div>

          {isLoading && (
            <div className="detalhes-aula-professor-feedback" role="status">
              Carregando seções...
            </div>
          )}

          {errorMessage && (
            <div
              className="detalhes-aula-professor-feedback detalhes-aula-professor-feedback-error"
              role="alert"
            >
              {errorMessage}
            </div>
          )}

          {!isLoading && !errorMessage && (
            <div className="detalhes-aula-professor-sections-grid">
              {sections.map((section) => (
                <article
                  key={section.id}
                  className="detalhes-aula-professor-section-card"
                >
                  <div className="detalhes-aula-professor-section-card-heading">
                    <span>Seção {section.ordem}</span>
                    <div className="detalhes-aula-professor-section-card-meta">
                      <span className={section.ativo ? 'detalhes-aula-professor-status' : 'detalhes-aula-professor-status inactive'}>
                        {section.ativo ? 'Ativa' : 'Inativa'}
                      </span>
                      <button
                        type="button"
                        className="detalhes-aula-professor-delete-button"
                        onClick={() => handleDeleteSection(section)}
                        aria-label={`Excluir seção ${section.titulo}`}
                      >
                        Excluir
                      </button>
                    </div>
                  </div>
                  <Link
                    to={`/app/turmas-professor/${classroomId}/aulas/${lessonId}/secoes/${section.id}`}
                    className="detalhes-aula-professor-section-card-link"
                  >
                    <h3>{section.titulo}</h3>
                    <p>{section.descricao || 'Sem descrição cadastrada.'}</p>
                    <span className="detalhes-aula-professor-section-card-footer">
                      {section.blocos.length} blocos de conteúdo
                    </span>
                  </Link>
                  <button
                    type="button"
                    className="detalhes-aula-professor-edit-button"
                    onClick={() => openEditSectionForm(section)}
                  >
                    Editar seção
                  </button>
                </article>
              ))}

              <article className="detalhes-aula-professor-empty-card">
                <span className="detalhes-aula-professor-empty-icon" aria-hidden="true">+</span>
                <h3>{sections.length === 0 ? 'Nenhuma seção criada' : 'Nova seção'}</h3>
                <p>Crie uma seção para começar a montar o conteúdo da aula.</p>
                <button type="button" onClick={openSectionForm}>Criar seção</button>
              </article>
            </div>
          )}
        </section>

        {isSectionFormOpen && (
          <div className="detalhes-aula-professor-modal-backdrop" role="presentation">
            <section
              className="detalhes-aula-professor-modal"
              aria-labelledby="nova-secao-title"
              role="dialog"
              aria-modal="true"
            >
              <div className="detalhes-aula-professor-modal-heading">
                <div>
                  <p>{editingSection ? 'Editar seção' : 'Nova seção'}</p>
                  <h2 id="nova-secao-title">
                    {editingSection ? 'Atualize os dados da seção' : 'Organize o próximo tema'}
                  </h2>
                </div>
                <button
                  type="button"
                  className="detalhes-aula-professor-close-button"
                  onClick={closeSectionForm}
                  aria-label="Fechar formulário de seção"
                  disabled={isCreatingSection}
                >
                  ×
                </button>
              </div>

              <form className="detalhes-aula-professor-form" onSubmit={handleSectionSubmit}>
                <label>
                  <span>Título da seção</span>
                  <input
                    type="text"
                    name="titulo"
                    value={sectionForm.titulo ?? ''}
                    onChange={handleSectionFieldChange}
                    placeholder="Ex.: Fundamentos do tema"
                    autoFocus
                  />
                </label>

                <label>
                  <span>Descrição</span>
                  <textarea
                    name="descricao"
                    value={sectionForm.descricao ?? ''}
                    onChange={handleSectionFieldChange}
                    placeholder="Descreva o que será estudado nesta seção."
                    rows={4}
                  />
                </label>

                <label>
                  <span>Ordem</span>
                  <input
                    type="number"
                    name="ordem"
                    value={sectionForm.ordem ?? 1}
                    onChange={handleSectionFieldChange}
                    min="1"
                    max={maxSectionOrder}
                  />
                </label>

                <label className="detalhes-aula-professor-checkbox-field">
                  <input
                    type="checkbox"
                    checked={sectionForm.ativo ?? true}
                    onChange={handleSectionStatusChange}
                  />
                  <span>Deixar seção ativa para os alunos</span>
                </label>

                {sectionFormError && <p className="detalhes-aula-professor-form-error" role="alert">{sectionFormError}</p>}

                <div className="detalhes-aula-professor-form-actions">
                  <button
                    type="button"
                    onClick={closeSectionForm}
                    disabled={isCreatingSection}
                  >
                    Cancelar
                  </button>
                  <button type="submit" disabled={isCreatingSection}>
                    {isCreatingSection
                      ? 'Salvando...'
                      : editingSection ? 'Salvar alterações' : 'Criar seção'}
                  </button>
                </div>
              </form>
            </section>
          </div>
        )}

        <footer className="detalhes-aula-professor-footer">
          <Link to={`/app/turmas-professor/${classroomId}/aulas`}>Voltar para as aulas</Link>
        </footer>
      </main>
    </div>
  )
}