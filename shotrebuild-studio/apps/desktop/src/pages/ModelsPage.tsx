import { useEffect, useMemo, useState } from 'react'
import { api } from '../services/api'

export function ModelsPage() {
  const [providers, setProviders] = useState<any[]>([])
  const [selectedProvider, setSelectedProvider] = useState('')
  const [models, setModels] = useState<any[]>([])
  const [modelKey, setModelKey] = useState('')
  const [displayName, setDisplayName] = useState('')
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
    }
  }

  async function loadModels(provider?: string) {
    setModels(await api.listModels(provider))
  }

  useEffect(() => {
    loadProviders().catch((e) => setError(String(e)))
  }, [])

  useEffect(() => {
    if (selectedProvider) {
      loadModels(selectedProvider).catch((e) => setError(String(e)))
    }
  }, [selectedProvider])

  async function createModel() {
    setError('')
    if (!selectedProviderRow) {
      setError('请先选择 Provider')
      return
    }
    if (!modelKey.trim() || !displayName.trim()) {
      setError('model_key 和 display_name 不能为空')
      return
    }
    await api.createModel({
      provider_id: selectedProviderRow.id,
      model_key: modelKey.trim(),
      display_name: displayName.trim()
    })
    setModelKey('')
    setDisplayName('')
    await loadModels(selectedProvider)
  }

  async function removeModel(modelId: number) {
    await api.deleteModel(modelId)
    await loadModels(selectedProvider)
  }

  return (
    <section>
      <h2>模型管理页</h2>
      <div>
        <select value={selectedProvider} onChange={(e) => setSelectedProvider(e.target.value)}>
          <option value="">请选择 Provider</option>
          {providers.map((provider) => (
            <option key={provider.id} value={provider.name}>{provider.name}</option>
          ))}
        </select>
        <input value={modelKey} onChange={(e) => setModelKey(e.target.value)} placeholder="model_key" />
        <input value={displayName} onChange={(e) => setDisplayName(e.target.value)} placeholder="display_name" />
        <button onClick={() => createModel()}>新增模型</button>
      </div>
      {error && <p style={{ color: 'crimson' }}>{error}</p>}
      <ul>
        {models.map((model) => (
          <li key={`${model.id}-${model.model_key}`}>
            {model.provider}: {model.display_name}
            <button onClick={() => removeModel(model.id)}>删除</button>
          </li>
        ))}
      </ul>
    </section>
  )
}
