import { Link, Route, Routes } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { DashboardPage } from './pages/DashboardPage'
import { ProjectsPage } from './pages/ProjectsPage'
import { AssetsPage } from './pages/AssetsPage'
import { ProvidersPage } from './pages/ProvidersPage'
import { ModelsPage } from './pages/ModelsPage'
import { WorkflowsPage } from './pages/WorkflowsPage'
import { SettingsPage } from './pages/SettingsPage'
import { LogsPage } from './pages/LogsPage'
import { api } from './services/api'

export function App() {
  const [health, setHealth] = useState('checking')

  useEffect(() => {
    api.health()
      .then((res) => setHealth(`${res.status} (${res.service})`))
      .catch(() => setHealth('backend-unreachable'))
  }, [])

  return (
    <div className="layout">
      <aside>
        <h1>ShotRebuild Studio</h1>
        <p>素材工厂（MVP）</p>
        <small>Backend: {health}</small>
        <nav>
          <Link to="/">Dashboard</Link>
          <Link to="/projects">项目页</Link>
          <Link to="/assets">资产页</Link>
          <Link to="/providers">Provider 管理</Link>
          <Link to="/models">模型管理</Link>
          <Link to="/workflows">Workflow 管理</Link>
          <Link to="/settings">设置</Link>
          <Link to="/logs">日志</Link>
        </nav>
      </aside>
      <main>
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/projects" element={<ProjectsPage />} />
          <Route path="/assets" element={<AssetsPage />} />
          <Route path="/providers" element={<ProvidersPage />} />
          <Route path="/models" element={<ModelsPage />} />
          <Route path="/workflows" element={<WorkflowsPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="/logs" element={<LogsPage />} />
        </Routes>
      </main>
    </div>
  )
}
