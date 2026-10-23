import type { LessonBlock } from '../../models'

import './LessonBlockRenderer.css'

interface LessonBlockRendererProps {
  block: LessonBlock
}

function getListItems(content: string): string[] {
  return content
    .split('\n')
    .map((item) => item.trim())
    .filter(Boolean)
}

function getTableRows(tableData: unknown): string[][] | null {
  if (!Array.isArray(tableData) || tableData.length === 0) {
    return null
  }

  const rows = tableData.map((row) => {
    if (!Array.isArray(row)) {
      return null
    }

    return row.map((cell) => String(cell ?? ''))
  })

  return rows.every((row): row is string[] => row !== null) ? rows : null
}

function getVideoEmbedUrl(videoUrl: string): string | null {
  let parsedUrl: URL

  try {
    parsedUrl = new URL(videoUrl)
  } catch {
    return null
  }

  const host = parsedUrl.hostname.replace(/^(www\.|m\.)/, '')
  const pathParts = parsedUrl.pathname.split('/').filter(Boolean)

  if (host === 'youtu.be' && pathParts[0]) {
    return `https://www.youtube.com/embed/${pathParts[0]}`
  }

  if (host === 'youtube.com') {
    const videoId = parsedUrl.searchParams.get('v')
    if (videoId) {
      return `https://www.youtube.com/embed/${videoId}`
    }

    if (['embed', 'shorts'].includes(pathParts[0]) && pathParts[1]) {
      return `https://www.youtube.com/embed/${pathParts[1]}`
    }
  }

  if (host === 'vimeo.com' && /^\d+$/.test(pathParts[0] ?? '')) {
    return `https://player.vimeo.com/video/${pathParts[0]}`
  }

  return null
}

export function LessonBlockRenderer({ block }: LessonBlockRendererProps) {
  const listItems = block.tipo === 'lista' ? getListItems(block.conteudo) : []
  const tableRows = block.tipo === 'tabela' ? getTableRows(block.tabela_json) : null
  const imageSource = block.arquivo_imagem || block.url_imagem
  const videoFile = block.arquivo_video
  const videoEmbedUrl = !videoFile && block.url_video ? getVideoEmbedUrl(block.url_video) : null
  const videoSource = videoFile || block.url_video

  return (
    <section className={`lesson-block-renderer lesson-block-renderer-${block.tipo}`}>
      {block.titulo && <h3>{block.titulo}</h3>}

      {block.tipo === 'texto' && block.conteudo && (
        <p className="lesson-block-renderer-text">{block.conteudo}</p>
      )}

      {block.tipo === 'lista' && (
        listItems.length > 0 ? (
          <ul className="lesson-block-renderer-list">
            {listItems.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        ) : (
          <p className="lesson-block-renderer-empty">Esta lista ainda não possui itens.</p>
        )
      )}

      {block.tipo === 'imagem' && imageSource && (
        <img
          className="lesson-block-renderer-image"
          src={imageSource}
          alt={block.titulo || 'Imagem do conteúdo da aula'}
        />
      )}

      {block.tipo === 'video' && videoEmbedUrl && (
        <iframe
          className="lesson-block-renderer-embed"
          src={videoEmbedUrl}
          title={block.titulo || 'Vídeo da aula'}
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; picture-in-picture"
          allowFullScreen
        />
      )}

      {block.tipo === 'video' && !videoEmbedUrl && videoSource && (
        <video className="lesson-block-renderer-video" controls src={videoSource}>
          Seu navegador não oferece suporte à reprodução de vídeo.
        </video>
      )}

      {block.tipo === 'tabela' && (
        tableRows ? (
          <div className="lesson-block-renderer-table-wrapper">
            <table className="lesson-block-renderer-table">
              <tbody>
                {tableRows.map((row, rowIndex) => (
                  <tr key={`${block.id}-${rowIndex}`}>
                    {row.map((cell, cellIndex) => (
                      <td key={`${block.id}-${rowIndex}-${cellIndex}`}>{cell}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="lesson-block-renderer-empty">Os dados desta tabela não estão disponíveis.</p>
        )
      )}
    </section>
  )
}