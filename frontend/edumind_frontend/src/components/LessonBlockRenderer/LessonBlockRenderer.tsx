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

export function LessonBlockRenderer({ block }: LessonBlockRendererProps) {
  const listItems = block.tipo === 'lista' ? getListItems(block.conteudo) : []
  const tableRows = block.tipo === 'tabela' ? getTableRows(block.tabela_json) : null

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

      {block.tipo === 'imagem' && block.url_imagem && (
        <img
          className="lesson-block-renderer-image"
          src={block.url_imagem}
          alt={block.titulo || 'Imagem do conteúdo da aula'}
        />
      )}

      {block.tipo === 'video' && block.url_video && (
        <video className="lesson-block-renderer-video" controls>
          <source src={block.url_video} />
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