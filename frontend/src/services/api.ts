// file: src/services/api.ts
export const API_BASE_URL = 'http://127.0.0.1:8000/api/v1'

export type ApiMeta = {
  source: string
  updated_at: string
  partial: boolean
  ai_available: boolean
}

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
    ...init,
  })

  if (!response.ok) {
    const detail = await response.text()
    throw new Error(detail || `API request failed: ${response.status}`)
  }

  if (response.status === 204) {
    return undefined as T
  }

  return (await response.json()) as T
}
