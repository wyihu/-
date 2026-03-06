import { useEffect, useState } from 'react'
import { api } from '../services/api'

export function WorkflowsPage() {
  const [workflows, setWorkflows] = useState<any[]>([])

  useEffect(() => {
    api.listWorkflows().then(setWorkflows).catch(console.error)
  }, [])

  return (
    <section>
      <h2>Workflow 管理页</h2>
      <ul>
        {workflows.map((workflow) => (
          <li key={workflow.workflow_key}>{workflow.provider}: {workflow.name}</li>
        ))}
      </ul>
    </section>
  )
}
