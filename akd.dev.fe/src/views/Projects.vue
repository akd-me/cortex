<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { 
  PlusIcon, 
  TrashIcon, 
  XMarkIcon,
  FolderIcon,
  CalendarIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/vue/24/outline'

interface Project {
  id: string
  name: string
  description?: string
  is_active: boolean
  created_at: string
  updated_at?: string
}

const projects = ref<Project[]>([])
const loading = ref(false)
const showCreateForm = ref(false)
const showDeleteModal = ref(false)
const projectToDelete = ref<Project | null>(null)
const projectContextCount = ref(0)

const newProject = ref({
  id: '',
  name: '',
  description: ''
})

onMounted(() => {
  fetchProjects()
})

const fetchProjects = async () => {
  loading.value = true
  try {
    const response = await fetch('/api/context/projects')
    if (response.ok) {
      projects.value = await response.json()
    }
  } catch (error) {
    console.error('Error fetching projects:', error)
  } finally {
    loading.value = false
  }
}

const createProject = async () => {
  try {
    const response = await fetch('/api/context/projects', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(newProject.value),
    })

    if (response.ok) {
      showCreateForm.value = false
      resetForm()
      fetchProjects()
    }
  } catch (error) {
    console.error('Error creating project:', error)
  }
}

const deleteProject = async (id: string) => {
  const project = projects.value.find(p => p.id === id)
  if (!project) return
  
  projectToDelete.value = project
  showDeleteModal.value = true
  
  // Fetch context count for this project
  try {
    const response = await fetch(`/api/context/stats?project_id=${id}`)
    if (response.ok) {
      const stats = await response.json()
      projectContextCount.value = stats.total_items
    }
  } catch (error) {
    console.error('Error fetching project stats:', error)
    projectContextCount.value = 0
  }
}

const confirmDelete = async () => {
  if (!projectToDelete.value) return
  
  try {
    const response = await fetch(`/api/context/projects/${projectToDelete.value.id}`, {
      method: 'DELETE',
    })

    if (response.ok) {
      fetchProjects()
      showDeleteModal.value = false
      projectToDelete.value = null
      projectContextCount.value = 0
    }
  } catch (error) {
    console.error('Error deleting project:', error)
  }
}

const cancelDelete = () => {
  showDeleteModal.value = false
  projectToDelete.value = null
  projectContextCount.value = 0
}

