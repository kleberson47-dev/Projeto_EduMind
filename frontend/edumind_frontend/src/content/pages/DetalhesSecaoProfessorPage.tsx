import { useEffect, useState } from 'react'
import type { ChangeEvent, FormEvent } from 'react'
import { Link, useParams } from 'react-router-dom'

import { ProfessorSidebar, TemporaryMessage } from '../../components'
import { getAccessToken } from '../../features/auth'
import type { CreateLessonBlockRequest, LessonBlock, LessonBlockType } from '../../models'
import { createLessonBlock, getProfessorLessonBlocks } from '../../services'
import {
  createTemporaryMessage,
  TEMPORARY_MESSAGE_DURATION,
  type TemporaryMessage as TemporaryMessageData,
} from '../../utils'
import { ApiRequestError } from '../../utils/requests'

import './DetalhesSecaoProfessorPage.css'

interface BlockFormState extends CreateLessonBlockRequest {
  tipo: LessonBlockType
  ordem: number
  ativo: boolean
  tabela_json: string
}

const initialBlockForm: BlockFormState = {
  tipo: 'texto',
  titulo: '',
  conteudo: '',
  url_imagem: '',
  url_video: '',
  tabela_json: '',
  ordem: 1,
  ativo: true,
}

const blockTypeLabels: Record<LessonBlockType, string> = {
  texto: 'Texto',
  imagem: 'Imagem',
  video: 'Vídeo',
  tabela: 'Tabela',
  lista: 'Lista',
}

