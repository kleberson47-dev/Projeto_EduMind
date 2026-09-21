import { Link } from 'react-router-dom'

import './TurmasAlunoPage.css'

export default function TurmasAlunoPage() {
  return (
    <main className="turmas-aluno-page">
      <header className="turmas-aluno-header">
        <div>
          <p className="turmas-aluno-eyebrow">Área do aluno</p>
          <h1>Minhas turmas</h1>
          <p>Encontre suas disciplinas e acompanhe os conteúdos disponíveis.</p>
        </div>
      </header>

      <section className="turmas-aluno-summary" aria-label="Resumo das turmas">
        <span className="turmas-aluno-summary-icon" aria-hidden="true">▦</span>
        <div>
          <strong>Seu espaço de aprendizagem</strong>
          <p>Acesse cada turma para estudar aulas, acompanhar atividades e consultar notas.</p>
        </div>
      </section>

      <section className="turmas-aluno-list-section" aria-labelledby="turmas-aluno-title">
        <div className="turmas-aluno-list-heading">
          <h2 id="turmas-aluno-title">Turmas matriculadas</h2>
          <span>Em breve, suas turmas aparecerão aqui.</span>
        </div>

        <article className="turmas-aluno-empty-state">
          <div className="turmas-aluno-empty-icon" aria-hidden="true">+</div>
          <h3>Você ainda não participa de uma turma</h3>
          <p>Use o código compartilhado pelo professor para entrar em uma nova turma.</p>
          <button type="button" disabled>
            Entrar em uma turma
          </button>
        </article>
      </section>

      <footer className="turmas-aluno-footer">
        <Link to="/app/inicio_aluno">Voltar ao início</Link>
      </footer>
    </main>
  )
}