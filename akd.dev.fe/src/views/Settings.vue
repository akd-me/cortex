<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { 
  Cog6ToothIcon, 
  InformationCircleIcon, 
  ServerIcon, 
  FolderIcon, 
  ArrowDownTrayIcon, 
  ArrowUpTrayIcon, 
  DocumentTextIcon,
  ClipboardDocumentIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon,
  TrashIcon
} from '@heroicons/vue/24/outline'
import type { AppInfo, McpServerInfo, McpInfo } from '@/types/api'

const appInfo = ref<AppInfo | null>(null)
const mcpServerInfo = ref<McpServerInfo | null>(null)
const mcpInfo = ref<McpInfo | null>(null)
const mcpConfig = ref<any>(null)
const dbPath = ref('~/.cortex/context.db')
const loadingConfig = ref(false)

// Wipe database modal state
const showWipeModal = ref(false)
const wipeConfirmationText = ref('')
const isWiping = ref(false)
const WIPE_CONFIRMATION_TEXT = 'DELETE ALL CONTENT'

onMounted(async () => {
  if (window.electronAPI) {
    appInfo.value = await window.electronAPI.getAppInfo()
    mcpServerInfo.value = await window.electronAPI.getMcpServerInfo()
  }

  try {
    const response = await fetch('/mcp/cortex/info')
    if (response.ok) {
      mcpInfo.value = await response.json()
    }
  } catch (error) {
    console.error('Error fetching MCP info:', error)
  }

  // Fetch dynamic MCP configuration
  await loadMCPConfig()
})

const loadMCPConfig = async () => {
  loadingConfig.value = true
  try {
    const response = await fetch('/api/mcp/config')
    if (response.ok) {
      const configData = await response.json()
      mcpConfig.value = configData
      // Update database path with dynamic value
      if (configData.system_info?.database_path) {
        dbPath.value = configData.system_info.database_path
      }
    }
  } catch (error) {
    console.error('Error fetching MCP config:', error)
  } finally {
    loadingConfig.value = false
  }
}

const exportData = async () => {
  try {
    console.log('Starting data export...')
    const response = await fetch('/api/data/export')
    
    if (!response.ok) {
      throw new Error(`Export failed: ${response.status} ${response.statusText}`)
    }
    
    // Get filename from response headers or create default
    const contentDisposition = response.headers.get('content-disposition')
    let filename = 'cortex_export.json'
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="(.+)"/)
      if (filenameMatch) {
        filename = filenameMatch[1]
      }
    }
    
    // Create blob and download
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
    
    console.log('Data export completed successfully')
  } catch (error) {
    console.error('Export failed:', error)
    alert('Export failed: ' + (error instanceof Error ? error.message : String(error)))
  }
}

const importData = async () => {
  try {
    // Create file input element
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = '.json'
    input.style.display = 'none'
    
    input.onchange = async (event) => {
      const target = event.target as HTMLInputElement
      const file = target.files?.[0]
      if (!file) return
      
      try {
        console.log('Starting data import...')
        const formData = new FormData()
        formData.append('file', file)
        
        const response = await fetch('/api/data/import', {
          method: 'POST',
          body: formData
        })
        
        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.detail || `Import failed: ${response.status}`)
        }
        
        const result = await response.json()
        console.log('Import completed:', result)
        
        // Show success message with details
        const message = `Import completed successfully!\n\n` +
          `Imported Items: ${result.imported_items}\n` +
          `Imported Projects: ${result.imported_projects}\n` +
          `Errors: ${result.total_errors}`
        
        if (result.errors && result.errors.length > 0) {
          console.warn('Import errors:', result.errors)
          alert(message + '\n\nErrors:\n' + result.errors.join('\n'))
        } else {
          alert(message)
        }
        
        // Clean up
        document.body.removeChild(input)
        
      } catch (error) {
        console.error('Import failed:', error)
        alert('Import failed: ' + (error instanceof Error ? error.message : String(error)))
        document.body.removeChild(input)
      }
    }
    
    // Add to DOM and trigger click
    document.body.appendChild(input)
    input.click()
    
  } catch (error) {
    console.error('Import setup failed:', error)
    alert('Import setup failed: ' + (error instanceof Error ? error.message : String(error)))
  }
}

