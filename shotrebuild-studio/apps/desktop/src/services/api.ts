const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'

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
  createProvider: (payload: { name: string; provider_type: string }) =>
    request('/providers', { method: 'POST', body: JSON.stringify(payload) }),
  listModels: () => request<any[]>('/models'),
  createModel: (payload: { provider_id: number; model_key: string; display_name: string }) =>
    request('/models', { method: 'POST', body: JSON.stringify(payload) }),
  listWorkflows: () => request<any[]>('/workflows'),
  createWorkflow: (payload: { provider_id: number; workflow_key: string; name: string }) =>
    request('/workflows', { method: 'POST', body: JSON.stringify(payload) }),
  listProjects: () => request<any[]>('/projects'),
  createProject: (payload: { name: string; description: string }) =>
    request('/projects', { method: 'POST', body: JSON.stringify(payload) })
}