const resetForm = () => {
  newProject.value = {
    id: '',
    name: '',
    description: ''
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString()
}
</script>

<template>
  <div class="projects">
    <div class="projects-header">
      <h1>PROJECTS</h1>
      <button @click="showCreateForm = true" class="btn btn-primary">
        <PlusIcon class="btn-icon" />
        CREATE PROJECT
      </button>
    </div>

    <!-- Create Form Modal -->
    <div v-if="showCreateForm" class="modal-overlay" @click="showCreateForm = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h2>CREATE NEW PROJECT</h2>
          <button @click="showCreateForm = false" class="btn-close">
            <XMarkIcon />
          </button>
        </div>
        <form @submit.prevent="createProject" class="project-form">
          <div class="form-group">
            <label for="project-id">PROJECT ID</label>
            <input
              id="project-id"
              v-model="newProject.id"
              type="text"
              required
              class="form-input"
              placeholder="Enter unique project ID"
            />
          </div>

          <div class="form-group">
            <label for="project-name">PROJECT NAME</label>
            <input
              id="project-name"
              v-model="newProject.name"
              type="text"
              required
              class="form-input"
              placeholder="Enter project name"
            />
          </div>

          <div class="form-group">
            <label for="project-description">DESCRIPTION (optional)</label>
            <textarea
              id="project-description"
              v-model="newProject.description"
              class="form-textarea"
              placeholder="Enter project description"
              rows="4"
            ></textarea>
          </div>

          <div class="form-actions">
            <button type="button" @click="showCreateForm = false" class="btn btn-secondary">
              CANCEL
            </button>
            <button type="submit" class="btn btn-primary">
              CREATE PROJECT
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click="cancelDelete">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h2>DELETE PROJECT</h2>
          <button @click="cancelDelete" class="btn-close">
            <XMarkIcon />
          </button>
        </div>
        
        <div class="delete-modal-content">
          <div class="delete-warning">
            <div class="warning-icon">
              <TrashIcon />
            </div>
            <h3>WARNING: This action cannot be undone!</h3>
            <p>You are about to permanently delete the project:</p>
          </div>
          
          <div class="project-to-delete">
            <div class="project-info">
              <h4>{{ projectToDelete?.name.toUpperCase() }}</h4>
              <div class="project-id">
                <span class="label">ID:</span>
                <code>{{ projectToDelete?.id }}</code>
              </div>
              <div v-if="projectToDelete?.description" class="project-description">
                {{ projectToDelete.description }}
              </div>
            </div>
          </div>
          
          <div class="deletion-impact">
            <div class="impact-item">
              <span class="impact-label">Associated Context Items:</span>
              <span class="impact-value">{{ projectContextCount }}</span>
            </div>
            <p class="impact-description">
              All context items associated with this project will also be deleted.
            </p>
          </div>
        </div>
        
        <div class="form-actions">
          <button @click="cancelDelete" class="btn btn-secondary">
            CANCEL
          </button>
          <button @click="confirmDelete" class="btn btn-danger">
            <TrashIcon class="btn-icon" />
            DELETE PROJECT
          </button>
        </div>
      </div>
    </div>

    <!-- Projects List -->
    <div v-if="loading" class="loading">
      LOADING PROJECTS...
    </div>

    <div v-else-if="projects.length === 0" class="empty-state">
      <div class="empty-icon">
        <FolderIcon />
      </div>
      <h3>NO PROJECTS YET</h3>
      <p>Create your first project to organize your context items.</p>
      <button @click="showCreateForm = true" class="btn btn-primary">
        <PlusIcon class="btn-icon" />
        CREATE FIRST PROJECT
      </button>
    </div>

    <div v-else class="projects-grid">
      <div v-for="project in projects" :key="project.id" class="project-card">
        <div class="project-header">
          <h3 class="project-name">{{ project.name.toUpperCase() }}</h3>
          <div class="project-actions">
            <button @click="deleteProject(project.id)" class="btn-delete" title="Delete">
              <TrashIcon />
            </button>
          </div>
        </div>

        <div class="project-id">
          <span class="label">ID:</span>
          <code>{{ project.id }}</code>
        </div>

        <div v-if="project.description" class="project-description">
          {{ project.description }}
        </div>

        <div class="project-meta">
          <span class="project-date">
            <CalendarIcon class="meta-icon" />
            Created: {{ formatDate(project.created_at) }}
          </span>
          <span v-if="project.updated_at" class="project-date">
            <CalendarIcon class="meta-icon" />
            Updated: {{ formatDate(project.updated_at) }}
          </span>
        </div>

        <div class="project-status">
          <span :class="['status-badge', project.is_active ? 'status-active' : 'status-inactive']">
            <CheckCircleIcon v-if="project.is_active" class="status-icon" />
            <XCircleIcon v-else class="status-icon" />
            {{ project.is_active ? 'ACTIVE' : 'INACTIVE' }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.projects {
  width: 100%;
  margin: 0;
  padding: 0;
}

.projects-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
}

.projects-header h1 {
  margin: 0;
  color: var(--color-heading);
  font-size: var(--font-size-4xl);
  font-weight: var(--font-weight-extrabold);
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md) var(--spacing-lg);
  border: var(--border-width) solid var(--color-border);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-bold);
  cursor: pointer;
  transition: var(--transition-fast);
  text-decoration: none;
  min-height: 44px;
  box-sizing: border-box;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  box-shadow: var(--shadow-brutal);
}

.btn-icon {
  width: 16px;
  height: 16px;
}

.btn-primary {
  background-color: var(--color-accent);
  color: white;
  border-color: var(--color-border);
}

.btn-primary:hover {
  background-color: var(--color-accent-hover);
  transform: translate(-2px, -2px);
  box-shadow: var(--shadow-brutal-accent-hover);
}

.btn-secondary {
  background-color: var(--color-background);
  color: var(--color-text);
  border-color: var(--color-border);
}

.btn-secondary:hover {
  background-color: var(--color-background-soft);
  transform: translate(-2px, -2px);
  box-shadow: var(--shadow-brutal-hover);
}

.btn-delete {
  background: var(--color-background);
  border: var(--border-width-thin) solid var(--color-border);
  cursor: pointer;
  padding: var(--spacing-sm);
  transition: var(--transition-fast);
  box-shadow: var(--shadow-brutal);
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
}

.btn-delete:hover {
  background-color: var(--color-danger);
  color: white;
  transform: translate(-1px, -1px);
  box-shadow: 4px 4px 0px 0px var(--color-danger);
}

.btn-delete:hover svg {
  color: white;
  fill: white;
}

