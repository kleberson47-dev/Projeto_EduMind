export const API_BASE_URL = 'http://localhost:8000/api/v1'

export const API_ENDPOINTS = {
	accounts: {
		token: '/accounts/token/',
		refreshToken: '/accounts/token/refresh/',
		me: '/accounts/me/',
		criarUsuario: '/accounts/criar_usuario/',
		editarUsuario: (id: number) => `/accounts/${id}/editar_usuario/`,
		excluirUsuario: (id: number) => `/accounts/${id}/excluir_usuario/`,
	},
}

export function buildApiUrl(path: string): string {
	return `${API_BASE_URL}${path}`
}
