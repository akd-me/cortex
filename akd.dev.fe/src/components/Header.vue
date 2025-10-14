<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ServerIcon } from '@heroicons/vue/24/outline'
import ThemeToggle from './ThemeToggle.vue'
import CortexLogo from '@/assets/cortex.png'
import type { AppInfo, McpServerInfo } from '@/types/api'

interface Props {
  appInfo: AppInfo | null
}

defineProps<Props>()

const mcpServerInfo = ref<McpServerInfo | null>(null)

onMounted(async () => {
  if (window.electronAPI) {
    mcpServerInfo.value = await window.electronAPI.getMcpServerInfo()
  }
})
</script>

<template>
  <header class="header">
    <div class="header-left">
      <div class="app-brand">
        <img :src="CortexLogo" alt="Cortex Logo" class="app-icon" />
        <h1 class="app-title">CORTEX</h1>
      </div>
      <div v-if="appInfo" class="version-badge">
        v{{ appInfo.version }}
      </div>
    </div>
    <div class="header-right">
      <div class="header-controls">
        <ThemeToggle />
        <div v-if="mcpServerInfo" class="mcp-status">
          <ServerIcon class="server-icon" />
          <div class="status-info">
            <span class="status-text">MCP SERVER</span>
            <span class="status-port">{{ mcpServerInfo.port }}</span>
          </div>
          <div class="status-indicator active"></div>
        </div>
      </div>
    </div>
  </header>
</template>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-lg) var(--spacing-xl);
  background-color: var(--color-background);
  border-bottom: var(--border-width) solid var(--color-border);
  -webkit-app-region: drag; /* Allow dragging the window on macOS */
  box-shadow: var(--shadow-brutal);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
}

.app-brand {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.app-icon {
  width: 32px;
  height: 32px;
  filter: drop-shadow(0 0 4px rgba(20, 184, 166, 0.3));
  transition: var(--transition-fast);
}

.app-icon:hover {
  filter: drop-shadow(0 0 8px rgba(20, 184, 166, 0.6));
  transform: scale(1.05);
}

.app-title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-extrabold);
  color: var(--color-heading);
  margin: 0;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.version-badge {
  font-size: var(--font-size-xs);
  color: var(--color-text);
  background-color: var(--color-accent);
  color: white;
  padding: var(--spacing-xs) var(--spacing-sm);
  border: var(--border-width-thin) solid var(--color-border);
  font-weight: var(--font-weight-bold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  box-shadow: var(--shadow-brutal-accent);
}

.header-right {
  -webkit-app-region: no-drag; /* Disable dragging for interactive elements */
}

.header-controls {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.mcp-status {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  background-color: var(--color-background-soft);
  border: var(--border-width-thin) solid var(--color-border);
  box-shadow: var(--shadow-brutal);
}

.server-icon {
  width: 16px;
  height: 16px;
  color: var(--color-accent);
}

.status-info {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
}

.status-text {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-bold);
  color: var(--color-text);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.status-port {
  font-family: var(--font-family-mono);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-bold);
  color: var(--color-accent);
}

.status-indicator {
  width: 8px;
  height: 8px;
  background-color: var(--color-secondary);
  border: var(--border-width-thin) solid var(--color-border);
}

.status-indicator.active {
  background-color: var(--color-accent);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.1);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}
</style>
