<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { 
  PlusIcon, 
  TrashIcon, 
  XMarkIcon,
  DocumentTextIcon,
  TagIcon,
  CalendarIcon,
  MagnifyingGlassIcon,
  ChevronUpIcon,
  ChevronDownIcon,
  PencilIcon
} from '@heroicons/vue/24/outline'
import type { 
  ContextItem, 
  ContextProject, 
  ContextSearchQuery, 
  ContextSearchResult,
  ContextItemCreate,
  ContextItemUpdate
} from '@/types/api'
import { SearchType } from '@/types/api'

const contextItems = ref<ContextItem[]>([])
const projects = ref<ContextProject[]>([])
const loading = ref(false)
const showCreateForm = ref(false)
const showEditForm = ref(false)
const showProjectDropdown = ref(false)
const showEditProjectDropdown = ref(false)
const projectSearchQuery = ref('')
const editProjectSearchQuery = ref('')

// Enhanced search state
const searchQuery = ref('')
const searchType = ref<string>('hybrid')
const searchResults = ref<ContextSearchResult | null>(null)
const isSearching = ref(false)
const showSearchFilters = ref(false)
const selectedContentTypes = ref<string[]>([])
const selectedTags = ref<string[]>([])
const selectedProject = ref<string>('')
const semanticWeight = ref(0.7)

// Sorting state
const sortField = ref<keyof ContextItem | null>(null)
const sortDirection = ref<'asc' | 'desc'>('asc')

const newContext = ref<ContextItemCreate>({
  title: '',
  content: '',
  content_type: 'text',
  tags: [],
  extra_metadata: {},
  project_id: ''
})

const newContextTagsString = ref('')

interface EditContextForm {
  id: number
  title: string
  content: string
  content_type: string
  tags: string
  project_id: string
}

const editContext = ref<EditContextForm>({
  id: 0,
  title: '',
  content: '',
  content_type: 'text',
  tags: '',
  project_id: ''
})

const contentTypes = ['text', 'code', 'markdown', 'json']

onMounted(() => {
  fetchContextItems()
  fetchProjects()
})

const fetchContextItems = async () => {
  loading.value = true
  try {
    const response = await fetch('/api/context/items?limit=50')
    if (response.ok) {
      const data = await response.json()
      contextItems.value = data || []
    } else {
      console.error('Failed to fetch context items:', response.status, response.statusText)
    }
  } catch (error) {
    console.error('Error fetching context items:', error)
  } finally {
    loading.value = false
  }
}

const fetchProjects = async () => {
  try {
    const response = await fetch('/api/context/projects')
    if (response.ok) {
      const data = await response.json()
      projects.value = data || []
    } else {
      console.error('Failed to fetch projects:', response.status, response.statusText)
    }
  } catch (error) {
    console.error('Error fetching projects:', error)
  }
}

const createContext = async () => {
  try {
    const payload: ContextItemCreate = {
      ...newContext.value,
      tags: newContext.value.tags && newContext.value.tags.length > 0 ? newContext.value.tags : []
    }

    const response = await fetch('/api/context/items', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    })

    if (response.ok) {
      showCreateForm.value = false
      resetForm()
      fetchContextItems()
    }
  } catch (error) {
    console.error('Error creating context:', error)
  }
}

const deleteContext = async (id: number) => {
  if (!confirm('Are you sure you want to delete this context item?')) {
    return
  }

  try {
    const response = await fetch(`/api/context/items/${id}`, {
      method: 'DELETE',
    })

    if (response.ok) {
      fetchContextItems()
    }
  } catch (error) {
    console.error('Error deleting context:', error)
  }
}

const resetForm = () => {
  newContext.value = {
    title: '',
    content: '',
    content_type: 'text',
    tags: [],
    extra_metadata: {},
    project_id: ''
  }
  newContextTagsString.value = ''
}

const openEditForm = (item: ContextItem) => {
  editContext.value = {
    id: item.id,
    title: item.title,
    content: item.content,
    content_type: item.content_type,
    tags: item.tags.join(', '),
    project_id: item.project_id || ''
  }
  
  // Set the project search query for display
  if (item.project_id) {
    const project = projects.value.find(p => p.id === item.project_id)
    editProjectSearchQuery.value = project ? project.name : item.project_id
  } else {
    editProjectSearchQuery.value = ''
  }
  
  showEditForm.value = true
}