const openWipeModal = () => {
  showWipeModal.value = true
  wipeConfirmationText.value = ''
}

const closeWipeModal = () => {
  showWipeModal.value = false
  wipeConfirmationText.value = ''
  isWiping.value = false
}

const wipeDatabase = async () => {
  if (wipeConfirmationText.value !== WIPE_CONFIRMATION_TEXT) {
    alert('Please type "DELETE ALL CONTENT" exactly to confirm')
    return
  }

  isWiping.value = true
  
  try {
    console.log('Starting database wipe...')
    const response = await fetch('/api/data/wipe', {
      method: 'DELETE'
    })
    
    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || `Wipe failed: ${response.status}`)
    }
    
    const result = await response.json()
    console.log('Database wiped:', result)
    
    alert(`Database wiped successfully!\n\nDeleted Items: ${result.deleted_items}\nDeleted Projects: ${result.deleted_projects}`)
    
    closeWipeModal()
    
    // Optionally refresh the page or reload data
    window.location.reload()
    
  } catch (error) {
    console.error('Database wipe failed:', error)
    alert('Database wipe failed: ' + (error instanceof Error ? error.message : String(error)))
  } finally {
    isWiping.value = false
  }
}

const isWipeButtonDisabled = () => {
  return wipeConfirmationText.value !== WIPE_CONFIRMATION_TEXT || isWiping.value
}
</script>

