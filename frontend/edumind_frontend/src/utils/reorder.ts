export function ordenarPorOrdem<T extends { ordem: number }>(itens: T[]): T[] {
  return [...itens].sort((primeiro, segundo) => primeiro.ordem - segundo.ordem)
}
