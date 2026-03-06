import { useEffect, useState } from 'react'
import { api } from '../services/api'

export function ModelsPage() {
  const [models, setModels] = useState<any[]>([])
  const [providerId, setProviderId] = useState('1')
  const [modelKey, setModelKey] = useState('')
  const [displayName, setDisplayName] = useState('')

  async function loadModels() {
    setModels(await api.listModels())
  }

  useEffect(() => {
    loadModels().catch(console.error)
  }, [])

  async function createModel() {
    if (!modelKey || !displayName) return
    await api.createModel({ provider_id: Number(providerId), model_key: modelKey, display_name: displayName })
    setModelKey('')
    setDisplayName('')
    await loadModels()
  }

  return (
    <section>
      <h2>模型管理页</h2>
      <div>
        <input value={providerId} onChange={(e) => setProviderId(e.target.value)} placeholder="provider_id" />
        <input value={modelKey} onChange={(e) => setModelKey(e.target.value)} placeholder="model_key" />
        <input value={displayName} onChange={(e) => setDisplayName(e.target.value)} placeholder="display_name" />
        <button onClick={() => createModel()}>新增模型</button>
      </div>
      <ul>
        {models.map((model) => (
          <li key={`${model.id}-${model.model_key}`}>{model.provider}: {model.display_name}</li>
        ))}
      </ul>
    </section>
  )
}
