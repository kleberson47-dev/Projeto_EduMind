import { useEffect, useState } from 'react'
import type { ChangeEvent, FormEvent } from 'react'
import { Link, useParams } from 'react-router-dom'

import { ProfessorSidebar, TemporaryMessage } from '../../components'
import { getAccessToken } from '../../features/auth'
import type { CreateLessonBlockRequest, LessonBlock, LessonBlockType } from '../../models'
import { createLessonBlock, getProfessorLessonBlocks, updateLessonBlock } from '../../services'
import {
  createTemporaryMessage,
  TEMPORARY_MESSAGE_DURATION,
  type TemporaryMessage as TemporaryMessageData,
} from '../../utils'
import { ApiRequestError } from '../../utils/requests'

import './DetalhesSecaoProfessorPage.css'

type VideoSource = 'arquivo' | 'link'

interface BlockFormState extends CreateLessonBlockRequest {
  tipo: LessonBlockType
  ordem: number
  ativo: boolean
  tabela_json: string
  arquivo_imagem: File | null
  arquivo_video: File | null
  fonte_video: VideoSource
}

const initialBlockForm: BlockFormState = {
  tipo: 'texto',
  titulo: '',
  conteudo: '',
  url_imagem: '',
  url_video: '',
  arquivo_imagem: null,
  arquivo_video: null,
  fonte_video: 'arquivo',
  tabela_json: '',
  ordem: 1,
  ativo: true,
}