<template>
  <div class="settings">
    <div class="settings-header">
      <div class="header-content">
        <Cog6ToothIcon class="header-icon" />
        <h1>SETTINGS</h1>
      </div>
      <p class="subtitle">CONFIGURE YOUR CORTEX CONTEXT MANAGER</p>
    </div>

    <div class="settings-sections">
      <!-- App Information -->
      <section class="settings-section">
        <div class="section-header">
          <InformationCircleIcon class="section-icon" />
          <h2>APPLICATION INFORMATION</h2>
        </div>
        <div class="setting-item">
          <div class="setting-label">APPLICATION NAME</div>
          <div class="setting-value">{{ appInfo?.name || 'Cortex Context Manager' }}</div>
        </div>
        <div class="setting-item">
          <div class="setting-label">VERSION</div>
          <div class="setting-value">{{ appInfo?.version || '1.0.0' }}</div>
        </div>
        <div class="setting-item">
          <div class="setting-label">PLATFORM</div>
          <div class="setting-value">{{ appInfo?.platform || 'darwin' }}</div>
        </div>
      </section>

      <!-- MCP Server Configuration -->
      <section class="settings-section">
        <div class="section-header">
          <ServerIcon class="section-icon" />
          <h2>MCP SERVER CONFIGURATION</h2>
          <div v-if="loadingConfig" class="loading-indicator">
            <span>Loading...</span>
          </div>
        </div>
        <div class="setting-item">
          <div class="setting-label">SERVER STATUS</div>
          <div class="setting-value">
            <CheckCircleIcon class="status-icon active" />
            <span>RUNNING</span>
          </div>
        </div>
        <div class="setting-item">
          <div class="setting-label">CONNECTION TYPE</div>
          <div class="setting-value code">HTTP</div>
        </div>
        <div class="setting-item">
          <div class="setting-label">PROJECT ROOT</div>
          <div class="setting-value code">{{ mcpConfig?.system_info?.project_root || 'Loading...' }}</div>
        </div>
        <div class="setting-item">
          <div class="setting-label">PYTHON EXECUTABLE</div>
          <div class="setting-value code">{{ mcpConfig?.system_info?.python_path || 'Loading...' }}</div>
        </div>
        <div class="setting-item">
          <div class="setting-label">AVAILABLE TOOLS</div>
          <div class="setting-value">{{ mcpInfo?.capabilities?.tools?.length || 0 }} TOOLS</div>
        </div>
      </section>

      <!-- Storage Configuration -->
      <section class="settings-section">
        <div class="section-header">
          <FolderIcon class="section-icon" />
          <h2>LOCAL STORAGE</h2>
        </div>
        <div class="setting-item">
          <div class="setting-label">STORAGE TYPE</div>
          <div class="setting-value">SQLITE</div>
        </div>
      </section>

      <!-- Data Management -->
      <section class="settings-section">
        <div class="section-header">
          <DocumentTextIcon class="section-icon" />
          <h2>DATA MANAGEMENT</h2>
        </div>
        <div class="setting-item">
          <div class="setting-label">EXPORT DATA</div>
          <div class="setting-value">
            <span class="setting-description">EXPORT ALL CONTEXT ITEMS AND PROJECTS</span>
            <button @click="exportData" class="btn btn-secondary">
              <ArrowDownTrayIcon class="btn-icon" />
              EXPORT
            </button>
          </div>
        </div>
        <div class="setting-item">
          <div class="setting-label">IMPORT DATA</div>
          <div class="setting-value">
            <span class="setting-description">IMPORT CONTEXT ITEMS FROM A BACKUP FILE</span>
            <button @click="importData" class="btn btn-secondary">
              <ArrowUpTrayIcon class="btn-icon" />
              IMPORT
            </button>
          </div>
        </div>
      </section>

      <!-- Advanced Settings -->
      <section class="settings-section danger-section">
        <div class="section-header">
          <ExclamationTriangleIcon class="section-icon danger-icon" />
          <h2>ADVANCED SETTINGS</h2>
        </div>
        <div class="setting-item">
          <div class="setting-label">WIPE DATABASE</div>
          <div class="setting-value">
            <span class="setting-description danger-text">PERMANENTLY DELETE ALL CONTEXT ITEMS AND PROJECTS</span>
            <button @click="openWipeModal" class="btn btn-danger">
              <TrashIcon class="btn-icon" />
              WIPE DATABASE
            </button>
          </div>
        </div>
      </section>

      <!-- Connection Guide -->
      <section class="settings-section">
        <div class="section-header">
          <ClipboardDocumentIcon class="section-icon" />
          <h2>MCP CLIENT CONNECTION</h2>
        </div>
        <div class="connection-guide">
          <h3>CURSOR IDE (HTTP)</h3>
          <div class="code-block">
            <pre>{
  "mcpServers": {
    "cortex-http": {
      "url": "http://localhost:8000/mcp/cortex",
    }
  }
}</pre>
            <button class="copy-btn" title="Copy to clipboard">
              <ClipboardDocumentIcon class="copy-icon" />
              COPY
            </button>
          </div>

          <h3>CLAUDE DESKTOP (HTTP)</h3>
          <div class="code-block">
            <pre>{
  "mcpServers": {
    "cortex-http": {
      "url": "http://localhost:8000/mcp/cortex",
    }
  }
}</pre>
            <button class="copy-btn" title="Copy to clipboard">
              <ClipboardDocumentIcon class="copy-icon" />
              COPY
            </button>
          </div>


          <div class="connection-note">
            <p><strong>NOTE:</strong> MCP SERVER RUNS VIA HTTP ON PORT 8000 (MAIN FASTAPI PORT). 
            ENSURE CORTEX APPLICATION IS RUNNING WITH <code>bash ./scripts/docker-dev.sh</code>. 
            THE SERVER PROVIDES CONTEXT MANAGEMENT TOOLS INCLUDING STORE, RETRIEVE, SEARCH, AND PROJECT MANAGEMENT.</p>
          </div>
        </div>
      </section>

    </div>

    <!-- Wipe Database Warning Modal -->
    <div v-if="showWipeModal" class="modal-overlay" @click="closeWipeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <ExclamationTriangleIcon class="modal-icon danger-icon" />
          <h3>DANGER: WIPE DATABASE</h3>
        </div>
        <div class="modal-body">
          <p class="warning-text">
            <strong>THIS ACTION CANNOT BE UNDONE!</strong>
          </p>
          <p>
            This will permanently delete ALL context items and projects from your database. 
            Make sure you have exported your data before proceeding.
          </p>
          <div class="confirmation-input">
            <label for="wipe-confirmation">
              Type <code>{{ WIPE_CONFIRMATION_TEXT }}</code> to confirm:
            </label>
            <input
              id="wipe-confirmation"
              v-model="wipeConfirmationText"
              type="text"
              class="confirmation-input-field"
              placeholder="Type the confirmation text here"
              :disabled="isWiping"
            />
          </div>
        </div>
        <div class="modal-footer">
          <button @click="closeWipeModal" class="btn btn-secondary" :disabled="isWiping">
            CANCEL
          </button>
          <button 
            @click="wipeDatabase" 
            class="btn btn-danger" 
            :disabled="isWipeButtonDisabled()"
          >
            <TrashIcon class="btn-icon" />
            {{ isWiping ? 'WIPING...' : 'WIPE DATABASE' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.settings {
  padding: var(--spacing-lg);
  max-width: var(--container-max-width);
  margin: 0 auto;
  background: var(--color-background);
  border: var(--border-width) solid var(--color-border);
  box-shadow: var(--shadow-brutal);
}

.settings-header {
  margin-bottom: var(--spacing-xl);
  border-bottom: var(--border-width) solid var(--color-border);
  padding-bottom: var(--spacing-lg);
}

.header-content {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-sm);
}

.header-icon {
  width: 32px;
  height: 32px;
  color: var(--color-accent);
}

.settings-header h1 {
  margin: 0;
  color: var(--color-heading);
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-extrabold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.subtitle {
  color: var(--color-text-muted);
  margin: 0;
  font-size: var(--font-size-lg);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: var(--font-weight-medium);
}

.settings-sections {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
}

.settings-section {
  background-color: var(--color-background-soft);
  border: var(--border-width) solid var(--color-border);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-brutal);
}

.section-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-lg);
  border-bottom: var(--border-width) solid var(--color-border);
  padding-bottom: var(--spacing-md);
}

