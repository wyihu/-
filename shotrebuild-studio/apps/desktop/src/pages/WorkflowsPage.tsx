import { useEffect, useState } from 'react'
import { api } from '../services/api'

export function WorkflowsPage() {
  const [workflows, setWorkflows] = useState<any[]>([])
  const [providerId, setProviderId] = useState('1')
  const [workflowKey, setWorkflowKey] = useState('')
  const [name, setName] = useState('')

  async function loadWorkflows() {
    setWorkflows(await api.listWorkflows())
  }

  useEffect(() => {
    loadWorkflows().catch(console.error)
  }, [])

  async function createWorkflow() {
    if (!workflowKey || !name) return
    await api.createWorkflow({ provider_id: Number(providerId), workflow_key: workflowKey, name })
    setWorkflowKey('')
    setName('')
    await loadWorkflows()
  }

  return (
    <section>
      <h2>Workflow 管理页</h2>
      <div>
        <input value={providerId} onChange={(e) => setProviderId(e.target.value)} placeholder="provider_id" />
        <input value={workflowKey} onChange={(e) => setWorkflowKey(e.target.value)} placeholder="workflow_key" />
        <input value={name} onChange={(e) => setName(e.target.value)} placeholder="name" />
        <button onClick={() => createWorkflow()}>新增 Workflow</button>
      </div>
      <ul>
        {workflows.map((workflow) => (
          <li key={`${workflow.id}-${workflow.workflow_key}`}>{workflow.provider ?? 'unknown'}: {workflow.name}</li>
        ))}
      </ul>
    </section>
  )
}
