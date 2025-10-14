<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { 
  DocumentTextIcon, 
  FolderIcon, 
  ChartBarIcon,
  ClockIcon
} from '@heroicons/vue/24/outline'
import type { ContextItem, StatsResponse } from '@/types/api'

const stats = ref({
  totalItems: 0,
  totalProjects: 0,
  contentTypes: {} as Record<string, number>,
  recentItems: [] as ContextItem[]
})


onMounted(async () => {
  try {
    console.log('Loading dashboard data...')
    // Fetch stats from API
    const response = await fetch('/api/context/stats')
    if (response.ok) {
      const data: StatsResponse = await response.json()
      stats.value.totalItems = data.total_items
      stats.value.contentTypes = data.content_types
      console.log('Stats loaded:', data)
    } else {
      console.error('Failed to fetch stats:', response.status, response.statusText)
    }

    // Fetch recent items
    const itemsResponse = await fetch('/api/context/items?limit=5')
    if (itemsResponse.ok) {
      const itemsData: ContextItem[] = await itemsResponse.json()
      stats.value.recentItems = itemsData
      console.log('Recent items loaded:', itemsData.length, 'items')
    } else {
      console.error('Failed to fetch items:', itemsResponse.status, itemsResponse.statusText)
    }


    // Get projects count
    const projectsResponse = await fetch('/api/context/projects')
    if (projectsResponse.ok) {
      const projectsData: any[] = await projectsResponse.json()
      stats.value.totalProjects = projectsData.length
      console.log('Projects loaded:', projectsData.length, 'projects')
    } else {
      console.error('Failed to fetch projects:', projectsResponse.status, projectsResponse.statusText)
    }
  } catch (error) {
    console.error('Error fetching dashboard data:', error)
    // Show some fallback data or error state
    stats.value.totalItems = 0
    stats.value.totalProjects = 0
    stats.value.contentTypes = {}
    stats.value.recentItems = []
  }
})

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString()
}
</script>

<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h1>DASHBOARD</h1>
      <p class="subtitle">Welcome to your local context management system</p>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">
          <DocumentTextIcon />
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.totalItems }}</div>
          <div class="stat-label">CONTEXT ITEMS</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">
          <FolderIcon />
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.totalProjects }}</div>
          <div class="stat-label">PROJECTS</div>
        </div>
      </div>

    </div>

    <div class="dashboard-content">
      <div class="section">
        <div class="section-header">
          <ChartBarIcon class="section-icon" />
          <h2>CONTENT TYPES</h2>
        </div>
        <div class="content-types">
          <div 
            v-for="(count, type) in stats.contentTypes" 
            :key="type"
            class="content-type-item"
          >
            <span class="content-type-name">{{ type.toUpperCase() }}</span>
            <span class="content-type-count">{{ count }}</span>
          </div>
          <div v-if="Object.keys(stats.contentTypes).length === 0" class="empty-state">
            NO CONTENT TYPES YET
          </div>
        </div>
      </div>

      <div class="section">
        <div class="section-header">
          <ClockIcon class="section-icon" />
          <h2>RECENT CONTEXT ITEMS</h2>
        </div>
        <div class="recent-items">
          <div 
            v-for="item in stats.recentItems" 
            :key="item.id"
            class="recent-item"
          >
            <div class="item-title">{{ item.title }}</div>
            <div class="item-meta">
              <span class="item-type">{{ item.content_type.toUpperCase() }}</span>
              <span class="item-date">{{ formatDate(item.created_at) }}</span>
            </div>
          </div>
          <div v-if="stats.recentItems.length === 0" class="empty-state">
            NO CONTEXT ITEMS YET
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.dashboard {
  width: 100%;
  margin: 0;
  padding: 0;
}

.dashboard-header {
  margin-bottom: var(--spacing-lg);
}

.dashboard-header h1 {
  margin: 0 0 var(--spacing-sm) 0;
  color: var(--color-heading);
  font-size: var(--font-size-4xl);
  font-weight: var(--font-weight-extrabold);
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.subtitle {
  color: var(--color-text-muted);
  margin: 0;
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-medium);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-xl);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
  padding: var(--spacing-xl);
  background-color: var(--color-background);
  border: var(--border-width) solid var(--color-border);
  box-shadow: var(--shadow-brutal);
  transition: var(--transition-fast);
}

.stat-card:hover {
  transform: translate(-2px, -2px);
  box-shadow: var(--shadow-brutal-hover);
}

.stat-icon {
  width: 48px;
  height: 48px;
  color: var(--color-accent);
  flex-shrink: 0;
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-extrabold);
  color: var(--color-heading);
  margin-bottom: var(--spacing-xs);
  line-height: 1;
}

.stat-label {
  color: var(--color-text);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-bold);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.dashboard-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: var(--spacing-lg);
}

.section {
  background-color: var(--color-background);
  border: var(--border-width) solid var(--color-border);
  box-shadow: var(--shadow-brutal);
  padding: var(--spacing-xl);
}

.section-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
  padding-bottom: var(--spacing-md);
  border-bottom: var(--border-width) solid var(--color-border);
}

.section-icon {
  width: 24px;
  height: 24px;
  color: var(--color-accent);
}

.section h2 {
  margin: 0;
  color: var(--color-heading);
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-extrabold);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.content-types {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.content-type-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-md);
  background-color: var(--color-background-soft);
  border: var(--border-width-thin) solid var(--color-border);
  box-shadow: var(--shadow-brutal);
}

.content-type-name {
  font-weight: var(--font-weight-bold);
  color: var(--color-text);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.content-type-count {
  background-color: var(--color-accent);
  color: white;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-extrabold);
  padding: var(--spacing-xs) var(--spacing-sm);
  border: var(--border-width-thin) solid var(--color-border);
  box-shadow: var(--shadow-brutal-accent);
}

.recent-items {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.recent-item {
  padding: var(--spacing-md);
  background-color: var(--color-background-soft);
  border: var(--border-width-thin) solid var(--color-border);
  box-shadow: var(--shadow-brutal);
}

.item-title {
  font-weight: var(--font-weight-semibold);
  color: var(--color-text);
  margin-bottom: var(--spacing-sm);
  font-size: var(--font-size-base);
}

.item-meta {
  display: flex;
  gap: var(--spacing-md);
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.item-type {
  background-color: var(--color-background);
  padding: var(--spacing-xs) var(--spacing-sm);
  border: var(--border-width-thin) solid var(--color-border);
  font-weight: var(--font-weight-bold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}


.empty-state {
  text-align: center;
  color: var(--color-text-muted);
  font-weight: var(--font-weight-bold);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  padding: var(--spacing-2xl);
  background-color: var(--color-background-soft);
  border: var(--border-width-thin) solid var(--color-border);
  box-shadow: var(--shadow-brutal);
}

/* Full screen optimizations */
@media (min-width: 1920px) {
  .dashboard-header {
    margin-bottom: var(--spacing-md);
  }
  
  .stats-grid {
    gap: var(--spacing-md);
    margin-bottom: var(--spacing-lg);
  }
  
  .dashboard-content {
    gap: var(--spacing-md);
  }
  
  .stat-card {
    padding: var(--spacing-lg);
  }
}
</style>