.section-icon {
  width: 24px;
  height: 24px;
  color: var(--color-accent);
}

.section-header h2 {
  margin: 0;
  color: var(--color-heading);
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-md) 0;
  border-bottom: 1px solid var(--color-border-light);
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-label {
  font-weight: var(--font-weight-bold);
  color: var(--color-text);
  flex-shrink: 0;
  margin-right: var(--spacing-md);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-size: var(--font-size-sm);
}

.setting-value {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  color: var(--color-text-muted);
  text-align: right;
  font-weight: var(--font-weight-medium);
}

.setting-description {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: var(--font-weight-medium);
}

.code {
  font-family: var(--font-family-mono);
  background-color: var(--color-background-mute);
  padding: var(--spacing-xs) var(--spacing-sm);
  border: 1px solid var(--color-border-light);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
}

.status-icon {
  width: 16px;
  height: 16px;
  color: var(--color-secondary);
}

.status-icon.active {
  color: var(--color-accent);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  border: var(--border-width) solid var(--color-border);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-bold);
  cursor: pointer;
  transition: var(--transition-fast);
  white-space: nowrap;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  box-shadow: var(--shadow-brutal);
}

.btn-secondary {
  background-color: var(--color-secondary);
  color: var(--color-background);
}

.btn-secondary:hover {
  box-shadow: var(--shadow-brutal-hover);
  transform: translate(-2px, -2px);
}

.btn-small {
  padding: var(--spacing-xs) var(--spacing-sm);
  font-size: var(--font-size-xs);
}

.btn-icon {
  width: 14px;
  height: 14px;
}

.toggle {
  position: relative;
  display: inline-block;
  width: 3rem;
  height: 1.5rem;
}

.toggle input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--color-border);
  transition: var(--transition-normal);
  border: var(--border-width) solid var(--color-border);
  box-shadow: var(--shadow-brutal);
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 1.125rem;
  width: 1.125rem;
  left: 0.1875rem;
  bottom: 0.1875rem;
  background-color: var(--color-background);
  transition: var(--transition-normal);
  border: var(--border-width) solid var(--color-border);
  box-shadow: var(--shadow-brutal);
}

.toggle input:checked + .toggle-slider {
  background-color: var(--color-accent);
}

.toggle input:checked + .toggle-slider:before {
  transform: translateX(1.5rem);
}