const updateContext = async () => {
  try {
    const payload: ContextItemUpdate = {
      title: editContext.value.title,
      content: editContext.value.content,
      content_type: editContext.value.content_type,
      tags: editContext.value.tags.split(',').map(tag => tag.trim()).filter(tag => tag),
      project_id: editContext.value.project_id || undefined
    }

    const response = await fetch(`/api/context/items/${editContext.value.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    })

    if (response.ok) {
      showEditForm.value = false
      fetchContextItems()
    }
  } catch (error) {
    console.error('Error updating context:', error)
  }
}

const resetEditForm = () => {
  editContext.value = {
    id: 0,
    title: '',
    content: '',
    content_type: 'text',
    tags: '',
    project_id: ''
  }
  editProjectSearchQuery.value = ''
}

// Enhanced search functionality
const performSearch = async () => {
  if (!searchQuery.value.trim()) {
    searchResults.value = null
    return
  }

  isSearching.value = true
  try {
    // Build query parameters for GET request
    const params = new URLSearchParams({
      query: searchQuery.value,
      limit: '50',
      offset: '0'
    })

    // Add optional filters
    if (selectedContentTypes.value && selectedContentTypes.value.length > 0) {
      selectedContentTypes.value.forEach(type => params.append('content_types', type))
    }
    if (selectedTags.value && selectedTags.value.length > 0) {
      selectedTags.value.forEach(tag => params.append('tags', tag))
    }
    if (selectedProject.value) {
      params.append('project_id', selectedProject.value)
    }
    if (searchType.value === 'hybrid') {
      params.append('semantic_weight', semanticWeight.value.toString())
    }

    // Use specific endpoint based on search type
    let endpoint = '/api/context/items/search'
    if (searchType.value === 'semantic') {
      endpoint = '/api/context/items/search/semantic'
    } else if (searchType.value === 'keyword') {
      endpoint = '/api/context/items/search/keyword'
    } else if (searchType.value === 'hybrid') {
      endpoint = '/api/context/items/search/hybrid'
    }

    const response = await fetch(`${endpoint}?${params.toString()}`)

    if (response.ok) {
      const data = await response.json()
      searchResults.value = data
    } else {
      console.error('Search failed:', response.status, response.statusText)
      const errorText = await response.text()
      console.error('Error details:', errorText)
    }
  } catch (error) {
    console.error('Error performing search:', error)
  } finally {
    isSearching.value = false
  }
}

const clearSearch = () => {
  searchQuery.value = ''
  searchResults.value = null
  selectedContentTypes.value = []
  selectedTags.value = []
  selectedProject.value = ''
  semanticWeight.value = 0.7
  searchType.value = 'hybrid'
}

const toggleSearchFilters = () => {
  showSearchFilters.value = !showSearchFilters.value
}

// Get unique content types and tags for filters
const availableContentTypes = computed(() => {
  const types = new Set<string>()
  contextItems.value.forEach(item => types.add(item.content_type || 'text'))
  return Array.from(types)
})

const availableTags = computed(() => {
  const tags = new Set<string>()
  contextItems.value.forEach(item => {
    if (item.tags && Array.isArray(item.tags)) {
      item.tags.forEach(tag => tags.add(tag))
    }
  })
  return Array.from(tags)
})

// Helper function to update tags from string input
const updateTagsFromString = (event: Event) => {
  const input = event.target as HTMLInputElement
  const tagString = input.value
  newContext.value.tags = tagString.split(',').map(tag => tag.trim()).filter(tag => tag)
}

const formatDate = (dateString: string) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString()
}

const truncateContent = (content: string, maxLength: number = 150) => {
  if (!content) return ''
  return content.length > maxLength ? content.substring(0, maxLength) + '...' : content
}

const filteredProjects = computed(() => {
  if (!projectSearchQuery.value) {
    return projects.value
  }
  return projects.value.filter(project => 
    project.name.toLowerCase().includes(projectSearchQuery.value.toLowerCase()) ||
    project.id.toLowerCase().includes(projectSearchQuery.value.toLowerCase())
  )
})

const filteredEditProjects = computed(() => {
  if (!editProjectSearchQuery.value) {
    return projects.value
  }
  return projects.value.filter(project => 
    project.name.toLowerCase().includes(editProjectSearchQuery.value.toLowerCase()) ||
    project.id.toLowerCase().includes(editProjectSearchQuery.value.toLowerCase())
  )
})

// Filtered and sorted context items
const filteredContextItems = computed(() => {
  // Use search results if available, otherwise use all context items
  let filtered = searchResults.value ? searchResults.value.items : contextItems.value

  // Apply sorting (search results are already sorted by relevance, but we can still sort by other fields)
  if (sortField.value && !searchResults.value) {
    filtered = [...filtered].sort((a, b) => {
      let aValue: any = a[sortField.value!]
      let bValue: any = b[sortField.value!]

      // Handle different data types
      if (sortField.value === 'created_at') {
        aValue = aValue ? new Date(aValue as string).getTime() : 0
        bValue = bValue ? new Date(bValue as string).getTime() : 0
      } else if (sortField.value === 'tags') {
        aValue = (aValue as string[] || []).join(', ')
        bValue = (bValue as string[] || []).join(', ')
      } else if (typeof aValue === 'string' && typeof bValue === 'string') {
        aValue = aValue.toLowerCase()
        bValue = bValue.toLowerCase()
      }

      // Handle undefined values
      if (aValue === undefined || aValue === null) aValue = ''
      if (bValue === undefined || bValue === null) bValue = ''

      if (aValue < bValue) return sortDirection.value === 'asc' ? -1 : 1
      if (aValue > bValue) return sortDirection.value === 'asc' ? 1 : -1
      return 0
    })
  }

  return filtered
})

const selectProject = (project: ContextProject) => {
  newContext.value.project_id = project.id
  showProjectDropdown.value = false
  projectSearchQuery.value = project.name
}

const clearProject = () => {
  newContext.value.project_id = ''
  projectSearchQuery.value = ''
}

const selectEditProject = (project: ContextProject) => {
  editContext.value.project_id = project.id
  showEditProjectDropdown.value = false
  editProjectSearchQuery.value = project.name
}

const clearEditProject = () => {
  editContext.value.project_id = ''
  editProjectSearchQuery.value = ''
}

const closeDropdown = () => {
  showProjectDropdown.value = false
  showEditProjectDropdown.value = false
}

const handleSort = (field: keyof ContextItem) => {
  if (sortField.value === field) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortField.value = field
    sortDirection.value = 'asc'
  }
}

// Content input helpers
const getContentPlaceholder = (contentType: string) => {
  const placeholders = {
    text: 'Enter your text content here...',
    code: '// Enter your code here...\nfunction example() {\n  return "Hello World";\n}',
    markdown: '# Enter your markdown here...\n\n**Bold text** and *italic text*',
    json: '{\n  "key": "value",\n  "array": [1, 2, 3]\n}'
  }
  return placeholders[contentType as keyof typeof placeholders] || 'Enter content here...'
}

const getContentRows = (contentType: string) => {
  const rowCounts = {
    text: 4,
    code: 8,
    markdown: 6,
    json: 6
  }
  return rowCounts[contentType as keyof typeof rowCounts] || 4
}

const handleContentInput = (event: Event) => {
  const textarea = event.target as HTMLTextAreaElement
  // Auto-resize textarea
  textarea.style.height = 'auto'
  textarea.style.height = textarea.scrollHeight + 'px'
}

const handleEditContentInput = (event: Event) => {
  const textarea = event.target as HTMLTextAreaElement
  // Auto-resize textarea
  textarea.style.height = 'auto'
  textarea.style.height = textarea.scrollHeight + 'px'
}

// Simple markdown renderer
const renderMarkdown = (content: string) => {
  return content
    .replace(/^# (.*$)/gim, '<h1>$1</h1>')
    .replace(/^## (.*$)/gim, '<h2>$1</h2>')
    .replace(/^### (.*$)/gim, '<h3>$1</h3>')
    .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
    .replace(/\*(.*)\*/gim, '<em>$1</em>')
    .replace(/`(.*)`/gim, '<code>$1</code>')
    .replace(/\n/gim, '<br>')
}
</script>

<template>
  <div class="contexts">
    <div class="contexts-header">
      <h1>CONTEXT ITEMS</h1>
      <button @click="showCreateForm = true" class="btn btn-primary">
        <PlusIcon class="btn-icon" />
        ADD CONTEXT
      </button>
    </div>

    <!-- Enhanced Search Bar -->
    <div class="search-container">
      <div class="search-main">
        <div class="search-input-wrapper">
          <MagnifyingGlassIcon class="search-icon" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search context items with semantic, keyword, or hybrid search..."
            class="search-input"
            @keyup.enter="performSearch"
          />
        </div>
        <div class="search-controls">
          <select v-model="searchType" class="search-type-select">
            <option value="hybrid">Hybrid</option>
            <option value="semantic">Semantic</option>
            <option value="keyword">Keyword</option>
          </select>
          <button @click="performSearch" class="btn btn-primary search-btn" :disabled="isSearching">
            {{ isSearching ? 'SEARCHING...' : 'SEARCH' }}
          </button>
          <button @click="clearSearch" class="btn btn-secondary" v-if="searchResults">
            CLEAR
          </button>
          <button @click="toggleSearchFilters" class="btn btn-secondary">
            {{ showSearchFilters ? 'HIDE FILTERS' : 'FILTERS' }}
          </button>
        </div>
      </div>
      
      <!-- Search Filters -->
      <div v-if="showSearchFilters" class="search-filters">
        <div class="filter-row">
          <div class="filter-group">
            <label>Content Types:</label>
            <div class="filter-checkboxes">
              <label v-for="type in availableContentTypes" :key="type" class="filter-checkbox">
                <input 
                  type="checkbox" 
                  :value="type" 
                  v-model="selectedContentTypes"
                />
                {{ type.toUpperCase() }}
              </label>
            </div>
          </div>
          
          <div class="filter-group">
            <label>Tags:</label>
            <div class="filter-checkboxes">
              <label v-for="tag in availableTags.slice(0, 10)" :key="tag" class="filter-checkbox">
                <input 
                  type="checkbox" 
                  :value="tag" 
                  v-model="selectedTags"
                />
                {{ tag.toUpperCase() }}
              </label>
            </div>
          </div>
          
          <div class="filter-group">
            <label>Project:</label>
            <select v-model="selectedProject" class="filter-select">
              <option value="">All Projects</option>
              <option v-for="project in projects" :key="project.id" :value="project.id">
                {{ project.name }}
              </option>
            </select>
          </div>
          
          <div v-if="searchType === 'hybrid'" class="filter-group">
            <label>Semantic Weight: {{ semanticWeight }}</label>
            <input 
              type="range" 
              v-model="semanticWeight" 
              min="0" 
              max="1" 
              step="0.1" 
              class="filter-range"
            />
          </div>
        </div>
      </div>
      
      <!-- Search Results Info -->
      <div v-if="searchResults" class="search-results-info">
        <div class="results-stats">
          <span class="results-count">{{ searchResults.total }} results</span>
          <span class="search-type-badge">{{ searchResults.search_type.toUpperCase() }}</span>
          <span v-if="searchResults.execution_time_ms" class="execution-time">
            {{ searchResults.execution_time_ms.toFixed(2) }}ms
          </span>
        </div>
        <div class="results-query">
          Query: "{{ searchResults.query }}"
        </div>
      </div>
    </div>

    <!-- Create Form Modal -->
    <div v-if="showCreateForm" class="modal-overlay" @click="showCreateForm = false; closeDropdown()">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h2>ADD NEW CONTEXT</h2>
          <button @click="showCreateForm = false" class="btn-close">
            <XMarkIcon />
          </button>
        </div>
        <form @submit.prevent="createContext" class="context-form">
          <div class="form-row">
            <div class="form-group">
              <label for="title">TITLE</label>
              <input
                id="title"
                v-model="newContext.title"
                type="text"
                required
                class="form-input"
                placeholder="Enter context title"
              />
            </div>

            <div class="form-group">
              <label for="content_type">CONTENT TYPE</label>
              <select id="content_type" v-model="newContext.content_type" class="form-select">
                <option v-for="type in contentTypes" :key="type" :value="type">
                  {{ type.toUpperCase() }}
                </option>
              </select>
            </div>
          </div>

          <div class="form-group content-group">
            <label for="content">CONTENT</label>
            <div class="content-layout">
              <div class="content-input-section">
                <textarea
                  id="content"
                  v-model="newContext.content"
                  required
                  class="form-textarea content-textarea"
                  :class="`content-type-${newContext.content_type}`"
                  :placeholder="getContentPlaceholder(newContext.content_type)"
                  :rows="getContentRows(newContext.content_type)"
                  @input="handleContentInput"
                ></textarea>
              </div>
              <div v-if="newContext.content" class="content-preview-section">
                <div class="content-preview">
                  <div class="preview-header">
                    <span class="preview-label">PREVIEW</span>
                    <span class="content-type-indicator">{{ newContext.content_type.toUpperCase() }}</span>
                  </div>
                  <div class="preview-content" :class="`preview-${newContext.content_type}`">
                    <pre v-if="newContext.content_type === 'code' || newContext.content_type === 'json'" class="code-preview">{{ newContext.content }}</pre>
                    <div v-else-if="newContext.content_type === 'markdown'" class="markdown-preview" v-html="renderMarkdown(newContext.content)"></div>
                    <div v-else class="text-preview">{{ newContext.content }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="tags">TAGS (comma-separated)</label>
              <input
                id="tags"
                v-model="newContextTagsString"
                type="text"
                class="form-input"
                placeholder="tag1, tag2, tag3"
                @input="updateTagsFromString"
              />
            </div>

            <div class="form-group">
              <label for="project_id">PROJECT (optional)</label>
              <div class="project-dropdown-container">
                <input
                  id="project_id"
                  v-model="projectSearchQuery"
                  type="text"
                  class="form-input"
                  placeholder="Search for a project..."
                  @focus="showProjectDropdown = true"
                  @input="showProjectDropdown = true"
                  autocomplete="off"
                />
                <button 
                  v-if="newContext.project_id" 
                  @click="clearProject" 
                  type="button" 
                  class="btn-clear-project"
                  title="Clear project"
                >
                  <XMarkIcon />
                </button>
                
                <div v-if="showProjectDropdown" class="project-dropdown">
                  <div v-if="filteredProjects.length === 0" class="dropdown-empty">
                    No projects found
                  </div>
                  <div 
                    v-for="project in filteredProjects" 
                    :key="project.id"
                    @click="selectProject(project)"
                    class="dropdown-item"
                  >
                    <div class="project-name">{{ project.name }}</div>
                    <div class="project-id">{{ project.id }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="form-actions">
            <button type="button" @click="showCreateForm = false" class="btn btn-secondary">
              CANCEL
            </button>
            <button type="submit" class="btn btn-primary">
              CREATE CONTEXT
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Edit Form Modal -->
    <div v-if="showEditForm" class="modal-overlay" @click="showEditForm = false; closeDropdown()">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h2>EDIT CONTEXT</h2>
          <button @click="showEditForm = false" class="btn-close">
            <XMarkIcon />
          </button>
        </div>
        <form @submit.prevent="updateContext" class="context-form">
          <div class="form-row">
            <div class="form-group">
              <label for="edit-title">TITLE</label>
              <input
                id="edit-title"
                v-model="editContext.title"
                type="text"
                required
                class="form-input"
                placeholder="Enter context title"
              />
            </div>

            <div class="form-group">
              <label for="edit-content_type">CONTENT TYPE</label>
              <select id="edit-content_type" v-model="editContext.content_type" class="form-select">
                <option v-for="type in contentTypes" :key="type" :value="type">
                  {{ type.toUpperCase() }}
                </option>
              </select>
            </div>
          </div>

          <div class="form-group content-group">
            <label for="edit-content">CONTENT</label>
            <div class="content-layout">
              <div class="content-input-section">
                <textarea
                  id="edit-content"
                  v-model="editContext.content"
                  required
                  class="form-textarea content-textarea"
                  :class="`content-type-${editContext.content_type}`"
                  :placeholder="getContentPlaceholder(editContext.content_type || 'text')"
                  :rows="getContentRows(editContext.content_type || 'text')"
                  @input="handleEditContentInput"
                ></textarea>
              </div>
              <div v-if="editContext.content" class="content-preview-section">
                <div class="content-preview">
                  <div class="preview-header">
                    <span class="preview-label">PREVIEW</span>
                    <span class="content-type-indicator">{{ (editContext.content_type || 'text').toUpperCase() }}</span>
                  </div>
                  <div class="preview-content" :class="`preview-${editContext.content_type}`">
                    <pre v-if="editContext.content_type === 'code' || editContext.content_type === 'json'" class="code-preview">{{ editContext.content }}</pre>
                    <div v-else-if="editContext.content_type === 'markdown'" class="markdown-preview" v-html="renderMarkdown(editContext.content)"></div>
                    <div v-else class="text-preview">{{ editContext.content }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="edit-tags">TAGS (comma-separated)</label>
              <input
                id="edit-tags"
                v-model="editContext.tags"
                type="text"
                class="form-input"
                placeholder="tag1, tag2, tag3"
              />
            </div>

            <div class="form-group">
              <label for="edit-project_id">PROJECT (optional)</label>
              <div class="project-dropdown-container">
                <input
                  id="edit-project_id"
                  v-model="editProjectSearchQuery"
                  type="text"
                  class="form-input"
                  placeholder="Search for a project..."
                  @focus="showEditProjectDropdown = true"
                  @input="showEditProjectDropdown = true"
                  autocomplete="off"
                />
                <button 
                  v-if="editContext.project_id" 
                  @click="clearEditProject" 
                  type="button" 
                  class="btn-clear-project"
                  title="Clear project"
                >
                  <XMarkIcon />
                </button>
                
                <div v-if="showEditProjectDropdown" class="project-dropdown">
                  <div v-if="filteredEditProjects.length === 0" class="dropdown-empty">
                    No projects found
                  </div>
                  <div 
                    v-for="project in filteredEditProjects" 
                    :key="project.id"
                    @click="selectEditProject(project)"
                    class="dropdown-item"
                  >
                    <div class="project-name">{{ project.name }}</div>
                    <div class="project-id">{{ project.id }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="form-actions">
            <button type="button" @click="showEditForm = false" class="btn btn-secondary">
              CANCEL
            </button>
            <button type="submit" class="btn btn-primary">
              UPDATE CONTEXT
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Context Items List -->
    <div v-if="loading" class="loading">
      LOADING CONTEXT ITEMS...
    </div>

    <div v-else-if="contextItems.length === 0" class="empty-state">
      <div class="empty-icon">
        <DocumentTextIcon />
      </div>
      <h3>NO CONTEXT ITEMS YET</h3>
      <p>Create your first context item to get started.</p>
      <button @click="showCreateForm = true" class="btn btn-primary">
        <PlusIcon class="btn-icon" />
        ADD FIRST CONTEXT
      </button>
    </div>

    <div v-else class="table-container">
      <table class="contexts-table">
        <thead>
          <tr>
            <th @click="handleSort('title')" class="sortable">
              <div class="th-content">
                TITLE
                <div class="sort-indicators">
                  <ChevronUpIcon 
                    :class="['sort-icon', { active: sortField === 'title' && sortDirection === 'asc' }]" 
                  />
                  <ChevronDownIcon 
                    :class="['sort-icon', { active: sortField === 'title' && sortDirection === 'desc' }]" 
                  />
                </div>
              </div>
            </th>
            <th @click="handleSort('content_type')" class="sortable">
              <div class="th-content">
                TYPE
                <div class="sort-indicators">
                  <ChevronUpIcon 
                    :class="['sort-icon', { active: sortField === 'content_type' && sortDirection === 'asc' }]" 
                  />
                  <ChevronDownIcon 
                    :class="['sort-icon', { active: sortField === 'content_type' && sortDirection === 'desc' }]" 
                  />
                </div>
              </div>
            </th>
            <th @click="handleSort('content')" class="sortable">
              <div class="th-content">
                CONTENT
                <div class="sort-indicators">
                  <ChevronUpIcon 
                    :class="['sort-icon', { active: sortField === 'content' && sortDirection === 'asc' }]" 
                  />
                  <ChevronDownIcon 
                    :class="['sort-icon', { active: sortField === 'content' && sortDirection === 'desc' }]" 
                  />
                </div>
              </div>
            </th>
            <th @click="handleSort('tags')" class="sortable">
              <div class="th-content">
                TAGS
                <div class="sort-indicators">
                  <ChevronUpIcon 
                    :class="['sort-icon', { active: sortField === 'tags' && sortDirection === 'asc' }]" 
                  />
                  <ChevronDownIcon 
                    :class="['sort-icon', { active: sortField === 'tags' && sortDirection === 'desc' }]" 
                  />
                </div>
              </div>
            </th>
            <th @click="handleSort('created_at')" class="sortable">
              <div class="th-content">
                CREATED
                <div class="sort-indicators">
                  <ChevronUpIcon 
                    :class="['sort-icon', { active: sortField === 'created_at' && sortDirection === 'asc' }]" 
                  />
                  <ChevronDownIcon 
                    :class="['sort-icon', { active: sortField === 'created_at' && sortDirection === 'desc' }]" 
                  />
                </div>
              </div>
            </th>
            <th>PROJECT</th>
            <th>ACTIONS</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in filteredContextItems" :key="item.id" class="table-row">
            <td class="title-cell">
              <div class="title-content">
                <DocumentTextIcon class="cell-icon" />
                <span class="title-text">{{ item.title }}</span>
              </div>
            </td>
            <td class="type-cell">
              <span class="type-badge">{{ (item.content_type || 'text').toUpperCase() }}</span>
            </td>
            <td class="content-cell">
              <div class="content-preview">{{ truncateContent(item.content, 100) }}</div>
            </td>
            <td class="tags-cell">
              <div v-if="item.tags && item.tags.length > 0" class="tags-list">
                <span v-for="tag in item.tags.slice(0, 2)" :key="tag" class="tag">
                  {{ tag.toUpperCase() }}
                </span>
                <span v-if="item.tags && item.tags.length > 2" class="more-tags">
                  +{{ item.tags.length - 2 }}
                </span>
              </div>
              <span v-else class="no-tags">No tags</span>
            </td>
            <td class="date-cell">
              <div class="date-content">
                <CalendarIcon class="cell-icon" />
                <span>{{ formatDate(item.created_at) }}</span>
              </div>
            </td>
            <td class="project-cell">
              <span v-if="item.project_id" class="project-badge">{{ item.project_id }}</span>
              <span v-else class="no-project">-</span>
            </td>
            <td class="actions-cell">
              <div class="actions-group">
                <button @click="openEditForm(item)" class="btn-edit" title="Edit">
                  <PencilIcon />
                </button>
                <button @click="deleteContext(item.id)" class="btn-delete" title="Delete">
                  <TrashIcon />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.contexts {
  width: 100%;
  margin: 0;
  padding: 0;
}

.contexts-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
}

.contexts-header h1 {
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

.btn-close svg,
.btn-delete svg {
  width: 24px;
  height: 24px;
  color: var(--color-text);
  fill: currentColor;
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
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal {
  background-color: var(--color-background);
  border: var(--border-width) solid var(--color-border);
  box-shadow: var(--shadow-brutal);
  max-width: 900px;
  width: 100%;
  max-height: calc(100vh - 4rem);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  animation: slideIn 0.2s ease-out;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-lg) var(--spacing-xl);
  border-bottom: var(--border-width) solid var(--color-border);
  flex-shrink: 0;
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

.context-form {
  padding: var(--spacing-xl);
  overflow-y: auto;
  flex: 1;
}

.form-group {
  margin-bottom: var(--spacing-lg);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-lg);
}

.form-row .form-group {
  margin-bottom: 0;
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
.form-select,
.form-textarea {
  width: 100%;
  padding: var(--spacing-md);
  border: var(--border-width) solid var(--color-border);
  font-size: var(--font-size-base);
  background-color: var(--color-background);
  color: var(--color-text);
  transition: var(--transition-fast);
  font-family: inherit;
  box-sizing: border-box;
  box-shadow: var(--shadow-brutal);
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--color-accent);
  box-shadow: var(--shadow-brutal-accent);
}

.form-input:hover,
.form-select:hover,
.form-textarea:hover {
  transform: translate(-1px, -1px);
  box-shadow: var(--shadow-brutal-hover);
}

.form-textarea {
  resize: vertical;
  min-height: 100px;
  height: 100px;
  line-height: 1.5;
}

/* Enhanced Content Input Styles */
.content-group {
  margin-bottom: var(--spacing-xl);
}

.content-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-lg);
  align-items: start;
}

.content-input-section {
  display: flex;
  flex-direction: column;
}

.content-preview-section {
  display: flex;
  flex-direction: column;
}

.content-input-container {
  position: relative;
}

.content-textarea {
  font-family: var(--font-family-mono);
  font-size: var(--font-size-sm);
  line-height: 1.6;
  min-height: 120px;
  max-height: 400px;
  overflow-y: auto;
  transition: all var(--transition-fast);
}

.content-textarea:focus {
  min-height: 200px;
  box-shadow: var(--shadow-brutal-accent);
  border-color: var(--color-accent);
}

.content-type-text {
  font-family: inherit;
  font-size: var(--font-size-base);
}

.content-type-code,
.content-type-json {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: var(--font-size-sm);
  background-color: var(--color-background-soft);
  border-left: 4px solid var(--color-accent);
}

.content-type-markdown {
  font-family: var(--font-family-mono);
  font-size: var(--font-size-sm);
  background-color: var(--color-background-soft);
  border-left: 4px solid var(--color-accent);
}

/* Content Preview Styles */
.content-preview {
  border: var(--border-width) solid var(--color-border);
  background-color: var(--color-background-soft);
  box-shadow: var(--shadow-brutal);
  border-radius: 0;
  overflow: hidden;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-sm) var(--spacing-md);
  background-color: var(--color-accent);
  color: white;
  border-bottom: var(--border-width) solid var(--color-border);
}

.preview-label {
  font-weight: var(--font-weight-bold);
  font-size: var(--font-size-xs);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.content-type-indicator {
  background-color: rgba(255, 255, 255, 0.2);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: 0;
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-bold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.preview-content {
  padding: var(--spacing-md);
  flex: 1;
  overflow-y: auto;
  min-height: 200px;
}

.preview-text {
  white-space: pre-wrap;
  line-height: 1.6;
  color: var(--color-text);
}

.code-preview {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: var(--font-size-sm);
  line-height: 1.5;
  background-color: var(--color-background);
  padding: var(--spacing-md);
  border: var(--border-width-thin) solid var(--color-border);
  border-radius: 0;
  overflow-x: auto;
  white-space: pre;
  color: var(--color-text);
  margin: 0;
}

.markdown-preview {
  line-height: 1.6;
  color: var(--color-text);
}

.markdown-preview h1,
.markdown-preview h2,
.markdown-preview h3 {
  margin: var(--spacing-md) 0 var(--spacing-sm) 0;
  color: var(--color-heading);
  font-weight: var(--font-weight-bold);
}

.markdown-preview h1 {
  font-size: var(--font-size-xl);
  border-bottom: var(--border-width-thin) solid var(--color-border);
  padding-bottom: var(--spacing-xs);
}

.markdown-preview h2 {
  font-size: var(--font-size-lg);
}

.markdown-preview h3 {
  font-size: var(--font-size-base);
}

.markdown-preview strong {
  font-weight: var(--font-weight-bold);
  color: var(--color-heading);
}

.markdown-preview em {
  font-style: italic;
}

.markdown-preview code {
  background-color: var(--color-background);
  padding: var(--spacing-xs) var(--spacing-sm);
  border: var(--border-width-thin) solid var(--color-border);
  border-radius: 0;
  font-family: var(--font-family-mono);
  font-size: var(--font-size-sm);
  color: var(--color-accent);
}

.text-preview {
  white-space: pre-wrap;
  line-height: 1.6;
  color: var(--color-text);
}

.form-actions {
  display: flex;
  gap: var(--spacing-md);
  justify-content: flex-end;
  margin-top: var(--spacing-lg);
  padding: var(--spacing-lg) var(--spacing-xl);
  border-top: var(--border-width) solid var(--color-border);
  flex-shrink: 0;
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

/* Enhanced Search Container */
.search-container {
  margin-bottom: var(--spacing-lg);
  background-color: var(--color-background-soft);
  border: var(--border-width) solid var(--color-border);
  box-shadow: var(--shadow-brutal);
  padding: var(--spacing-lg);
}

.search-main {
  display: flex;
  gap: var(--spacing-md);
  align-items: center;
  margin-bottom: var(--spacing-md);
}

.search-input-wrapper {
  position: relative;
  flex: 1;
  max-width: 600px;
}

.search-icon {
  position: absolute;
  left: var(--spacing-md);
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  color: var(--color-text-muted);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: var(--spacing-md) var(--spacing-md) var(--spacing-md) 48px;
  border: var(--border-width) solid var(--color-border);
  font-size: var(--font-size-base);
  background-color: var(--color-background);
  color: var(--color-text);
  transition: var(--transition-fast);
  font-family: inherit;
  box-sizing: border-box;
  box-shadow: var(--shadow-brutal);
}

.search-input:focus {
  outline: none;
  border-color: var(--color-accent);
  box-shadow: var(--shadow-brutal-accent);
}

.search-input:hover {
  transform: translate(-1px, -1px);
  box-shadow: var(--shadow-brutal-hover);
}

.search-controls {
  display: flex;
  gap: var(--spacing-sm);
  align-items: center;
  flex-shrink: 0;
}

.search-type-select {
  padding: var(--spacing-sm) var(--spacing-md);
  border: var(--border-width) solid var(--color-border);
  background-color: var(--color-background);
  color: var(--color-text);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-bold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  box-shadow: var(--shadow-brutal);
  cursor: pointer;
}

.search-type-select:focus {
  outline: none;
  border-color: var(--color-accent);
  box-shadow: var(--shadow-brutal-accent);
}

.search-btn {
  min-width: 100px;
}

/* Search Filters */
.search-filters {
  border-top: var(--border-width) solid var(--color-border);
  padding-top: var(--spacing-md);
  margin-top: var(--spacing-md);
}

.filter-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-lg);
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.filter-group label {
  font-weight: var(--font-weight-bold);
  color: var(--color-text);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-size: var(--font-size-sm);
}

.filter-checkboxes {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-sm);
}

.filter-checkbox {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-bold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  cursor: pointer;
  padding: var(--spacing-xs) var(--spacing-sm);
  border: var(--border-width-thin) solid var(--color-border);
  background-color: var(--color-background);
  box-shadow: var(--shadow-brutal);
  transition: var(--transition-fast);
}

.filter-checkbox:hover {
  background-color: var(--color-background-soft);
  transform: translate(-1px, -1px);
  box-shadow: var(--shadow-brutal-hover);
}

.filter-checkbox input[type="checkbox"] {
  margin: 0;
  cursor: pointer;
}

.filter-checkbox input[type="checkbox"]:checked + span {
  color: var(--color-accent);
}

.filter-select {
  padding: var(--spacing-sm) var(--spacing-md);
  border: var(--border-width) solid var(--color-border);
  background-color: var(--color-background);
  color: var(--color-text);
  font-size: var(--font-size-sm);
  box-shadow: var(--shadow-brutal);
  cursor: pointer;
}

.filter-select:focus {
  outline: none;
  border-color: var(--color-accent);
  box-shadow: var(--shadow-brutal-accent);
}

.filter-range {
  width: 100%;
  height: 6px;
  background-color: var(--color-background);
  border: var(--border-width-thin) solid var(--color-border);
  box-shadow: var(--shadow-brutal);
  cursor: pointer;
}

.filter-range::-webkit-slider-thumb {
  appearance: none;
  width: 20px;
  height: 20px;
  background-color: var(--color-accent);
  border: var(--border-width-thin) solid var(--color-border);
  box-shadow: var(--shadow-brutal);
  cursor: pointer;
}

.filter-range::-moz-range-thumb {
  width: 20px;
  height: 20px;
  background-color: var(--color-accent);
  border: var(--border-width-thin) solid var(--color-border);
  box-shadow: var(--shadow-brutal);
  cursor: pointer;
}

/* Search Results Info */
.search-results-info {
  border-top: var(--border-width) solid var(--color-border);
  padding-top: var(--spacing-md);
  margin-top: var(--spacing-md);
  background-color: var(--color-background);
  padding: var(--spacing-md);
  border: var(--border-width-thin) solid var(--color-border);
  box-shadow: var(--shadow-brutal);
}

.results-stats {
  display: flex;
  gap: var(--spacing-md);
  align-items: center;
  margin-bottom: var(--spacing-sm);
}

.results-count {
  font-weight: var(--font-weight-bold);
  color: var(--color-heading);
  font-size: var(--font-size-lg);
}

.search-type-badge {
  background-color: var(--color-accent);
  color: white;
  padding: var(--spacing-xs) var(--spacing-sm);
  border: var(--border-width-thin) solid var(--color-border);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-bold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  box-shadow: var(--shadow-brutal-accent);
}

.execution-time {
  background-color: var(--color-background-soft);
  color: var(--color-text-muted);
  padding: var(--spacing-xs) var(--spacing-sm);
  border: var(--border-width-thin) solid var(--color-border);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-bold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  box-shadow: var(--shadow-brutal);
  font-family: var(--font-family-mono);
}

.results-query {
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
  font-style: italic;
}

/* Table Styles */
.table-container {
  background-color: var(--color-background);
  border: var(--border-width) solid var(--color-border);
  box-shadow: var(--shadow-brutal);
  overflow-x: auto;
  margin: 0;
  width: 100%;
}

.contexts-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--font-size-sm);
}

.contexts-table th {
  background-color: var(--color-background-soft);
  border-bottom: var(--border-width) solid var(--color-border);
  padding: var(--spacing-md);
  text-align: left;
  font-weight: var(--font-weight-bold);
  color: var(--color-heading);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  position: sticky;
  top: 0;
  z-index: 10;
}

.contexts-table th.sortable {
  cursor: pointer;
  user-select: none;
  transition: var(--transition-fast);
}

.contexts-table th.sortable:hover {
  background-color: var(--color-accent);
  color: white;
  transform: translate(-1px, -1px);
  box-shadow: var(--shadow-brutal-accent);
}

.th-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-sm);
}

.sort-indicators {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.sort-icon {
  width: 12px;
  height: 12px;
  color: var(--color-text-muted);
  transition: var(--transition-fast);
}

.sort-icon.active {
  color: var(--color-accent);
}

.contexts-table th.sortable:hover .sort-icon {
  color: white;
}

.contexts-table th.sortable:hover .sort-icon.active {
  color: white;
}

.table-row {
  border-bottom: var(--border-width-thin) solid var(--color-border);
  transition: var(--transition-fast);
}

.table-row:hover {
  background-color: var(--color-background-soft);
  transform: translate(-1px, -1px);
  box-shadow: var(--shadow-brutal-hover);
}

.contexts-table td {
  padding: var(--spacing-md);
  vertical-align: top;
}

/* Cell Styles */
.title-cell {
  min-width: 200px;
}

.title-content {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.title-text {
  font-weight: var(--font-weight-bold);
  color: var(--color-heading);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.type-cell {
  min-width: 100px;
}

.type-badge {
  background-color: var(--color-accent);
  color: white;
  padding: var(--spacing-xs) var(--spacing-sm);
  border: var(--border-width-thin) solid var(--color-border);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-bold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  box-shadow: var(--shadow-brutal-accent);
  display: inline-block;
}

.content-cell {
  min-width: 300px;
  max-width: 400px;
}

.content-preview {
  color: var(--color-text);
  line-height: 1.4;
  white-space: pre-wrap;
  font-size: var(--font-size-sm);
}

.tags-cell {
  min-width: 150px;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-xs);
  align-items: center;
}

.tag {
  background-color: var(--color-accent);
  color: white;
  font-size: var(--font-size-xs);
  padding: var(--spacing-xs) var(--spacing-sm);
  border: var(--border-width-thin) solid var(--color-border);
  font-weight: var(--font-weight-bold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  box-shadow: var(--shadow-brutal-accent);
  display: inline-block;
}

.more-tags {
  background-color: var(--color-background-soft);
  color: var(--color-text-muted);
  font-size: var(--font-size-xs);
  padding: var(--spacing-xs) var(--spacing-sm);
  border: var(--border-width-thin) solid var(--color-border);
  font-weight: var(--font-weight-bold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  box-shadow: var(--shadow-brutal);
  display: inline-block;
}

.no-tags {
  color: var(--color-text-muted);
  font-style: italic;
  font-size: var(--font-size-xs);
}

.date-cell {
  min-width: 120px;
}

.date-content {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.project-cell {
  min-width: 120px;
}

.project-badge {
  background-color: var(--color-background-soft);
  color: var(--color-text);
  font-family: var(--font-family-mono);
  font-size: var(--font-size-xs);
  padding: var(--spacing-xs) var(--spacing-sm);
  border: var(--border-width-thin) solid var(--color-border);
  font-weight: var(--font-weight-bold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  box-shadow: var(--shadow-brutal);
  display: inline-block;
}

.no-project {
  color: var(--color-text-muted);
  font-style: italic;
  font-size: var(--font-size-xs);
}

.actions-cell {
  min-width: 120px;
  text-align: center;
}

.actions-group {
  display: flex;
  gap: var(--spacing-sm);
  justify-content: center;
  align-items: center;
}

.btn-edit {
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

.btn-edit:hover {
  background-color: var(--color-accent);
  color: white;
  transform: translate(-1px, -1px);
  box-shadow: 4px 4px 0px 0px var(--color-accent);
}

.btn-edit:hover svg {
  color: white;
  fill: white;
}

.btn-edit svg {
  width: 24px;
  height: 24px;
  color: var(--color-text);
  fill: currentColor;
}

.cell-icon {
  width: 16px;
  height: 16px;
  color: var(--color-accent);
  flex-shrink: 0;
}

/* Responsive Modal Design */
@media (max-width: 768px) {
  .modal-overlay {
    padding: var(--spacing-sm);
  }

  .modal {
    max-width: calc(100vw - var(--spacing-md));
    max-height: calc(100vh - var(--spacing-md));
  }

  .modal-header {
    padding: var(--spacing-md);
  }

  .modal-header h2 {
    font-size: var(--font-size-lg);
  }

  .context-form {
    padding: var(--spacing-md);
  }

  .form-actions {
    flex-direction: column-reverse;
    gap: var(--spacing-sm);
  }

  .btn {
    width: 100%;
    justify-content: center;
  }

  .contexts-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-md);
  }

  .search-container {
    margin-bottom: var(--spacing-lg);
    padding: var(--spacing-md);
  }

  .search-main {
    flex-direction: column;
    gap: var(--spacing-sm);
  }

  .search-input-wrapper {
    max-width: 100%;
  }

  .search-controls {
    flex-wrap: wrap;
    justify-content: center;
  }

  .filter-row {
    grid-template-columns: 1fr;
    gap: var(--spacing-md);
  }

  .filter-checkboxes {
    flex-direction: column;
    gap: var(--spacing-xs);
  }

  .filter-checkbox {
    justify-content: flex-start;
  }

  .table-container {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  .contexts-table {
    font-size: var(--font-size-xs);
  }

  .contexts-table th,
  .contexts-table td {
    padding: var(--spacing-md);
  }

  .content-cell {
    min-width: 200px;
    max-width: 250px;
  }

  .title-cell {
    min-width: 150px;
  }

  .content-layout {
    grid-template-columns: 1fr;
    gap: var(--spacing-md);
  }

  .form-row {
    grid-template-columns: 1fr;
    gap: var(--spacing-md);
  }

  .content-preview {
    margin-top: var(--spacing-sm);
  }

  .preview-content {
    max-height: 200px;
    padding: var(--spacing-sm);
    min-height: 150px;
  }

  .content-textarea {
    min-height: 100px;
    font-size: var(--font-size-xs);
  }

  .content-textarea:focus {
    min-height: 150px;
  }
}

@media (max-width: 480px) {
  .main-content {
    padding: var(--spacing-md);
  }

  .contexts-header h1 {
    font-size: var(--font-size-2xl);
  }

  .search-input {
    font-size: var(--font-size-sm);
    padding: var(--spacing-sm) var(--spacing-sm) var(--spacing-sm) 40px;
  }

  .search-icon {
    width: 16px;
    height: 16px;
    left: var(--spacing-sm);
  }

  .contexts-table {
    font-size: var(--font-size-xs);
  }

  .contexts-table th,
  .contexts-table td {
    padding: var(--spacing-sm);
  }

  .content-cell {
    min-width: 150px;
    max-width: 200px;
  }

  .title-cell {
    min-width: 120px;
  }

  .tags-cell {
    min-width: 100px;
  }

  .date-cell {
    min-width: 80px;
  }

  .project-cell {
    min-width: 80px;
  }

  .actions-cell {
    min-width: 80px;
  }

  .actions-group {
    flex-direction: column;
    gap: var(--spacing-xs);
  }

  .btn-edit,
  .btn-delete {
    width: 32px;
    height: 32px;
  }

  .btn-edit svg,
  .btn-delete svg {
    width: 20px;
    height: 20px;
  }

  .th-content {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-xs);
  }

  .sort-indicators {
    flex-direction: row;
    gap: var(--spacing-xs);
  }

  .content-textarea {
    min-height: 80px;
    font-size: var(--font-size-xs);
  }

  .content-textarea:focus {
    min-height: 120px;
  }

  .preview-content {
    max-height: 150px;
    padding: var(--spacing-xs);
  }

  .preview-header {
    padding: var(--spacing-xs) var(--spacing-sm);
  }

  .preview-label,
  .content-type-indicator {
    font-size: 10px;
  }

  .content-layout {
    grid-template-columns: 1fr;
    gap: var(--spacing-sm);
  }

  .form-row {
    grid-template-columns: 1fr;
    gap: var(--spacing-sm);
  }

  .preview-content {
    max-height: 120px;
    min-height: 100px;
  }
}

/* Large screen optimizations */
@media (min-width: 1200px) {
  .modal {
    max-width: 1200px;
  }

  .content-layout {
    grid-template-columns: 1fr 1fr;
    gap: var(--spacing-xl);
  }

  .content-textarea {
    min-height: 300px;
    font-size: var(--font-size-base);
  }

  .preview-content {
    min-height: 300px;
  }
}

/* Full screen optimizations */
@media (min-width: 1920px) {
  .contexts-header {
    margin-bottom: var(--spacing-md);
  }
  
  .search-container {
    margin-bottom: var(--spacing-md);
  }
  
  .contexts-table th,
  .contexts-table td {
    padding: var(--spacing-sm);
  }
  
  .contexts-table {
    font-size: var(--font-size-xs);
  }
  
  .content-cell {
    min-width: 400px;
    max-width: 500px;
  }
  
  .title-cell {
    min-width: 250px;
  }

  .modal {
    max-width: 1400px;
  }

  .content-layout {
    gap: var(--spacing-2xl);
  }

  .content-textarea {
    min-height: 400px;
  }

  .preview-content {
    min-height: 400px;
  }
}

/* Project Dropdown Styles */
.project-dropdown-container {
  position: relative;
}

.btn-clear-project {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  background: var(--color-background);
  border: var(--border-width-thin) solid var(--color-border);
  cursor: pointer;
  padding: var(--spacing-xs);
  transition: var(--transition-fast);
  box-shadow: var(--shadow-brutal);
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
}

.btn-clear-project:hover {
  background-color: var(--color-danger);
  color: white;
  transform: translateY(-50%) translate(-1px, -1px);
  box-shadow: 4px 4px 0px 0px var(--color-danger);
}

.btn-clear-project:hover svg {
  color: white;
  fill: white;
}

.btn-clear-project svg {
  width: 20px;
  height: 20px;
  color: var(--color-text);
  fill: currentColor;
}

.project-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background-color: var(--color-background);
  border: var(--border-width) solid var(--color-border);
  border-top: none;
  box-shadow: var(--shadow-brutal);
  max-height: 200px;
  overflow-y: auto;
  z-index: 1000;
}

.dropdown-empty {
  padding: var(--spacing-md);
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
  text-align: center;
  font-style: italic;
}

.dropdown-item {
  padding: var(--spacing-md);
  cursor: pointer;
  transition: var(--transition-fast);
  border-bottom: var(--border-width-thin) solid var(--color-border);
}

.dropdown-item:hover {
  background-color: var(--color-background-soft);
  transform: translate(-1px, -1px);
  box-shadow: var(--shadow-brutal-hover);
}

.dropdown-item:last-child {
  border-bottom: none;
}

.project-name {
  font-weight: var(--font-weight-bold);
  color: var(--color-text);
  font-size: var(--font-size-sm);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--spacing-xs);
}

.project-id {
  font-family: var(--font-family-mono);
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  background-color: var(--color-background-soft);
  padding: var(--spacing-xs) var(--spacing-sm);
  border: var(--border-width-thin) solid var(--color-border);
  display: inline-block;
  box-shadow: var(--shadow-brutal);
}
</style>
