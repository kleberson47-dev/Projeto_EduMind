import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'

import { LessonBlockRenderer } from '../../components'
import type { Lesson, LessonBlock, LessonSection } from '../../models'
import { getAccessToken } from '../../features/auth'
import {
  getProfessorLessonBlocks,
  getProfessorLessonSections,
  getProfessorLessons,
} from '../../services'
import { ApiRequestError } from '../../utils/requests'

import './VisualizarAulaProfessorPage.css'

export default function VisualizarAulaProfessorPage() {
  const { classroomId, lessonId } = useParams()
  const editLessonPath = `/app/turmas-professor/${classroomId}/aulas/${lessonId}`
  const [lesson, setLesson] = useState<Lesson | null>(null)
  const [sections, setSections] = useState<LessonSection[]>([])
  const [activeSectionId, setActiveSectionId] = useState<number | null>(null)
  const [blocks, setBlocks] = useState<LessonBlock[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isLoadingBlocks, setIsLoadingBlocks] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [blocksErrorMessage, setBlocksErrorMessage] = useState<string | null>(null)

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
      setErrorMessage('Sua sessão expirou. Entre novamente para pré-visualizar a aula.')
      setIsLoading(false)
      return
    }

    const accessToken = token
    let isActive = true

    async function loadLessonPreview() {
      try {
        setIsLoading(true)
        setErrorMessage(null)

        const [lessons, loadedSections] = await Promise.all([
          getProfessorLessons(parsedClassroomId, accessToken),
          getProfessorLessonSections(
            parsedClassroomId,
            parsedLessonId,
            accessToken,
          ),
        ])
        const loadedLesson = lessons.find((item) => item.id === parsedLessonId)

        if (!loadedLesson) {
          throw new Error('A aula não foi encontrada nesta turma.')
        }

        if (isActive) {
          setLesson(loadedLesson)
          setSections(loadedSections)
          setActiveSectionId(loadedSections[0]?.id ?? null)
        }
      } catch (error) {
        if (!isActive) {
          return
        }

        setErrorMessage(
          error instanceof ApiRequestError
            ? error.message
            : error instanceof Error
              ? error.message
              : 'Não foi possível carregar a pré-visualização da aula.',
        )
      } finally {
        if (isActive) {
          setIsLoading(false)
        }
      }
    }

    void loadLessonPreview()

    return () => {
      isActive = false
    }
  }, [classroomId, lessonId])

  useEffect(() => {
    const parsedClassroomId = Number(classroomId)
    const parsedLessonId = Number(lessonId)
    const token = getAccessToken()

    if (!activeSectionId || !token) {
      setBlocks([])
      return
    }

    if (!Number.isInteger(parsedClassroomId) || !Number.isInteger(parsedLessonId)) {
      setBlocks([])
      return
    }

    const sectionId = activeSectionId
    const accessToken = token
    let isActive = true

    async function loadBlocks() {
      try {
        setIsLoadingBlocks(true)
        setBlocksErrorMessage(null)

        const response = await getProfessorLessonBlocks(
          parsedClassroomId,
          parsedLessonId,
          sectionId,
          accessToken,
        )

        if (isActive) {
          setBlocks(response)
        }
      } catch (error) {
        if (!isActive) {
          return
        }

        setBlocks([])
        setBlocksErrorMessage(
          error instanceof ApiRequestError
            ? error.message
            : 'Não foi possível carregar os blocos desta seção.',
        )
      } finally {
        if (isActive) {
          setIsLoadingBlocks(false)
        }
      }
    }

    void loadBlocks()

    return () => {
      isActive = false
    }
  }, [activeSectionId, classroomId, lessonId])

  const activeSection = sections.find((section) => section.id === activeSectionId)
  const activeSectionIndex = sections.findIndex((section) => section.id === activeSectionId)
  const previousSection = activeSectionIndex > 0 ? sections[activeSectionIndex - 1] : null
  const nextSection =
    activeSectionIndex >= 0 && activeSectionIndex < sections.length - 1
      ? sections[activeSectionIndex + 1]
      : null

  const selectSection = (sectionId: number) => {
    setActiveSectionId(sectionId)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
    <div className="visualizar-aula-professor-page">
      <header className="visualizar-aula-professor-topbar">
        <Link to={editLessonPath} className="visualizar-aula-professor-back-link">
          <span aria-hidden="true">&#8592;</span>
          Voltar para edição
        </Link>
        <div className="visualizar-aula-professor-title">
          <p>Pré-visualização da aula</p>
          <h1>{lesson?.titulo ?? 'Carregando aula'}</h1>
        </div>
        <span className="visualizar-aula-professor-status">Modo professor</span>
      </header>

      <main className="visualizar-aula-professor-main">
        <section className="visualizar-aula-professor-hero" aria-labelledby="preview-title">
          <p>Conteúdo da aula</p>
          <h2 id="preview-title">{lesson?.titulo ?? 'Pré-visualização da aula'}</h2>
        </section>

        <section className="visualizar-aula-professor-reader" aria-label="Leitor da aula">
          <aside className="visualizar-aula-professor-navigation" aria-label="Navegação das seções">
            <p>Seções da aula</p>
            {sections.map((section, index) => (
              <button
                key={section.id}
                type="button"
                className={section.id === activeSectionId ? 'is-active' : undefined}
                onClick={() => selectSection(section.id)}
              >
                {index + 1}. {section.titulo}
              </button>
            ))}
          </aside>

          <article className="visualizar-aula-professor-content">
            {isLoading ? (
              <p className="visualizar-aula-professor-state">Carregando aula...</p>
            ) : errorMessage ? (
              <p className="visualizar-aula-professor-state is-error">{errorMessage}</p>
            ) : !activeSection ? (
              <p className="visualizar-aula-professor-state">
                Esta aula ainda não possui seções para pré-visualização.
              </p>
            ) : (
              <>
                <p className="visualizar-aula-professor-content-label">
                  Seção {activeSection.ordem}
                </p>
                <h2>{activeSection.titulo}</h2>
                <p>{activeSection.descricao || 'Esta seção ainda não possui uma descrição.'}</p>

                {isLoadingBlocks ? (
                  <p className="visualizar-aula-professor-state">Carregando conteúdo...</p>
                ) : blocksErrorMessage ? (
                  <p className="visualizar-aula-professor-state is-error">
                    {blocksErrorMessage}
                  </p>
                ) : blocks.length === 0 ? (
                  <p className="visualizar-aula-professor-state">
                    Esta seção ainda não possui blocos de conteúdo.
                  </p>
                ) : (
                  <div className="visualizar-aula-professor-block-list">
                    {blocks.map((block) => <LessonBlockRenderer key={block.id} block={block} />)}
                  </div>
                )}
              </>
            )}
          </article>
        </section>

        <nav className="visualizar-aula-professor-controls" aria-label="Navegação entre seções">
          <button
            type="button"
            disabled={!previousSection}
            onClick={() => previousSection && selectSection(previousSection.id)}
          >
            Voltar
          </button>
          <button
            type="button"
            disabled={!nextSection}
            onClick={() => nextSection && selectSection(nextSection.id)}
          >
            Avançar
          </button>
        </nav>
      </main>
    </div>
  )
}