import { useEffect, useMemo, useState } from 'react'
import { api } from '../services/api'

export function WorkflowsPage() {
  const [providers, setProviders] = useState<any[]>([])
  const [selectedProvider, setSelectedProvider] = useState('')
  const [fallbackProvider, setFallbackProvider] = useState('')
  const [models, setModels] = useState<any[]>([])
  const [workflows, setWorkflows] = useState<any[]>([])

  const [workflowKey, setWorkflowKey] = useState('')
  const [name, setName] = useState('')

  const [selectedModelKey, setSelectedModelKey] = useState('')
  const [fallbackModelKey, setFallbackModelKey] = useState('')
  const [selectedWorkflowId, setSelectedWorkflowId] = useState('')
  const [maxRetries, setMaxRetries] = useState('1')
  const [promptJson, setPromptJson] = useState('{"prompt":{}}')
  const [jobId, setJobId] = useState<number | null>(null)
  const [jobStatus, setJobStatus] = useState('')
  const [jobError, setJobError] = useState('')
  const [outputs, setOutputs] = useState('')
  const [error, setError] = useState('')

  const selectedProviderRow = useMemo(
    () => providers.find((p) => p.name === selectedProvider),
    [providers, selectedProvider]
  )

  async function loadProviders() {
    const rows = await api.listProviders()
    setProviders(rows)
    if (!selectedProvider && rows.length > 0) {
      setSelectedProvider(rows[0].name)
      setFallbackProvider(rows.find((x) => x.name !== rows[0].name)?.name ?? rows[0].name)
    }
  }

  async function loadDependentData(providerName: string) {
    const [modelRows, workflowRows] = await Promise.all([
      api.listModels(providerName),
      api.listWorkflows(providerName)
    ])
    setModels(modelRows)
    setWorkflows(workflowRows)
    setSelectedModelKey(modelRows[0]?.model_key ?? '')
    setSelectedWorkflowId(workflowRows[0]?.id ? String(workflowRows[0].id) : '')
  }

  useEffect(() => {
    loadProviders().catch((e) => setError(String(e)))
  }, [])

  useEffect(() => {
    if (selectedProvider) {
      loadDependentData(selectedProvider).catch((e) => setError(String(e)))
    }
  }, [selectedProvider])

  useEffect(() => {
    if (!jobId) return
    const timer = setInterval(async () => {
      try {
        const status = await api.getProviderJobStatus(jobId)
        setJobStatus(status.status)
        setJobError(status.error ?? '')
      } catch (e) {
        setError(String(e))
      }
    }, 2000)
    return () => clearInterval(timer)
  }, [jobId])

  async function createWorkflow() {
    setError('')
    if (!selectedProviderRow) {
      setError('请先选择 Provider')
      return
    }
    if (!workflowKey.trim() || !name.trim()) {
      setError('workflow_key 和 name 不能为空')
      return
    }
    await api.createWorkflow({
      provider_id: selectedProviderRow.id,
      workflow_key: workflowKey.trim(),
      name: name.trim()
    })
    setWorkflowKey('')
    setName('')
    await loadDependentData(selectedProvider)
  }


  async function removeWorkflow(workflowId: number) {
    await api.deleteWorkflow(workflowId)
    await loadDependentData(selectedProvider)
  }

  async function submitJob() {
    setError('')
    setJobError('')
    setOutputs('')
    if (selectedProvider !== 'comfyui') {
      setError('当前仅支持提交 ComfyUI 任务')
      return
    }
    if (!selectedModelKey || !selectedWorkflowId) {
      setError('请先选择模型和工作流')
      return
    }

    let parsedPrompt: Record<string, unknown>
    try {
      parsedPrompt = JSON.parse(promptJson)
    } catch {
      setError('Prompt JSON 格式错误')
      return
    }

    const submit = await api.submitProviderJob('comfyui', {
      workflow_id: Number(selectedWorkflowId),
      model_key: selectedModelKey,
      fallback_provider: fallbackProvider || undefined,
      fallback_model_key: fallbackModelKey || undefined,
      max_retries: Number(maxRetries || '0'),
      prompt: parsedPrompt
    })
    setJobId(submit.job_id)
    setJobStatus(submit.status)
  }

  async function retryJob() {
    if (!jobId) {
      setError('请先提交任务')
      return
    }
    const retried = await api.retryProviderJob(jobId, Number(maxRetries || '0'))
    setJobId(retried.job_id)
    setJobStatus(retried.status)
    setJobError('')
    setOutputs('')
  }

  async function loadOutputs() {
    if (!jobId) {
      setError('请先提交任务')
      return
    }
    const result = await api.getProviderJobOutputs(jobId)
    setOutputs(JSON.stringify(result.outputs, null, 2))
  }

  return (
    <section>
      <h2>Workflow 管理页</h2>
      <div>
        <select value={selectedProvider} onChange={(e) => setSelectedProvider(e.target.value)}>
          <option value="">请选择 Provider</option>
          {providers.map((provider) => (
            <option key={provider.id} value={provider.name}>{provider.name}</option>
          ))}
        </select>
        <input value={workflowKey} onChange={(e) => setWorkflowKey(e.target.value)} placeholder="workflow_key" />
        <input value={name} onChange={(e) => setName(e.target.value)} placeholder="name" />
        <button onClick={() => createWorkflow()}>新增 Workflow</button>
      </div>

      <h3>任务提交（ComfyUI）</h3>
      <div>
        <select value={selectedModelKey} onChange={(e) => setSelectedModelKey(e.target.value)}>
          <option value="">请选择模型</option>
          {models.map((model) => (
            <option key={model.id} value={model.model_key}>{model.display_name}</option>
          ))}
        </select>
        <select value={selectedWorkflowId} onChange={(e) => setSelectedWorkflowId(e.target.value)}>
          <option value="">请选择工作流</option>
          {workflows.map((workflow) => (
            <option key={workflow.id} value={workflow.id}>{workflow.name}</option>
          ))}
        </select>
      </div>
      <div>
        <label>Fallback Provider: </label>
        <select value={fallbackProvider} onChange={(e) => setFallbackProvider(e.target.value)}>
          <option value="">无</option>
          {providers.map((provider) => (
            <option key={provider.id} value={provider.name}>{provider.name}</option>
          ))}
        </select>
        <label>Fallback Model: </label>
        <input value={fallbackModelKey} onChange={(e) => setFallbackModelKey(e.target.value)} placeholder="fallback model_key" />
        <label>Max Retries: </label>
        <input value={maxRetries} onChange={(e) => setMaxRetries(e.target.value)} style={{ width: 60 }} />
      </div>
      <textarea
        value={promptJson}
        onChange={(e) => setPromptJson(e.target.value)}
        rows={8}
        style={{ width: '100%', marginTop: 8 }}
      />
      <div>
        <button onClick={() => submitJob()}>提交任务</button>
        <button onClick={() => retryJob()}>重试任务</button>
        <button onClick={() => loadOutputs()}>获取输出</button>
      </div>

      {jobId && <p>当前任务ID: {jobId} / 状态: {jobStatus}</p>}
      {jobError && <p style={{ color: 'crimson' }}>失败原因: {jobError}</p>}
      {error && <p style={{ color: 'crimson' }}>{error}</p>}
      {outputs && <pre>{outputs}</pre>}

      <ul>
        {workflows.map((workflow) => (
          <li key={`${workflow.id}-${workflow.workflow_key}`}>{workflow.provider ?? 'unknown'}: {workflow.name} <button onClick={() => removeWorkflow(workflow.id)}>删除</button></li>
        ))}
      </ul>
    </section>
  )
}
