import type { AppInfo, McpServerInfo } from './api'

export {}

declare global {
  interface Window {
    electronAPI: {
      getAppInfo: () => Promise<AppInfo>
      getMcpServerInfo: () => Promise<McpServerInfo>
      platform: string
    }
  }
}
