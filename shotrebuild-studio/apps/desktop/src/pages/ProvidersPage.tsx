import { useEffect, useState } from 'react'
import { api } from '../services/api'

export function ProvidersPage() {
  const [providers, setProviders] = useState<any[]>([])
  const [name, setName] = useState('')
  const [error, setError] = useState('')

  async function loadProviders() {
    setProviders(await api.listProviders())
  }

  useEffect(() => {
    loadProviders().catch((e) => setError(String(e)))
  }, [])

  async function createProvider() {
    if (!name.trim()) {
      setError('provider name 不能为空')
      return
    }
    await api.createProvider({ name: name.trim(), provider_type: name.trim() })
    setName('')
    setError('')
    await loadProviders()
  }

  async function toggleProvider(provider: any) {
    await api.updateProvider(provider.name, { enabled: provider.enabled ? 0 : 1 })
    await loadProviders()
  }

  async function removeProvider(providerName: string) {
    await api.deleteProvider(providerName)
    await loadProviders()
  }

  return (
    <section>
      <h2>Provider 管理页</h2>
      <div>
        <input value={name} onChange={(e) => setName(e.target.value)} placeholder="新增 provider 名称" />
        <button onClick={() => createProvider()}>新增 Provider</button>
      </div>
      {error && <p style={{ color: 'crimson' }}>{error}</p>}
      <ul>
        {providers.map((provider) => (
          <li key={provider.id ?? provider.name}>
            #{provider.id} {provider.name} - {provider.health?.status ?? 'unknown'} / enabled:{provider.enabled}
            <button onClick={() => toggleProvider(provider)}>启停</button>
            <button onClick={() => removeProvider(provider.name)}>删除</button>
          </li>
        ))}
      </ul>
    </section>
  )
}
