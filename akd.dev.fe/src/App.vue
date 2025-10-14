<script setup lang="ts">
import { RouterView } from 'vue-router'
import { ref, onMounted } from 'vue'
import Sidebar from './components/Sidebar.vue'
import Header from './components/Header.vue'
import type { AppInfo } from '@/types/api'

const appInfo = ref<AppInfo | null>(null)

onMounted(async () => {
  if (window.electronAPI) {
    appInfo.value = await window.electronAPI.getAppInfo()
  }
  
  // Initialize theme
  const savedTheme = localStorage.getItem('theme')
  const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
  
  if (savedTheme) {
    document.documentElement.setAttribute('data-theme', savedTheme)
  } else if (systemPrefersDark) {
    document.documentElement.setAttribute('data-theme', 'dark')
  } else {
    document.documentElement.setAttribute('data-theme', 'light')
  }
})
</script>

<template>
  <div class="app">
    <Header :app-info="appInfo" />
    <div class="app-body">
      <Sidebar />
      <main class="main-content">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<style scoped>
.app {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: var(--color-background);
  font-family: var(--font-family-sans);
  border: var(--border-width) solid var(--color-border);
  box-shadow: var(--shadow-brutal);
}

.app-body {
  display: flex;
  flex: 1;
  overflow: hidden;
  border-top: var(--border-width) solid var(--color-border);
}

.main-content {
  flex: 1;
  padding: var(--spacing-lg);
  overflow-y: auto;
  background-color: var(--color-background);
  border-left: var(--border-width) solid var(--color-border);
  margin: 0;
  box-sizing: border-box;
}
</style>