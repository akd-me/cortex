export interface ContextItem {
  id: number
  title: string
  content: string
  content_type: string
  tags: string[]
  project_id?: string
  created_at: string
  updated_at?: string
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