function getFileName(fileUrl: string | null) {
  if (!fileUrl) {
    return ''
  }

  return decodeURIComponent(fileUrl.split('/').pop() ?? '')
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
  const [editingBlock, setEditingBlock] = useState<LessonBlock | null>(null)
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
    setEditingBlock(null)
    setBlockForm({
      ...initialBlockForm,
      ordem: Math.max(0, ...blocks.map((block) => block.ordem)) + 1,
    })
    setBlockFormError(null)
    setIsBlockFormOpen(true)
  }

  const openEditBlockForm = (block: LessonBlock) => {
    const hasTableData = block.tabela_json !== null && block.tabela_json !== undefined

    setEditingBlock(block)
    setBlockForm({
      tipo: block.tipo,
      titulo: block.titulo,
      conteudo: block.conteudo,
      url_imagem: block.url_imagem,
      url_video: block.url_video,
      arquivo_imagem: null,
      arquivo_video: null,
      fonte_video: block.url_video ? 'link' : 'arquivo',
      tabela_json: hasTableData ? JSON.stringify(block.tabela_json, null, 2) : '',
      ordem: block.ordem,
      ativo: block.ativo,
    })
    setBlockFormError(null)
    setIsBlockFormOpen(true)
  }

  const closeBlockForm = () => {
    if (isCreatingBlock) {
      return
    }

    setIsBlockFormOpen(false)
    setEditingBlock(null)
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

  const handleBlockFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const { name, files } = event.target
    const file = files?.[0] ?? null

    setBlockForm((currentForm) => ({
      ...currentForm,
      [name]: file,
    }))
  }

  const handleVideoSourceChange = (event: ChangeEvent<HTMLSelectElement>) => {
    const fonteVideo = event.target.value as VideoSource

    setBlockForm((currentForm) => ({
      ...currentForm,
      fonte_video: fonteVideo,
      arquivo_video: fonteVideo === 'link' ? null : currentForm.arquivo_video,
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
      tabela: 'tabela_json',
    }
    const requiredField = requiredFieldByType[blockForm.tipo]

    if (requiredField && !String(blockForm[requiredField] ?? '').trim()) {
      setBlockFormError(`Informe o conteúdo obrigatório para o bloco de ${blockTypeLabels[blockForm.tipo].toLowerCase()}.`)
      return
    }

    if (
      blockForm.tipo === 'imagem' &&
      !blockForm.arquivo_imagem &&
      !editingBlock?.arquivo_imagem
    ) {
      setBlockFormError('Selecione um arquivo de imagem para o bloco.')
      return
    }

    if (blockForm.tipo === 'video') {
      if (
        blockForm.fonte_video === 'arquivo' &&
        !blockForm.arquivo_video &&
        !editingBlock?.arquivo_video
      ) {
        setBlockFormError('Selecione um arquivo de vídeo para o bloco.')
        return
      }

      if (blockForm.fonte_video === 'link' && !blockForm.url_video?.trim()) {
        setBlockFormError('Informe a URL do vídeo para o bloco.')
        return
      }
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
      setBlockFormError('Sua sessão expirou. Entre novamente para salvar o bloco.')
      return
    }

    try {
      setIsCreatingBlock(true)
      setBlockFormError(null)

      const isVideoFile = blockForm.tipo === 'video' && blockForm.fonte_video === 'arquivo'

      const payload: CreateLessonBlockRequest = {
        tipo: blockForm.tipo,
        titulo: blockForm.titulo?.trim() ?? '',
        conteudo: blockForm.conteudo,
        url_imagem: blockForm.url_imagem,
        // O backend rejeita arquivo e URL juntos no mesmo vídeo.
        url_video: isVideoFile ? '' : blockForm.url_video,
        arquivo_imagem: blockForm.tipo === 'imagem' ? blockForm.arquivo_imagem : null,
        arquivo_video: isVideoFile ? blockForm.arquivo_video : null,
        tabela_json: tableData,
        ordem: blockForm.ordem,
        ativo: blockForm.ativo,
      }

      if (editingBlock) {
        const updatedBlock = await updateLessonBlock(
          parsedClassroomId,
          parsedLessonId,
          parsedSectionId,
          editingBlock.id,
          payload,
          token,
        )

        setBlocks((currentBlocks) => currentBlocks
          .map((block) => block.id === updatedBlock.id ? updatedBlock : block)
          .sort((firstBlock, secondBlock) => firstBlock.ordem - secondBlock.ordem))
        setTemporaryMessage(
          createTemporaryMessage('success', 'Bloco atualizado com sucesso.'),
        )
      } else {
        const createdBlock = await createLessonBlock(
          parsedClassroomId,
          parsedLessonId,
          parsedSectionId,
          payload,
          token,
        )

        setBlocks((currentBlocks) =>
          [...currentBlocks, createdBlock].sort(
            (firstBlock, secondBlock) => firstBlock.ordem - secondBlock.ordem,
          ),
        )
        setTemporaryMessage(
          createTemporaryMessage('success', 'Bloco criado com sucesso.'),
        )
      }

      setIsBlockFormOpen(false)
      setEditingBlock(null)
      setBlockForm(initialBlockForm)
    } catch (error) {
      const message =
        error instanceof ApiRequestError
          ? error.message
          : 'Não foi possível salvar o bloco. Tente novamente.'

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
                  <p>{block.conteudo || getFileName(block.arquivo_imagem) || getFileName(block.arquivo_video) || block.url_imagem || block.url_video || 'Conteúdo em tabela ou lista.'}</p>
                  <footer>Bloco {block.ordem}</footer>
                  <button
                    type="button"
                    className="detalhes-secao-professor-edit-button"
                    onClick={() => openEditBlockForm(block)}
                  >
                    Editar bloco
                  </button>
                </article>
              ))}

              <article className="detalhes-secao-professor-empty-card">
                <div aria-hidden="true">+</div>
                <h3>Novo bloco</h3>
                <p>Adicione outro bloco de conteúdo a esta seção.</p>
                <button type="button" onClick={openBlockForm}>Criar bloco</button>
              </article>
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
                  <p>{editingBlock ? 'Editar conteúdo' : 'Novo conteúdo'}</p>
                  <h2 id="novo-bloco-title">{editingBlock ? 'Editar bloco' : 'Criar bloco'}</h2>
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
                    <span>
                      Arquivo da imagem
                      {editingBlock?.arquivo_imagem && (
                        <small> atual: {getFileName(editingBlock.arquivo_imagem)}</small>
                      )}
                    </span>
                    <input type="file" name="arquivo_imagem" accept="image/*" onChange={handleBlockFileChange} />
                  </label>
                )}

                {blockForm.tipo === 'video' && (
                  <>
                    {!editingBlock?.arquivo_video && (
                      <label>
                        <span>Origem do vídeo</span>
                        <select value={blockForm.fonte_video} onChange={handleVideoSourceChange}>
                          <option value="arquivo">Enviar arquivo</option>
                          <option value="link">Usar link</option>
                        </select>
                      </label>
                    )}

                    {blockForm.fonte_video === 'arquivo' ? (
                      <label>
                        <span>
                          Arquivo do vídeo
                          {editingBlock?.arquivo_video && (
                            <small> atual: {getFileName(editingBlock.arquivo_video)}</small>
                          )}
                        </span>
                        <input type="file" name="arquivo_video" accept="video/mp4,video/webm" onChange={handleBlockFileChange} />
                      </label>
                    ) : (
                      <label>
                        <span>URL do vídeo</span>
                        <input type="url" name="url_video" value={blockForm.url_video} onChange={handleBlockFieldChange} placeholder="https://" />
                      </label>
                    )}
                  </>
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
                    {isCreatingBlock
                      ? 'Salvando...'
                      : editingBlock ? 'Salvar alterações' : 'Salvar bloco'}
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