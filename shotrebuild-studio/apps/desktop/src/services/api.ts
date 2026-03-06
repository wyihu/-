const API_BASE = 'http://127.0.0.1:8000'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options
  })
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`)
  }
  return (await response.json()) as T
}

export const api = {
  health: () => request<{ status: string; service: string }>('/health'),
  listProviders: () => request<any[]>('/providers'),
  listModels: () => request<any[]>('/models'),
  listWorkflows: () => request<any[]>('/workflows'),
  listProjects: () => request<any[]>('/projects'),
  createProject: (payload: { name: string; description: string }) =>
    request('/projects', { method: 'POST', body: JSON.stringify(payload) })
}
