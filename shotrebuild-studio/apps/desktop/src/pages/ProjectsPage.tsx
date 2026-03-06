import { useEffect, useState } from 'react'
import { api } from '../services/api'

export function ProjectsPage() {
  const [projects, setProjects] = useState<any[]>([])
  const [name, setName] = useState('')

  async function loadProjects() {
    setProjects(await api.listProjects())
  }

  useEffect(() => {
    loadProjects().catch(console.error)
  }, [])

  async function createProject() {
    if (!name) return
    await api.createProject({ name, description: 'MVP 项目占位' })
    setName('')
    await loadProjects()
  }

  return (
    <section>
      <h2>素材工厂 / 项目页</h2>
      <div>
        <input value={name} onChange={(e) => setName(e.target.value)} placeholder="输入项目名" />
        <button onClick={() => createProject()}>创建项目</button>
      </div>
      <ul>
        {projects.map((project) => (
          <li key={project.id}>#{project.id} {project.name} - {project.status}</li>
        ))}
      </ul>
    </section>
  )
}