.btn-close {
  background: var(--color-background);
  border: var(--border-width-thin) solid var(--color-border);
  cursor: pointer;
  padding: var(--spacing-sm);
  transition: var(--transition-fast);
  box-shadow: var(--shadow-brutal);
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
}

.btn-close:hover {
  background-color: var(--color-danger);
  color: white;
  transform: translate(-1px, -1px);
  box-shadow: 4px 4px 0px 0px var(--color-danger);
}

.btn-close:hover svg {
  color: white;
  fill: white;
}

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

.modal {
  background-color: var(--color-background);
  border: var(--border-width) solid var(--color-border);
  box-shadow: var(--shadow-brutal);
  max-width: 450px;
  width: 100%;
  max-height: calc(100vh - 4rem);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-lg) var(--spacing-xl);
  border-bottom: var(--border-width) solid var(--color-border);
  background-color: var(--color-accent);
  color: white;
}

.modal-header h2 {
  margin: 0;
  color: white;
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-extrabold);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.project-form {
  padding: var(--spacing-xl);
  overflow-y: auto;
  flex: 1;
}

.form-group {
  margin-bottom: var(--spacing-lg);
}

.form-group label {
  display: block;
  margin-bottom: var(--spacing-sm);
  font-weight: var(--font-weight-bold);
  color: var(--color-text);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-size: var(--font-size-sm);
}

.form-input,
.form-textarea {
  width: 100%;
  padding: var(--spacing-md);
  border: var(--border-width) solid var(--color-border);
  font-size: var(--font-size-base);
  background-color: var(--color-background);
  color: var(--color-text);
  transition: var(--transition-fast);
  box-sizing: border-box;
  box-shadow: var(--shadow-brutal);
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--color-accent);
  box-shadow: var(--shadow-brutal-accent);
}

.form-input:hover,
.form-textarea:hover {
  transform: translate(-1px, -1px);
  box-shadow: var(--shadow-brutal-hover);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
  height: 80px;
}

.form-actions {
  display: flex;
  gap: var(--spacing-md);
  justify-content: flex-end;
  margin-top: var(--spacing-lg);
  padding: var(--spacing-lg) var(--spacing-xl);
  border-top: var(--border-width) solid var(--color-border);
  background-color: var(--color-background-soft);
}

.loading {
  text-align: center;
  padding: var(--spacing-3xl);
  color: var(--color-text);
  font-weight: var(--font-weight-bold);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  background-color: var(--color-background-soft);
  border: var(--border-width) solid var(--color-border);
  box-shadow: var(--shadow-brutal);
}

.empty-state {
  text-align: center;
  padding: var(--spacing-3xl) var(--spacing-xl);
  color: var(--color-text);
  background-color: var(--color-background-soft);
  border: var(--border-width) solid var(--color-border);
  box-shadow: var(--shadow-brutal);
}

.empty-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto var(--spacing-lg);
  color: var(--color-accent);
}

.empty-state h3 {
  margin: 0 0 var(--spacing-sm) 0;
  color: var(--color-heading);
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-extrabold);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.empty-state p {
  margin: 0 0 var(--spacing-xl) 0;
  font-size: var(--font-size-lg);
  color: var(--color-text-muted);
}

.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: var(--spacing-lg);
  margin: 0;
}

.project-card {
  background-color: var(--color-background);
  border: var(--border-width) solid var(--color-border);
  box-shadow: var(--shadow-brutal);
  padding: var(--spacing-xl);
  transition: var(--transition-fast);
}

.project-card:hover {
  transform: translate(-2px, -2px);
  box-shadow: var(--shadow-brutal-hover);
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-lg);
}