export default function DetalhesSecaoProfessorPage() {
  const { classroomId, lessonId, sectionId } = useParams()
  const [blocks, setBlocks] = useState<LessonBlock[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [isBlockFormOpen, setIsBlockFormOpen] = useState(false)
  const [blockForm, setBlockForm] = useState<BlockFormState>(initialBlockForm)
  const [blockFormError, setBlockFormError] = useState<string | null>(null)
  const [isCreatingBlock, setIsCreatingBlock] = useState(false)
  const [temporaryMessage, setTemporaryMessage] =
    useState<TemporaryMessageData | null>(null)

  useEffect(() => {
    const parsedClassroomId = Number(classroomId)
    const parsedLessonId = Number(lessonId)
    const parsedSectionId = Number(sectionId)
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

    if (!Number.isInteger(parsedSectionId) || parsedSectionId <= 0) {
      setErrorMessage('A seção informada é inválida.')
      setIsLoading(false)
      return
    }

    if (!token) {
      setErrorMessage('Sua sessão expirou. Entre novamente para ver os blocos.')
      setIsLoading(false)
      return
    }

    const accessToken = token
    let isActive = true

    async function loadBlocks() {
      try {
        setIsLoading(true)
        setErrorMessage(null)
        const response = await getProfessorLessonBlocks(
          parsedClassroomId,
          parsedLessonId,
          parsedSectionId,
          accessToken,
        )

        if (isActive) {
          setBlocks(response)
        }
      } catch (error) {
        if (!isActive) {
          return
        }

        setErrorMessage(
          error instanceof ApiRequestError
            ? error.message
            : 'Não foi possível carregar os blocos. Tente novamente.',
        )
      } finally {
        if (isActive) {
          setIsLoading(false)
        }
      }
    }

    void loadBlocks()

    return () => {
      isActive = false
    }
  }, [classroomId, lessonId, sectionId])

  const openBlockForm = () => {
    setBlockForm(initialBlockForm)
    setBlockFormError(null)
    setIsBlockFormOpen(true)
  }

  const closeBlockForm = () => {
    setIsBlockFormOpen(false)
    setBlockForm(initialBlockForm)
    setBlockFormError(null)
  }

  const handleBlockFieldChange = (
    event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>,
  ) => {
    const { name, value } = event.target
    const fieldValue = name === 'ordem' ? Number(value) : value

    setBlockForm((currentForm) => ({
      ...currentForm,
      [name]: fieldValue,
    }))
  }

  const handleBlockStatusChange = (event: ChangeEvent<HTMLInputElement>) => {
    setBlockForm((currentForm) => ({
      ...currentForm,
      ativo: event.target.checked,
    }))
  }

  const handleBlockSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    if (isCreatingBlock) {
      return
    }

    if (!blockForm.ordem || blockForm.ordem < 1) {
      setBlockFormError('A ordem do bloco deve ser maior que zero.')
      return
    }

    const requiredFieldByType: Partial<Record<LessonBlockType, keyof BlockFormState>> = {
      texto: 'conteudo',
      imagem: 'url_imagem',
      video: 'url_video',
      tabela: 'tabela_json',
    }
    const requiredField = requiredFieldByType[blockForm.tipo]

    if (requiredField && !String(blockForm[requiredField] ?? '').trim()) {
      setBlockFormError(`Informe o conteúdo obrigatório para o bloco de ${blockTypeLabels[blockForm.tipo].toLowerCase()}.`)
      return
    }

    let tableData: unknown = undefined
    if (blockForm.tipo === 'tabela') {
      try {
        tableData = JSON.parse(blockForm.tabela_json)
      } catch {
        setBlockFormError('Informe dados da tabela em um JSON válido.')
        return
      }
    }

    const parsedClassroomId = Number(classroomId)
    const parsedLessonId = Number(lessonId)
    const parsedSectionId = Number(sectionId)
    const token = getAccessToken()

    if (!Number.isInteger(parsedClassroomId) || parsedClassroomId <= 0) {
      setBlockFormError('A turma informada é inválida.')
      return
    }

    if (!Number.isInteger(parsedLessonId) || parsedLessonId <= 0) {
      setBlockFormError('A aula informada é inválida.')
      return
    }

    if (!Number.isInteger(parsedSectionId) || parsedSectionId <= 0) {
      setBlockFormError('A seção informada é inválida.')
      return
    }

    if (!token) {
      setBlockFormError('Sua sessão expirou. Entre novamente para criar o bloco.')
      return
    }

    try {
      setIsCreatingBlock(true)
      setBlockFormError(null)

      const createdBlock = await createLessonBlock(
        parsedClassroomId,
        parsedLessonId,
        parsedSectionId,
        {
          tipo: blockForm.tipo,
          titulo: blockForm.titulo?.trim() ?? '',
          conteudo: blockForm.conteudo,
          url_imagem: blockForm.url_imagem,
          url_video: blockForm.url_video,
          tabela_json: tableData,
          ordem: blockForm.ordem,
          ativo: blockForm.ativo,
        },
        token,
      )

      setBlocks((currentBlocks) =>
        [...currentBlocks, createdBlock].sort(
          (firstBlock, secondBlock) => firstBlock.ordem - secondBlock.ordem,
        ),
      )
      closeBlockForm()
      setTemporaryMessage(
        createTemporaryMessage('success', 'Bloco criado com sucesso.'),
      )
    } catch (error) {
      const message =
        error instanceof ApiRequestError
          ? error.message
          : 'Não foi possível criar o bloco. Tente novamente.'

      setBlockFormError(message)
      setTemporaryMessage(createTemporaryMessage('error', message))
    } finally {
      setIsCreatingBlock(false)
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
    <div className="detalhes-secao-professor-layout">
      <ProfessorSidebar activeItem="turmas" />
      <TemporaryMessage message={temporaryMessage} />

      <main className="detalhes-secao-professor-page">
        <header className="detalhes-secao-professor-header">
          <p>Conteúdo da seção</p>
          <h1>Monte os blocos de conteúdo</h1>
          <span>
            Adicione textos, imagens, vídeos, tabelas e listas para apresentar o tema aos alunos.
          </span>
        </header>

        <section className="detalhes-secao-professor-summary" aria-label="Estrutura da seção">
          <div aria-hidden="true">▤</div>
          <div>
            <strong>Conteúdo organizado em blocos</strong>
            <p>Combine diferentes formatos para construir uma explicação clara e sequencial.</p>
          </div>
        </section>

        <section className="detalhes-secao-professor-blocks" aria-labelledby="detalhes-secao-blocks-title">
          <div className="detalhes-secao-professor-blocks-heading">
            <div>
              <p>Estrutura da seção</p>
              <h2 id="detalhes-secao-blocks-title">Blocos de conteúdo</h2>
              <span>Organize cada parte do material na ordem em que os alunos devem estudar.</span>
            </div>
            <span>{blocks.length} {blocks.length === 1 ? 'bloco' : 'blocos'}</span>
          </div>

          {isLoading && (
            <p className="detalhes-secao-professor-status">Carregando blocos...</p>
          )}

          {!isLoading && errorMessage && (
            <p className="detalhes-secao-professor-status detalhes-secao-professor-status-error">
              {errorMessage}
            </p>
          )}

          {!isLoading && !errorMessage && blocks.length === 0 && (
            <article className="detalhes-secao-professor-empty-card">
              <div aria-hidden="true">+</div>
              <h3>Nenhum bloco criado</h3>
              <p>Crie um bloco para começar a desenvolver o conteúdo desta seção.</p>
              <button type="button" onClick={openBlockForm}>Criar bloco</button>
            </article>
          )}

          {!isLoading && !errorMessage && blocks.length > 0 && (
            <div className="detalhes-secao-professor-block-list">
              {blocks.map((block) => (
                <article key={block.id} className="detalhes-secao-professor-block-card">
                  <div>
                    <span>{block.tipo}</span>
                    {!block.ativo && <span>Inativo</span>}
                  </div>
                  <h3>{block.titulo || `Bloco de ${block.tipo}`}</h3>
                  <p>{block.conteudo || block.url_imagem || block.url_video || 'Conteúdo em tabela ou lista.'}</p>
                  <footer>Bloco {block.ordem}</footer>
                </article>
              ))}
            </div>
          )}
        </section>

        {isBlockFormOpen && (
          <div className="detalhes-secao-professor-modal-backdrop" role="presentation">
            <section
              className="detalhes-secao-professor-modal"
              role="dialog"
              aria-modal="true"
              aria-labelledby="novo-bloco-title"
            >
              <header>
                <div>
                  <p>Novo conteúdo</p>
                  <h2 id="novo-bloco-title">Criar bloco</h2>
                </div>
                <button type="button" onClick={closeBlockForm} aria-label="Fechar formulário" disabled={isCreatingBlock}>×</button>
              </header>

              <form onSubmit={handleBlockSubmit}>
                <label>
                  <span>Tipo de bloco</span>
                  <select name="tipo" value={blockForm.tipo} onChange={handleBlockFieldChange}>
                    {Object.entries(blockTypeLabels).map(([value, label]) => (
                      <option key={value} value={value}>{label}</option>
                    ))}
                  </select>
                </label>

                <label>
                  <span>Título <small>opcional</small></span>
                  <input name="titulo" value={blockForm.titulo} onChange={handleBlockFieldChange} />
                </label>

                {(blockForm.tipo === 'texto' || blockForm.tipo === 'lista') && (
                  <label>
                    <span>{blockForm.tipo === 'lista' ? 'Itens da lista' : 'Conteúdo'}</span>
                    <textarea name="conteudo" value={blockForm.conteudo} onChange={handleBlockFieldChange} rows={5} />
                  </label>
                )}

                {blockForm.tipo === 'imagem' && (
                  <label>
                    <span>URL da imagem</span>
                    <input type="url" name="url_imagem" value={blockForm.url_imagem} onChange={handleBlockFieldChange} placeholder="https://" />
                  </label>
                )}

                {blockForm.tipo === 'video' && (
                  <label>
                    <span>URL do vídeo</span>
                    <input type="url" name="url_video" value={blockForm.url_video} onChange={handleBlockFieldChange} placeholder="https://" />
                  </label>
                )}

                {blockForm.tipo === 'tabela' && (
                  <label>
                    <span>Dados da tabela em JSON</span>
                    <textarea name="tabela_json" value={blockForm.tabela_json} onChange={handleBlockFieldChange} rows={5} />
                  </label>
                )}

                <div className="detalhes-secao-professor-form-row">
                  <label>
                    <span>Ordem</span>
                    <input type="number" name="ordem" min="1" value={blockForm.ordem} onChange={handleBlockFieldChange} />
                  </label>
                  <label className="detalhes-secao-professor-checkbox">
                    <input type="checkbox" checked={blockForm.ativo} onChange={handleBlockStatusChange} />
                    <span>Bloco ativo</span>
                  </label>
                </div>

                {blockFormError && <p className="detalhes-secao-professor-form-error">{blockFormError}</p>}

                <footer>
                  <button type="button" onClick={closeBlockForm} disabled={isCreatingBlock}>Cancelar</button>
                  <button type="submit" disabled={isCreatingBlock}>
                    {isCreatingBlock ? 'Salvando...' : 'Salvar bloco'}
                  </button>
                </footer>
              </form>
            </section>
          </div>
        )}

        <footer className="detalhes-secao-professor-footer">
          <Link to={`/app/turmas-professor/${classroomId}/aulas/${lessonId}`}>
            Voltar para as seções
          </Link>
        </footer>
      </main>
    </div>
  )
}