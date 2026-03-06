const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options
  })
  if (!response.ok) {
    const detail = await response.text()
    throw new Error(`Request failed: ${response.status} ${detail}`)
  }
  return (await response.json()) as T
}

export const api = {
  health: () => request<{ status: string; service: string }>('/health'),

  listProviders: () => request<any[]>('/providers'),
  createProvider: (payload: { name: string; provider_type: string }) =>
    request('/providers', { method: 'POST', body: JSON.stringify(payload) }),
  updateProvider: (name: string, payload: { provider_type?: string; enabled?: number; config_json?: string }) =>
    request(`/providers/${name}`, { method: 'PUT', body: JSON.stringify(payload) }),
  deleteProvider: (name: string) => request(`/providers/${name}`, { method: 'DELETE' }),

  comfyHealth: () => request<any>('/providers/comfyui/health'),
  comfyModels: () => request<any[]>('/providers/comfyui/models'),

  listModels: (provider?: string) => request<any[]>(provider ? `/models?provider=${provider}` : '/models'),
  createModel: (payload: { provider_id: number; model_key: string; display_name: string }) =>
    request('/models', { method: 'POST', body: JSON.stringify(payload) }),
  updateModel: (modelId: number, payload: { model_key?: string; display_name?: string; capabilities?: string; is_default?: number }) =>
    request(`/models/${modelId}`, { method: 'PUT', body: JSON.stringify(payload) }),
  deleteModel: (modelId: number) => request(`/models/${modelId}`, { method: 'DELETE' }),

  listWorkflows: (provider?: string) => request<any[]>(provider ? `/workflows?provider=${provider}` : '/workflows'),
  createWorkflow: (payload: { provider_id: number; workflow_key: string; name: string }) =>
    request('/workflows', { method: 'POST', body: JSON.stringify(payload) }),
  updateWorkflow: (workflowId: number, payload: { workflow_key?: string; name?: string; definition_json?: string }) =>
    request(`/workflows/${workflowId}`, { method: 'PUT', body: JSON.stringify(payload) }),
  deleteWorkflow: (workflowId: number) => request(`/workflows/${workflowId}`, { method: 'DELETE' }),

  submitProviderJob: (
    provider: string,
    payload: {
      workflow_id?: number
      model_key?: string
      fallback_provider?: string
      fallback_model_key?: string
      max_retries?: number
      prompt: Record<string, unknown>
    }
  ) => request(`/providers/${provider}/jobs`, { method: 'POST', body: JSON.stringify(payload) }),
  retryProviderJob: (jobId: number, max_retries?: number) =>
    request(`/provider_jobs/${jobId}/retry`, { method: 'POST', body: JSON.stringify({ max_retries }) }),
  listProviderJobs: () => request<any[]>('/provider_jobs'),
  getProviderJobStatus: (jobId: number) => request<any>(`/provider_jobs/${jobId}/status`),
  getProviderJobOutputs: (jobId: number) => request<any>(`/provider_jobs/${jobId}/outputs`),

  listProjects: () => request<any[]>('/projects'),
  createProject: (payload: { name: string; description: string }) =>
    request('/projects', { method: 'POST', body: JSON.stringify(payload) })
}