.project-name {
  margin: 0;
  color: var(--color-heading);
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  flex: 1;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.project-actions {
  display: flex;
  gap: var(--spacing-sm);
}

.project-id {
  margin-bottom: var(--spacing-lg);
  font-size: var(--font-size-sm);
}

.label {
  color: var(--color-text-muted);
  margin-right: var(--spacing-sm);
  font-weight: var(--font-weight-bold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

code {
  background-color: var(--color-background-soft);
  padding: var(--spacing-xs) var(--spacing-sm);
  border: var(--border-width-thin) solid var(--color-border);
  font-family: var(--font-family-mono);
  font-size: var(--font-size-xs);
  color: var(--color-text);
  font-weight: var(--font-weight-bold);
  box-shadow: var(--shadow-brutal);
}

.project-description {
  color: var(--color-text);
  line-height: 1.5;
  margin-bottom: var(--spacing-lg);
  font-size: var(--font-size-sm);
}

.project-meta {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-lg);
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.project-date {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  background-color: var(--color-background-soft);
  padding: var(--spacing-xs) var(--spacing-sm);
  border: var(--border-width-thin) solid var(--color-border);
  font-weight: var(--font-weight-bold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  box-shadow: var(--shadow-brutal);
}

.meta-icon {
  width: 12px;
  height: 12px;
  color: var(--color-accent);
}

.project-status {
  display: flex;
  justify-content: flex-end;
}

.status-badge {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-bold);
  padding: var(--spacing-xs) var(--spacing-sm);
  border: var(--border-width-thin) solid var(--color-border);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  box-shadow: var(--shadow-brutal);
}

.status-icon {
  width: 12px;
  height: 12px;
}

.status-active {
  background-color: var(--color-accent);
  color: white;
}

.status-inactive {
  background-color: var(--color-secondary);
  color: white;
}

.btn-close svg,
.btn-delete svg {
  width: 24px;
  height: 24px;
  color: var(--color-text);
  fill: currentColor;
}

/* Full screen optimizations */
@media (min-width: 1920px) {
  .projects-header {
    margin-bottom: var(--spacing-md);
  }
  
  .projects-grid {
    gap: var(--spacing-md);
  }
  
  .project-card {
    padding: var(--spacing-lg);
  }
  
  .project-header {
    margin-bottom: var(--spacing-md);
  }
  
  .project-id {
    margin-bottom: var(--spacing-md);
  }
  
  .project-description {
    margin-bottom: var(--spacing-md);
  }
  
  .project-meta {
    margin-bottom: var(--spacing-md);
  }
}

/* Delete Confirmation Modal Styles */
.delete-modal-content {
  padding: var(--spacing-xl);
  overflow-y: auto;
  flex: 1;
}

.delete-warning {
  text-align: center;
  margin-bottom: var(--spacing-xl);
  padding: var(--spacing-lg);
  background-color: var(--color-background-soft);
  border: var(--border-width) solid var(--color-border);
  box-shadow: var(--shadow-brutal);
}

.warning-icon {
  width: 48px;
  height: 48px;
  margin: 0 auto var(--spacing-md);
  color: var(--color-danger);
  display: flex;
  align-items: center;
  justify-content: center;
}

.warning-icon svg {
  width: 48px;
  height: 48px;
}

.delete-warning h3 {
  margin: 0 0 var(--spacing-sm) 0;
  color: var(--color-danger);
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-extrabold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.delete-warning p {
  margin: 0;
  color: var(--color-text);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-bold);
}

.project-to-delete {
  margin-bottom: var(--spacing-xl);
  padding: var(--spacing-lg);
  background-color: var(--color-background);
  border: var(--border-width) solid var(--color-border);
  box-shadow: var(--shadow-brutal);
}

.project-info h4 {
  margin: 0 0 var(--spacing-md) 0;
  color: var(--color-heading);
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-extrabold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.project-info .project-id {
  margin-bottom: var(--spacing-md);
  font-size: var(--font-size-sm);
}

.project-info .project-description {
  color: var(--color-text);
  line-height: 1.5;
  font-size: var(--font-size-sm);
  font-style: italic;
}

.deletion-impact {
  padding: var(--spacing-lg);
  background-color: var(--color-background-soft);
  border: var(--border-width) solid var(--color-border);
  box-shadow: var(--shadow-brutal);
}

.impact-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
  padding: var(--spacing-sm);
  background-color: var(--color-background);
  border: var(--border-width-thin) solid var(--color-border);
  box-shadow: var(--shadow-brutal);
}

.impact-label {
  font-weight: var(--font-weight-bold);
  color: var(--color-text);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-size: var(--font-size-sm);
}

.impact-value {
  font-weight: var(--font-weight-extrabold);
  color: var(--color-danger);
  font-size: var(--font-size-lg);
  background-color: var(--color-background-soft);
  padding: var(--spacing-xs) var(--spacing-sm);
  border: var(--border-width-thin) solid var(--color-border);
  box-shadow: var(--shadow-brutal);
}

.impact-description {
  margin: 0;
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-bold);
  text-align: center;
}

.btn-danger {
  background-color: var(--color-danger);
  color: white;
  border-color: var(--color-border);
}

.btn-danger:hover {
  background-color: #dc2626;
  transform: translate(-2px, -2px);
  box-shadow: var(--shadow-brutal-danger);
}

.btn-danger:hover svg {
  color: white;
  fill: white;
}
</style>
