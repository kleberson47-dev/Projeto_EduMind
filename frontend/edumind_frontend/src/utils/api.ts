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
	classrooms: {
		listCreate: '/classrooms/',
		studentList: '/classrooms/me/',
		join: '/classrooms/join/',
		studentDetail: (id: number) => `/classrooms/${id}/`,
		professorDetail: (id: number) => `/classrooms/professor/${id}/`,
		professorActivities: (id: number) => `/classrooms/${id}/activities/`,
		studentActivities: (id: number) => `/classrooms/${id}/activities/student/`,
		professorGrades: (id: number) => `/classrooms/${id}/grades/`,
		studentGrades: (id: number) => `/classrooms/${id}/grades/student/`,
		professorLessons: (id: number) => `/classrooms/${id}/lessons/`,
		studentLessons: (id: number) => `/classrooms/${id}/lessons/student/`,
		studentLessonDetail: (id: number, lessonId: number) =>
			`/classrooms/${id}/lessons/${lessonId}/`,
		professorSections: (id: number, lessonId: number) =>
			`/classrooms/${id}/lessons/${lessonId}/sections/`,
		studentSections: (id: number, lessonId: number) =>
			`/classrooms/${id}/lessons/${lessonId}/sections/student/`,
		professorBlocks: (id: number, lessonId: number, sectionId: number) =>
			`/classrooms/${id}/lessons/${lessonId}/sections/${sectionId}/blocks/`,
		studentBlocks: (id: number, lessonId: number, sectionId: number) =>
			`/classrooms/${id}/lessons/${lessonId}/sections/${sectionId}/blocks/student/`,
	},
}

export function buildApiUrl(path: string): string {
	return `${API_BASE_URL}${path}`
}
