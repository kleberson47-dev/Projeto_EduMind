export function formatDate(dateValue: string): string {
  const date = new Date(dateValue)
  return date.toLocaleDateString('pt-BR')
}
