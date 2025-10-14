<script setup lang="ts">
import { RouterLink, useRoute } from 'vue-router'
import { ref, onMounted, onUnmounted } from 'vue'
import { 
  HomeIcon, 
  DocumentTextIcon, 
  FolderIcon, 
  Cog6ToothIcon,
  ServerIcon,
  ChevronLeftIcon,
  ChevronRightIcon
} from '@heroicons/vue/24/outline'

const route = useRoute()
const isCollapsed = ref(false)
const isHovered = ref(false)

const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
}

// Auto-collapse on narrow screens
const checkScreenSize = () => {
  if (window.innerWidth < 1024) {
    isCollapsed.value = true
  } else {
    isCollapsed.value = false
  }
}

onMounted(() => {
  checkScreenSize()
  window.addEventListener('resize', checkScreenSize)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkScreenSize)
})

const menuItems = [
  {
    path: '/',
    name: 'Dashboard',
    icon: HomeIcon
  },
  {
    path: '/contexts',
    name: 'Context Items',
    icon: DocumentTextIcon
  },
  {
    path: '/projects',
    name: 'Projects',
    icon: FolderIcon
  },
  {
    path: '/settings',
    name: 'Settings',
    icon: Cog6ToothIcon
  }
]

const isActiveRoute = (path: string) => {
  if (path === '/') {
    return route.path === '/'
  }
  return route.path.startsWith(path)
}
</script>

<template>
  <aside 
    class="sidebar" 
    :class="{ 
      'sidebar--collapsed': isCollapsed && !isHovered,
      'sidebar--hovered': isHovered
    }"
    @mouseenter="isHovered = true"
    @mouseleave="isHovered = false"
  >
    <div class="sidebar-header">
      <button @click="toggleCollapse" class="collapse-btn">
        <ChevronLeftIcon v-if="!isCollapsed" class="collapse-icon" />
        <ChevronRightIcon v-else class="collapse-icon" />
      </button>
    </div>
    
    <nav class="nav">
      <ul class="nav-list">
        <li v-for="item in menuItems" :key="item.path" class="nav-item">
          <RouterLink 
            :to="item.path" 
            class="nav-link"
            :class="{ 'nav-link--active': isActiveRoute(item.path) }"
            :title="isCollapsed && !isHovered ? item.name : ''"
          >
            <component :is="item.icon" class="nav-icon" />
            <span v-if="!isCollapsed || isHovered" class="nav-text">{{ item.name.toUpperCase() }}</span>
          </RouterLink>
        </li>
      </ul>
    </nav>
    
    <div v-if="!isCollapsed || isHovered" class="sidebar-footer">
      <div class="storage-info">
        <div class="storage-header">
          <ServerIcon class="storage-icon" />
          <span class="storage-label">LOCAL STORAGE</span>
        </div>
        <div class="storage-path">~/.cortex/</div>
      </div>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  width: var(--sidebar-width);
  background-color: var(--color-background);
  border-right: var(--border-width) solid var(--color-border);
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-brutal);
  transition: width var(--transition-normal);
  position: relative;
  z-index: 10;
}

.sidebar--collapsed {
  width: var(--sidebar-width-collapsed);
}

.sidebar--hovered {
  width: var(--sidebar-width) !important;
}

.sidebar-header {
  padding: var(--spacing-md);
  border-bottom: var(--border-width) solid var(--color-border);
  display: flex;
  justify-content: flex-end;
}

.collapse-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background-color: var(--color-background-soft);
  border: var(--border-width) solid var(--color-border);
  cursor: pointer;
  transition: var(--transition-fast);
  box-shadow: var(--shadow-brutal);
  color: var(--color-text);
}

.collapse-btn:hover {
  background-color: var(--color-accent);
  color: var(--color-background);
  box-shadow: var(--shadow-brutal-accent-hover);
  transform: translate(-2px, -2px);
}

.collapse-icon {
  width: 16px;
  height: 16px;
}

.nav {
  flex: 1;
  padding: var(--spacing-xl) 0;
}

.nav-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.nav-item {
  margin: 0;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md) var(--spacing-lg);
  color: var(--color-text);
  text-decoration: none;
  transition: var(--transition-fast);
  border: var(--border-width-thin) solid transparent;
  background: none;
  margin: 0 var(--spacing-md);
  font-weight: var(--font-weight-semibold);
  letter-spacing: 0.05em;
  justify-content: flex-start;
}

.sidebar--collapsed .nav-link {
  justify-content: center;
  padding: var(--spacing-md);
  min-height: 48px;
}

.sidebar--collapsed .nav-link:hover {
  background-color: var(--color-background-soft);
  border-color: var(--color-border);
}

.sidebar--hovered .nav-link {
  justify-content: flex-start;
  padding: var(--spacing-md) var(--spacing-lg);
}

.nav-link:hover {
  background-color: var(--color-background-soft);
  border-color: var(--color-border-light);
  transform: translateX(2px);
}

.nav-link--active {
  background-color: var(--color-accent);
  color: white;
  border-color: var(--color-border);
  box-shadow: var(--shadow-brutal-accent);
  transform: translateX(4px);
}

.nav-link--active:hover {
  background-color: var(--color-accent-hover);
  transform: translateX(6px);
}

.nav-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  color: var(--color-text);
}

.nav-text {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-bold);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.sidebar-footer {
  padding: var(--spacing-lg);
  border-top: var(--border-width) solid var(--color-border);
  background-color: var(--color-background-soft);
}

.storage-info {
  font-size: var(--font-size-xs);
  color: var(--color-text);
}

.storage-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-sm);
}

.storage-icon {
  width: 16px;
  height: 16px;
  color: var(--color-accent);
}

.storage-label {
  font-weight: var(--font-weight-bold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.storage-path {
  font-family: var(--font-family-mono);
  background-color: var(--color-background);
  padding: var(--spacing-sm);
  border: var(--border-width-thin) solid var(--color-border);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  word-break: break-all;
  box-shadow: var(--shadow-brutal);
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    z-index: 1000;
    transform: translateX(-100%);
    transition: transform var(--transition-normal);
  }
  
  .sidebar--collapsed {
    transform: translateX(0);
  }
  
  .sidebar--hovered {
    transform: translateX(0) !important;
  }
}
</style>
