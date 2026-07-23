import { apiRequest, authenticatedDownload } from './client'
import type { Project, ProjectDocument, ProjectFile, ProjectStatus } from './types'

export interface ProjectInput {
  name: string
  client_id: string
  opportunity_id?: string | null
  work_order_id?: string | null
  manager_id?: string | null
  status: ProjectStatus
  location?: string
  description?: string
  planned_start?: string | null
  planned_end?: string | null
  budget: string
  notes?: string
}

export function getProjects(): Promise<Project[]> {
  return apiRequest<Project[]>('/projects')
}

export function createProject(payload: ProjectInput): Promise<Project> {
  return apiRequest<Project>('/projects', { method: 'POST', body: JSON.stringify(payload) })
}

export function updateProject(projectId: string, payload: Partial<ProjectInput>): Promise<Project> {
  return apiRequest<Project>(`/projects/${projectId}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
}

export function getProjectFile(projectId: string): Promise<ProjectFile> {
  return apiRequest<ProjectFile>(`/projects/${projectId}/file`)
}

export function uploadProjectDocument(
  projectId: string,
  file: File,
  category: string,
  notes?: string,
): Promise<ProjectDocument> {
  const body = new FormData()
  body.append('file', file)
  body.append('category', category)
  if (notes) body.append('notes', notes)
  return apiRequest<ProjectDocument>(`/projects/${projectId}/documents`, {
    method: 'POST',
    body,
  })
}

export function downloadProjectDocument(document: ProjectDocument): Promise<void> {
  return authenticatedDownload(
    `/projects/documents/${document.id}/download`,
    document.filename,
  )
}
