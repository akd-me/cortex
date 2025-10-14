<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { SunIcon, MoonIcon } from '@heroicons/vue/24/outline'

const isDark = ref(false)

onMounted(() => {
  // Check for saved theme preference or default to system preference
  const savedTheme = localStorage.getItem('theme')
  const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
  
  if (savedTheme) {
    isDark.value = savedTheme === 'dark'
  } else {
    isDark.value = systemPrefersDark
  }
  
  applyTheme()
})

const toggleTheme = () => {
  isDark.value = !isDark.value
  applyTheme()
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
}

const applyTheme = () => {
  const root = document.documentElement
  if (isDark.value) {
    root.setAttribute('data-theme', 'dark')
  } else {
    root.setAttribute('data-theme', 'light')
  }
}
</script>

<template>
  <button @click="toggleTheme" class="theme-toggle" :title="isDark ? 'Switch to light mode' : 'Switch to dark mode'">
    <SunIcon v-if="isDark" class="theme-icon" />
    <MoonIcon v-else class="theme-icon" />
  </button>
</template>

<style scoped>
.theme-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background-color: var(--color-background-soft);
  border: var(--border-width) solid var(--color-border);
  cursor: pointer;
  transition: var(--transition-fast);
  box-shadow: var(--shadow-brutal);
}

.theme-toggle:hover {
  background-color: var(--color-accent);
  color: var(--color-background);
  box-shadow: var(--shadow-brutal-accent-hover);
  transform: translate(-2px, -2px);
}

.theme-icon {
  width: 20px;
  height: 20px;
  color: var(--color-text);
}

.theme-toggle:hover .theme-icon {
  color: var(--color-background);
}
</style>
