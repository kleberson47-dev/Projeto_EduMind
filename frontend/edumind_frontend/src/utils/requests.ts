import { buildApiUrl } from './api'

type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'

interface RequestOptions {
	method?: HttpMethod
	body?: unknown
	token?: string
	headers?: Record<string, string>
}

export class ApiRequestError extends Error {
	status: number
	details: unknown

	constructor(message: string, status: number, details: unknown) {
		super(message)
		this.name = 'ApiRequestError'
		this.status = status
		this.details = details
	}
}

export async function requestJson<T>(
	path: string,
	{ method = 'GET', body, token, headers = {} }: RequestOptions = {},
): Promise<T> {
	const isFormData = body instanceof FormData
	const requestHeaders: Record<string, string> = {
		Accept: 'application/json',
		...headers,
	}

	if (!isFormData) {
		requestHeaders['Content-Type'] = 'application/json'
	}

	if (token) {
		requestHeaders.Authorization = `Bearer ${token}`
	}

	const response = await fetch(buildApiUrl(path), {
		method,
		headers: requestHeaders,
		body: body == null ? undefined : isFormData ? body : JSON.stringify(body),
	})

	if (response.status === 204) {
		return undefined as T
	}

	const responseData = await response.json().catch(() => null)

	if (!response.ok) {
		const message =
			(responseData as { detail?: string } | null)?.detail ??
			'Nao foi possivel completar a requisicao.'

		throw new ApiRequestError(message, response.status, responseData)
	}

	return responseData as T
}
