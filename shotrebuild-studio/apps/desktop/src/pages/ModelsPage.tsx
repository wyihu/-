import { useEffect, useState } from 'react'
import { api } from '../services/api'

export function ModelsPage() {
  const [models, setModels] = useState<any[]>([])

  useEffect(() => {
    api.listModels().then(setModels).catch(console.error)
  }, [])

  return (
    <section>
      <h2>模型管理页</h2>
      <ul>
        {models.map((model) => (
          <li key={`${model.provider}-${model.model_key}`}>{model.provider}: {model.display_name}</li>
        ))}
      </ul>
    </section>
  )
}
