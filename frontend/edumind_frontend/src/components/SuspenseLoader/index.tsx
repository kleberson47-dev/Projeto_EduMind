import './styles.css'

export function SuspenseLoader() {
  return (
    <div className="suspense-loader" role="status" aria-live="polite" aria-label="Carregando conteúdo">
      <div className="suspense-loader__dot" />
      <span>Carregando...</span>
    </div>
  )
}
