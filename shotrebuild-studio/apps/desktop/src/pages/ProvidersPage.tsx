import { useEffect, useState } from 'react'
import { api } from '../services/api'

export function ProvidersPage() {
  const [providers, setProviders] = useState<any[]>([])
  const [name, setName] = useState('')

  async function loadProviders() {
    setProviders(await api.listProviders())
  }

  useEffect(() => {
    loadProviders().catch(console.error)
  }, [])

  async function createProvider() {
    if (!name) return
    await api.createProvider({ name, provider_type: name })
    setName('')
    await loadProviders()
  }

  return (
    <section>
      <h2>Provider 管理页</h2>
      <div>
        <input value={name} onChange={(e) => setName(e.target.value)} placeholder="新增 provider 名称" />
        <button onClick={() => createProvider()}>新增 Provider</button>
      </div>
      <ul>
        {providers.map((provider) => (
          <li key={provider.id ?? provider.name}>
            #{provider.id} {provider.name} - {provider.health?.status ?? 'unknown'}
          </li>
        ))}
      </ul>
    </section>
  )
}
