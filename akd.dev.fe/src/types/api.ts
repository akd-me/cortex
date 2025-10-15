export interface ContextItem {
  id: number
  title: string
  content: string
  content_type: string
  tags: string[]
  extra_metadata: Record<string, any>
  source?: string
  project_id?: string
  is_active: boolean
  created_at: string
  updated_at?: string
  combined_score?: number
}

export interface ContextItemCreate {
  title: string
  content: string
  content_type: string
  tags: string[]
  extra_metadata?: Record<string, any>
  source?: string
  project_id?: string
}

export interface ContextItemUpdate {
  title?: string
  content?: string
  content_type?: string
  tags?: string[]
  extra_metadata?: Record<string, any>
  source?: string
  project_id?: string
  is_active?: boolean
}

export enum SearchType {
  SEMANTIC = 'semantic',
  KEYWORD = 'keyword',
  HYBRID = 'hybrid'
}

export interface ContextSearchQuery {
  query: string
  search_type: SearchType
  content_types?: string[]
  tags?: string[]
  project_id?: string
  limit: number
  offset: number
  semantic_weight: number
}

export interface ContextSearchResult {
  items: ContextItem[]
  total: number
  limit: number
  offset: number
  search_type: SearchType
  query: string
  execution_time_ms?: number
}

export interface ContextProject {
  id: string
  name: string
  description?: string
  settings: Record<string, any>
  is_active: boolean
  created_at: string
  updated_at?: string
}

export interface ContextProjectCreate {
  id: string
  name: string
  description?: string
  settings?: Record<string, any>
}

export interface ContextProjectUpdate {
  name?: string
  description?: string
  settings?: Record<string, any>
  is_active?: boolean
}

export interface ContextStats {
  total_items: number
  active_items: number
  content_types: Record<string, number>
  projects_count: number
  embedding_dimension: number
  last_updated: string
}

export interface McpInfo {
  name: string
  version: string
  description: string
  mcp_server: {
    host: string
    port: number
    status: string
  }
  capabilities: {
    tools: string[]
    resources: string[]
  }
}

export interface AppInfo {
  name: string
  version: string
  platform: string
}

export interface McpServerInfo {
  host: string
  port: number
  mcpPort: number
  status: string
}

export interface TestResults {
  [key: string]: any
}

export interface StatsResponse {
  total_items: number
  content_types: Record<string, number>
  project_id: string | null
}