.connection-guide {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.connection-guide h3 {
  margin: 0 0 var(--spacing-sm) 0;
  color: var(--color-heading);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-bold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.code-block {
  position: relative;
  background-color: var(--color-background-mute);
  border: var(--border-width) solid var(--color-border);
  padding: var(--spacing-md);
  box-shadow: var(--shadow-brutal);
}

.code-block pre {
  margin: 0;
  font-family: var(--font-family-mono);
  font-size: var(--font-size-sm);
  color: var(--color-text);
  overflow-x: auto;
  line-height: 1.5;
}

.copy-btn {
  position: absolute;
  top: var(--spacing-md);
  right: var(--spacing-md);
  background: var(--color-accent);
  color: var(--color-background);
  border: var(--border-width) solid var(--color-border);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-bold);
  cursor: pointer;
  padding: var(--spacing-xs) var(--spacing-sm);
  box-shadow: var(--shadow-brutal);
  transition: var(--transition-fast);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.copy-btn:hover {
  box-shadow: var(--shadow-brutal-accent-hover);
  transform: translate(-2px, -2px);
}

.copy-icon {
  width: 12px;
  height: 12px;
}

.connection-note {
  background-color: var(--color-background-soft);
  border-left: var(--border-width-thick) solid var(--color-accent);
  padding: var(--spacing-md);
  border: var(--border-width) solid var(--color-border);
  box-shadow: var(--shadow-brutal);
}

.connection-note p {
  margin: 0;
  font-size: var(--font-size-sm);
  color: var(--color-text);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: var(--font-weight-medium);
}

.connection-note code {
  background-color: var(--color-background-mute);
  padding: var(--spacing-xs);
  border: 1px solid var(--color-border-light);
  font-family: var(--font-family-mono);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-bold);
}

/* Loading Indicator */
.loading-indicator {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
}

.loading-indicator::before {
  content: '';
  width: 16px;
  height: 16px;
  border: 2px solid var(--color-border);
  border-top: 2px solid var(--color-accent);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Danger Section Styles */
.danger-section {
  border-left: var(--border-width-thick) solid #dc2626;
  background-color: rgba(220, 38, 38, 0.05);
}

.danger-icon {
  color: #dc2626;
}

.danger-text {
  color: #dc2626;
}

.btn-danger {
  background-color: #dc2626;
  color: var(--color-background);
  border-color: #dc2626;
}

.btn-danger:hover:not(:disabled) {
  background-color: #b91c1c;
  border-color: #b91c1c;
  box-shadow: var(--shadow-brutal-hover);
  transform: translate(-2px, -2px);
}

.btn-danger:disabled {
  background-color: #9ca3af;
  border-color: #9ca3af;
  cursor: not-allowed;
  transform: none;
  box-shadow: var(--shadow-brutal);
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: var(--spacing-lg);
}

.modal-content {
  background-color: var(--color-background);
  border: var(--border-width) solid var(--color-border);
  box-shadow: var(--shadow-brutal);
  max-width: 500px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-lg);
  border-bottom: var(--border-width) solid var(--color-border);
  background-color: var(--color-background-soft);
}

.modal-icon {
  width: 24px;
  height: 24px;
}

.modal-header h3 {
  margin: 0;
  color: var(--color-heading);
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.modal-body {
  padding: var(--spacing-lg);
}

.warning-text {
  color: #dc2626;
  font-weight: var(--font-weight-bold);
  margin-bottom: var(--spacing-md);
}

.modal-body p {
  margin: 0 0 var(--spacing-md) 0;
  color: var(--color-text);
  line-height: 1.5;
}

.confirmation-input {
  margin-top: var(--spacing-lg);
}

.confirmation-input label {
  display: block;
  margin-bottom: var(--spacing-sm);
  font-weight: var(--font-weight-bold);
  color: var(--color-text);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-size: var(--font-size-sm);
}

.confirmation-input code {
  background-color: var(--color-background-mute);
  padding: var(--spacing-xs);
  border: 1px solid var(--color-border-light);
  font-family: var(--font-family-mono);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-bold);
  color: #dc2626;
}

.confirmation-input-field {
  width: 100%;
  padding: var(--spacing-sm);
  border: var(--border-width) solid var(--color-border);
  font-family: var(--font-family-mono);
  font-size: var(--font-size-sm);
  background-color: var(--color-background);
  color: var(--color-text);
  box-shadow: var(--shadow-brutal);
}

.confirmation-input-field:focus {
  outline: none;
  border-color: var(--color-accent);
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

.confirmation-input-field:disabled {
  background-color: var(--color-background-mute);
  color: var(--color-text-muted);
  cursor: not-allowed;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-md);
  padding: var(--spacing-lg);
  border-top: var(--border-width) solid var(--color-border);
  background-color: var(--color-background-soft);
}
</style>
