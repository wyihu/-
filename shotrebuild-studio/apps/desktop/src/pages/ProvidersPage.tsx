import { useEffect, useState } from 'react'
import { api } from '../services/api'

export function ProvidersPage() {
  const [providers, setProviders] = useState<any[]>([])

  useEffect(() => {
    api.listProviders().then(setProviders).catch(console.error)
  }, [])

  return (
    <section>
      <h2>Provider 管理页</h2>
      <ul>
        {providers.map((provider) => (
          <li key={provider.name}>{provider.name} - {provider.health.status}</li>
        ))}
      </ul>
    </section>
  )
}
