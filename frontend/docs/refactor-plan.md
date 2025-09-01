# Frontend Refactor Execution Plan (v3)

This document provides a detailed, step-by-step guide to refactor the frontend, aligning it with modern Vue 3 best practices. This plan is based on thorough analysis of the existing codebase.

---

## 1. Executive Summary

After analyzing the current codebase, I found:

**Current State:**

- Well-structured shared styles system already exists (`shared-styles.css`)
- Sophisticated composables for CRUD operations (`useEntityCRUD.js`)
- Class-based API service with good error handling
- Options API components that need conversion to `<script setup>`
- Basic ESLint setup that needs enhancement
- Missing Pinia for centralized state management

**Key Improvements:**

- Convert all components from Options API to `<script setup>`
- Replace composable-based state with Pinia stores
- Modernize API service architecture
- Enhance ESLint rules for consistency
- Consolidate and optimize style system
- Implement proper folder structure by feature

---

## 2. Foundational Setup

### 2.1. Install Pinia

```bash
npm install pinia
```

### 2.2. Update Main Entry Point

**File:** `src/main.js`

```javascript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './styles/index.css' // New consolidated stylesheet

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
```

### 2.3. Consolidate Style System

The current `shared-styles.css` is excellent but needs consolidation with `style.css`.

**New File:** `src/styles/tokens.css`

```css
:root {
  /* Extract and consolidate from existing shared-styles.css */
  --color-primary: #007bff;
  --color-primary-dark: #0056b3;
  --color-success: #28a745;
  --color-danger: #dc3545;
  --color-secondary: #6c757d;

  /* Keep existing spacing scale */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;

  /* Keep existing radius scale */
  --radius-2: 0.375rem;
  --radius-3: 0.5rem;

  --font-sans: ui-sans-serif, system-ui, sans-serif;
}
```

**New File:** `src/styles/index.css`

```css
@import './tokens.css';

/* Merge relevant parts from style.css and shared-styles.css */
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  min-width: 320px;
  min-height: 100vh;
  font-family: var(--font-sans);
}

#app {
  width: 100%;
  height: 100vh;
}

/* Import all shared component styles */
@import '../components/shared.css'; /* Move shared-styles.css content here */
```

---

## 3. State Management with Pinia

### 3.1. World State Store

**Replaces:** `src/services/worldState.js`

**New File:** `src/stores/world.js`

```javascript
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useWorldStore = defineStore('world', () => {
  const currentWorldId = ref(1)

  const setCurrentWorldId = (id) => {
    currentWorldId.value = id
  }

  return {
    currentWorldId,
    setCurrentWorldId,
  }
})
```

### 3.2. Game Data Store

**Replaces:** `src/composables/useGameData.js`

**New File:** `src/stores/gameData.js`

```javascript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getGameData } from '../services/gameDataService'

export const useGameDataStore = defineStore('gameData', () => {
  const data = ref(null)
  const isLoading = ref(false)
  const error = ref(null)

  const load = async () => {
    if (data.value) return data.value

    isLoading.value = true
    error.value = null

    try {
      data.value = await getGameData()
      return data.value
    } catch (err) {
      error.value = err
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return { data, isLoading, error, load }
})
```

### 3.3. Entity Stores (Characters, Players, etc.)

**Replaces:** `src/utils/useEntityCRUD.js`

**New File:** `src/features/characters/store.js`

```javascript
import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import apiService from '@/services/api'
import { useNotification } from '@/composables/useNotification'
import { useWorldStore } from '@/stores/world'

export const useCharacterStore = defineStore('characters', () => {
  const entities = ref([])
  const loading = ref(false)
  const error = ref('')
  const selectedEntityId = ref(null)
  const showCreateForm = ref(false)

  const worldStore = useWorldStore()
  const { showError, showSuccess } = useNotification()

  // Getters
  const selectedCharacter = computed(
    () => entities.value.find((c) => c.id === selectedEntityId.value) || null
  )

  // Actions (migrate from useEntityCRUD)
  const loadEntities = async () => {
    loading.value = true
    error.value = ''
    try {
      entities.value = await apiService.getCharacters()
    } catch (err) {
      const errorMessage = 'Failed to load characters. Please try again.'
      error.value = errorMessage
      showError(errorMessage)
      console.error('Error loading characters:', err)
    } finally {
      loading.value = false
    }
  }

  const createEntity = async (entityData) => {
    try {
      const newEntity = await apiService.createCharacter(entityData)
      entities.value.push(newEntity)
      selectedEntityId.value = newEntity.id
      showCreateForm.value = false
      showSuccess('Character created successfully!')
      return newEntity
    } catch (err) {
      const errorMessage = 'Failed to create character. Please check your input.'
      error.value = errorMessage
      showError(errorMessage)
      console.error('Error creating character:', err)
      throw err
    }
  }

  const updateEntity = async (entityId, entityData) => {
    try {
      const updatedEntity = await apiService.updateCharacter(entityId, entityData)
      const index = entities.value.findIndex((e) => e.id === entityId)
      if (index !== -1) {
        entities.value[index] = updatedEntity
      }
      showSuccess('Character updated successfully!')
      return updatedEntity
    } catch (err) {
      const errorMessage = 'Failed to update character. Please try again.'
      error.value = errorMessage
      showError(errorMessage)
      console.error('Error updating character:', err)
      throw err
    }
  }

  const deleteEntity = async (entityId) => {
    try {
      await apiService.deleteCharacter(entityId)
      entities.value = entities.value.filter((e) => e.id !== entityId)

      if (selectedEntityId.value === entityId) {
        if (entities.value.length > 0) {
          selectedEntityId.value = entities.value[0].id
        } else {
          selectedEntityId.value = null
        }
      }
      showSuccess('Character deleted successfully!')
    } catch (err) {
      const errorMessage = 'Failed to delete character. Please try again.'
      error.value = errorMessage
      showError(errorMessage)
      console.error('Error deleting character:', err)
      throw err
    }
  }

  const selectEntity = (entityId) => {
    selectedEntityId.value = entityId
    showCreateForm.value = false
  }

  const startCreate = () => {
    showCreateForm.value = true
    selectedEntityId.value = null
  }

  const cancelCreate = () => {
    showCreateForm.value = false
  }

  // Watch for world changes and reload data
  watch(
    () => worldStore.currentWorldId,
    () => {
      selectedEntityId.value = null
      showCreateForm.value = false
      loadEntities()
    }
  )

  return {
    entities,
    loading,
    error,
    selectedEntityId,
    selectedCharacter,
    showCreateForm,
    loadEntities,
    createEntity,
    updateEntity,
    deleteEntity,
    selectEntity,
    startCreate,
    cancelCreate,
  }
})
```

**Similar stores needed for:** Players, Memories, Reveals, Encounters

---

## 4. API Service Refactor

### 4.1. Create HTTP Client

**New File:** `src/services/http.js`

```javascript
import { useWorldStore } from '@/stores/world'

const request = async (method, url, body, { signal } = {}) => {
  const worldStore = useWorldStore()

  const res = await fetch(import.meta.env.VITE_API_URL || 'http://localhost:8000/api' + url, {
    method,
    signal,
    headers: {
      'content-type': 'application/json',
      'X-World-Id': worldStore.currentWorldId,
    },
    body: body ? JSON.stringify(body) : undefined,
  })

  if (!res.ok) {
    const error = new Error(`HTTP error! status: ${res.status}`)
    throw error
  }

  if (res.status === 204) return null
  return res.json()
}

export const http = {
  get: (url, opts) => request('GET', url, undefined, opts),
  post: (url, body, opts) => request('POST', url, body, opts),
  put: (url, body, opts) => request('PUT', url, body, opts),
  delete: (url, opts) => request('DELETE', url, undefined, opts),
}
```

### 4.2. Refactor API Service

**Update:** `src/services/api.js` - Convert from class to functional exports

```javascript
import { http } from './http.js'

// Player CRUD operations
export const getPlayers = () => http.get('/players')
export const getPlayer = (id) => http.get(`/players/${id}`)
export const createPlayer = (playerData) => http.post('/players', playerData)
export const updatePlayer = (id, playerData) => http.put(`/players/${id}`, playerData)
export const deletePlayer = (id) => http.delete(`/players/${id}`)

// Character CRUD operations
export const getCharacters = () => http.get('/characters')
export const getCharacter = (id) => http.get(`/characters/${id}`)
export const createCharacter = (characterData) => http.post('/characters', characterData)
export const updateCharacter = (id, characterData) => http.put(`/characters/${id}`, characterData)
export const deleteCharacter = (id) => http.delete(`/characters/${id}`)

// Reveal CRUD operations
export const getReveals = () => http.get('/reveals')
export const getReveal = (id) => http.get(`/reveals/${id}`)
export const createReveal = (revealData) => http.post('/reveals', revealData)
export const updateReveal = (id, revealData) => http.put(`/reveals/${id}`, revealData)
export const deleteReveal = (id) => http.delete(`/reveals/${id}`)

// Memory CRUD operations
export const getMemories = () => http.get('/memories')
export const getMemory = (id) => http.get(`/memories/${id}`)
export const createMemory = (memoryData) => http.post('/memories', memoryData)
export const updateMemory = (id, memoryData) => http.put(`/memories/${id}`, memoryData)
export const deleteMemory = (id) => http.delete(`/memories/${id}`)

// Encounter CRUD operations
export const getEncounters = () => http.get('/canvas')
export const getEncounter = (id) => http.get(`/encounters/${id}`)
export const createEncounter = (encounterData) => http.post('/encounters', encounterData)
export const updateEncounter = (id, encounterData) => http.put(`/encounters/${id}`, encounterData)
export const deleteEncounter = (id) => http.delete(`/encounters/${id}`)

// Other operations
export const getConversationData = (encounterId, playerId, characterId) =>
  http.get(`/encounters/${encounterId}/conversation/${playerId}/${characterId}`)
export const saveCanvas = (canvasData) => http.post('/canvas', canvasData)
export const getGameData = () => http.get('/game')
export const getWorlds = () => http.get('/worlds')
export const createWorld = () => http.post('/worlds')
export const deleteWorld = (worldId) => http.delete(`/worlds/${worldId}`)

// Voice operations
export const searchVoices = (searchTerm, pageToken = null) => {
  const params = new URLSearchParams({ search_term: searchTerm })
  if (pageToken) params.append('next_page_token', pageToken)
  return http.get(`/voices/search?${params}`)
}

export const getVoiceSample = async (voiceId) => {
  const worldStore = useWorldStore()
  const response = await fetch(
    `${import.meta.env.VITE_API_URL || 'http://localhost:8000/api'}/voices/${voiceId}/sample`,
    {
      headers: {
        'X-World-Id': worldStore.currentWorldId,
      },
    }
  )

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }

  return response
}
```

---

## 5. Component Refactoring

### 5.1. Convert CharactersPage to `<script setup>`

**File:** `src/views/CharactersPage.vue`

```vue
<script setup>
  import { reactive, computed, onMounted, watch } from 'vue'
  import { useRoute } from 'vue-router'
  import { storeToRefs } from 'pinia'
  import SplitViewLayout from '../components/layout/SplitViewLayout.vue'
  import EmptyState from '../components/ui/EmptyState.vue'
  import CharacterCard from '../components/CharacterCard.vue'
  import EntityAvatarSection from '../components/entity/EntityAvatarSection.vue'
  import ImportButton from '../components/ui/ImportButton.vue'
  import FilterPanel from '../components/filters/FilterPanel.vue'
  import BaseTextareaWithCharacterCounter from '../components/base/BaseTextareaWithCharacterCounter.vue'
  import { useCharacterStore } from '@/features/characters/store'
  import { useGameDataStore } from '@/stores/gameData'
  import { useFileImport } from '../utils/useFileImport.js'
  import { useFormValidation } from '../utils/useFormValidation.js'
  import { useDropdownOptions } from '../composables/useDropdownOptions.js'
  import { applyFilters } from '../utils/filterUtils.js'

  const route = useRoute()

  // Initialize stores
  const characterStore = useCharacterStore()
  const gameDataStore = useGameDataStore()

  // Reactive refs from stores
  const { entities, loading, error, selectedEntityId, selectedCharacter, showCreateForm } =
    storeToRefs(characterStore)

  const { data: gameData } = storeToRefs(gameDataStore)

  // Actions
  const {
    loadEntities,
    createEntity,
    updateEntity,
    deleteEntity,
    selectEntity,
    startCreate,
    cancelCreate,
  } = characterStore

  // File import composable
  const { importing, handleImportFile: handleFileImport } = useFileImport('Character')

  // Create form and validation (keep existing logic)
  const createForm = reactive({
    name: '',
    avatar: null,
    race: '',
    size: '',
    alignment: '',
    gender: '',
    profession: '',
    background: '',
    communication_style: '',
    motivation: '',
  })

  const { isFormValid: isCreateFormValid } = useFormValidation(createForm, 'CHARACTER')
  const { genders } = useDropdownOptions()

  // Character filter tabs configuration
  const characterFilterTabs = [
    { id: 'race', label: 'Race' },
    { id: 'alignment', label: 'Alignment' },
    { id: 'size', label: 'Size' },
    { id: 'gender', label: 'Gender' },
    { id: 'class', label: 'Class' },
  ]

  // Filter state management
  const activeFilters = ref({
    race: [],
    alignment: [],
    size: [],
    gender: [],
    class: [],
  })

  // Computed filtered entities
  const filteredEntities = computed(() => {
    return applyFilters(entities.value, activeFilters.value)
  })

  // Computed properties for dropdown options
  const races = computed(() => gameData.value?.races || [])
  const characterSizes = computed(() => gameData.value?.sizes?.character || [])
  const alignments = computed(() => gameData.value?.alignments || [])

  // Methods
  const resetCreateForm = () => {
    createForm.name = ''
    createForm.avatar = null
    createForm.race = ''
    createForm.size = ''
    createForm.alignment = ''
    createForm.gender = ''
    createForm.profession = ''
    createForm.background = ''
    createForm.communication_style = ''
    createForm.motivation = ''
  }

  const saveCreate = async () => {
    if (isCreateFormValid.value) {
      try {
        await createEntity({
          name: createForm.name.trim(),
          avatar: createForm.avatar,
          race: createForm.race,
          size: createForm.size,
          alignment: createForm.alignment,
          gender: createForm.gender,
          profession: createForm.profession.trim(),
          background: createForm.background.trim(),
          communication_style: createForm.communication_style.trim(),
          motivation: createForm.motivation.trim(),
          // Initialize empty influence profile fields
          race_preferences: {},
          class_preferences: {},
          gender_preferences: {},
          size_preferences: {},
        })
        resetCreateForm()
      } catch (err) {
        // Error handling done in store
      }
    }
  }

  const handleCancelCreate = () => {
    cancelCreate()
    resetCreateForm()
  }

  const handleImportFile = (event) => {
    handleFileImport(
      event,
      createEntity,
      (message) => {
        console.log('Import success:', message)
      },
      (errorMessage) => {
        error.value = errorMessage
      }
    )
  }

  // Lifecycle
  onMounted(async () => {
    await gameDataStore.load()
    await loadEntities()

    // Auto-select character if ID is provided
    const characterId = route.query.id
    if (characterId) {
      const id = parseInt(characterId, 10)
      if (entities.value.some((char) => char.id === id)) {
        selectEntity(id)
      }
    }
  })

  // Watch for changes in entities to handle auto-selection after data loads
  watch(entities, (newEntities) => {
    const characterId = route.query.id
    if (characterId && newEntities.length > 0 && !selectedEntityId.value) {
      const id = parseInt(characterId, 10)
      if (newEntities.some((char) => char.id === id)) {
        selectEntity(id)
      }
    }
  })
</script>

<template>
  <SplitViewLayout
    :items="filteredEntities"
    :selected-item-id="selectedEntityId"
    :loading="loading"
    :enable-attribute-filter="true"
    :attribute-filters="activeFilters"
    list-title="Characters"
    create-button-text="Add Character"
    empty-message="No characters yet"
    @select-item="selectEntity"
    @create-item="startCreate"
  >
    <template #filter-content>
      <FilterPanel
        v-model="activeFilters"
        :enable-tabs="true"
        :available-tabs="characterFilterTabs"
      />
    </template>
    <template #footer-actions>
      <ImportButton entity-type="Character" :importing="importing" @import="handleImportFile" />
    </template>

    <template #detail-content>
      <div v-if="loading" class="shared-loading">Loading characters...</div>
      <div v-else-if="error" class="shared-error">{{ error }}</div>

      <EmptyState
        v-else-if="!selectedCharacter && !showCreateForm"
        icon="👤"
        title="No Character Selected"
        message="Select a character from the list to view details, or create a new one."
      />

      <div v-else-if="showCreateForm" class="shared-card">
        <div class="shared-form">
          <!-- Avatar Upload -->
          <EntityAvatarSection v-model="createForm.avatar" :name="createForm.name" />

          <!-- Name -->
          <input
            v-model="createForm.name"
            placeholder="Character name"
            class="shared-input shared-input-name"
          />

          <!-- Two Column Layout for Create -->
          <div class="shared-field-columns">
            <!-- Left Column -->
            <div class="shared-field-column">
              <select v-model="createForm.race" class="shared-select">
                <option value="">Select Race</option>
                <option v-for="race in races" :key="race" :value="race">{{ race }}</option>
              </select>

              <select v-model="createForm.alignment" class="shared-select">
                <option value="">Select Alignment</option>
                <option v-for="alignment in alignments" :key="alignment" :value="alignment">
                  {{ alignment }}
                </option>
              </select>

              <BaseTextareaWithCharacterCounter
                v-model="createForm.background"
                :placeholder="`Character background (max ${gameData?.validation_limits?.character_background} characters)`"
                :max-characters="gameData?.validation_limits?.character_background"
              />
            </div>

            <!-- Right Column -->
            <div class="shared-field-column">
              <select v-model="createForm.size" class="shared-select">
                <option value="">Select Size</option>
                <option v-for="size in characterSizes" :key="size" :value="size">{{ size }}</option>
              </select>

              <input
                v-model="createForm.profession"
                placeholder="Profession"
                class="shared-input"
              />
            </div>
          </div>

          <!-- Gender Field (Full Width) -->
          <select v-model="createForm.gender" class="shared-select">
            <option value="">Select Gender</option>
            <option v-for="gender in genders" :key="gender" :value="gender">{{ gender }}</option>
          </select>

          <!-- Communication Style Field (Full Width) -->
          <BaseTextareaWithCharacterCounter
            v-model="createForm.communication_style"
            :placeholder="`Communication style (max ${gameData?.validation_limits?.character_communication} characters)`"
            :max-characters="gameData?.validation_limits?.character_communication"
          />

          <!-- Motivation Field (Full Width) -->
          <BaseTextareaWithCharacterCounter
            v-model="createForm.motivation"
            :placeholder="`Character motivation (max ${gameData?.validation_limits?.character_motivation} characters)`"
            :max-characters="gameData?.validation_limits?.character_motivation"
          />

          <div class="shared-actions">
            <button
              @click="saveCreate"
              class="shared-btn shared-btn-success"
              :disabled="!isCreateFormValid"
            >
              Save
            </button>
            <button @click="handleCancelCreate" class="shared-btn shared-btn-secondary">
              Cancel
            </button>
          </div>
        </div>
      </div>

      <CharacterCard
        v-else-if="selectedCharacter"
        :character="selectedCharacter"
        @update="updateEntity"
        @delete="deleteEntity"
      />
    </template>
  </SplitViewLayout>
</template>
```

### 5.2. Convert CharacterCard to `<script setup>`

**File:** `src/components/CharacterCard.vue`

```vue
<script setup>
  import { ref, reactive, computed, onMounted, onUnmounted, watch, watchEffect } from 'vue'
  import { storeToRefs } from 'pinia'
  import { useGameDataStore } from '@/stores/gameData'
  import { useFormValidation } from '../utils/useFormValidation.js'
  import { useDropdownOptions } from '../composables/useDropdownOptions.js'
  import { useAudioPlayer } from '../composables/useAudioPlayer.js'
  import { getInitials } from '../utils/avatarUtils.js'
  import AvatarUpload from './base/AvatarUpload.vue'
  import BaseTextareaWithCharacterCounter from './base/BaseTextareaWithCharacterCounter.vue'
  import BiasPreferenceRow from './BiasPreferenceRow.vue'
  import TraitsDisplay from './base/TraitsDisplay.vue'
  import VoiceSelector from './VoiceSelector.vue'
  import * as apiService from '../services/api.js'

  const props = defineProps({
    character: {
      type: Object,
      required: true,
      validator: (value) => {
        return (
          value &&
          typeof value.id !== 'undefined' &&
          typeof value.name === 'string' &&
          value.name.length > 0
        )
      },
    },
  })

  const emit = defineEmits(['update', 'delete'])

  // Store data
  const gameDataStore = useGameDataStore()
  const { data: gameData } = storeToRefs(gameDataStore)

  // Component state
  const isEditing = ref(false)
  const editForm = reactive({
    name: '',
    avatar: null,
    race: '',
    size: '',
    alignment: '',
    gender: '',
    profession: '',
    background: '',
    communication_style: '',
    communication_style_type: 'Custom',
    motivation: '',
    voice_id: '',
    voice_name: '',
    biases: {
      race_preferences: [],
      class_preferences: [],
      gender_preferences: [],
      size_preferences: [],
    },
  })

  // Composables
  const { isFormValid } = useFormValidation(editForm, 'CHARACTER')
  const { genders, getGenderEmoji } = useDropdownOptions()
  const { playStreamingResponse, isLoading: previewLoading } = useAudioPlayer()

  // Computed properties
  const races = computed(() => gameData.value?.races || [])
  const alignments = computed(() => gameData.value?.alignments || [])
  const sizes = computed(() => gameData.value?.sizes?.character || [])

  // Bias display functionality
  const displayBiases = ref({})

  // Methods (convert from existing methods)
  const startEdit = () => {
    // Copy character data to edit form
    Object.assign(editForm, {
      name: props.character.name || '',
      avatar: props.character.avatar || null,
      race: props.character.race || '',
      size: props.character.size || '',
      alignment: props.character.alignment || '',
      gender: props.character.gender || '',
      profession: props.character.profession || '',
      background: props.character.background || '',
      communication_style: props.character.communication_style || '',
      communication_style_type: props.character.communication_style_type || 'Custom',
      motivation: props.character.motivation || '',
      voice_id: props.character.voice_id || '',
      voice_name: props.character.voice_name || '',
    })

    loadInfluenceProfile()
    isEditing.value = true
  }

  const saveEdit = () => {
    if (isFormValid.value) {
      const updateData = {
        name: editForm.name.trim(),
        avatar: editForm.avatar,
        race: editForm.race,
        size: editForm.size,
        alignment: editForm.alignment,
        gender: editForm.gender,
        profession: editForm.profession.trim(),
        background: editForm.background.trim(),
        communication_style: editForm.communication_style.trim(),
        communication_style_type: editForm.communication_style_type,
        motivation: editForm.motivation.trim(),
        voice_id: editForm.voice_id || '',
        voice_name: editForm.voice_name || '',
        // Include bias profile fields
        race_preferences: convertBiasesToObject(editForm.biases.race_preferences),
        class_preferences: convertBiasesToObject(editForm.biases.class_preferences),
        gender_preferences: convertBiasesToObject(editForm.biases.gender_preferences),
        size_preferences: convertBiasesToObject(editForm.biases.size_preferences),
      }

      emit('update', props.character.id, updateData)
      isEditing.value = false
    }
  }

  const cancelEdit = () => {
    isEditing.value = false
  }

  const deleteCharacter = () => {
    if (confirm(`Are you sure you want to delete ${props.character.name}?`)) {
      emit('delete', props.character.id)
    }
  }

  const loadInfluenceProfile = () => {
    const character = props.character
    editForm.biases = {
      race_preferences: Object.entries(character.race_preferences || {}).map(([option, value]) => ({
        option,
        value,
      })),
      class_preferences: Object.entries(character.class_preferences || {}).map(
        ([option, value]) => ({ option, value })
      ),
      gender_preferences: Object.entries(character.gender_preferences || {}).map(
        ([option, value]) => ({ option, value })
      ),
      size_preferences: Object.entries(character.size_preferences || {}).map(([option, value]) => ({
        option,
        value,
      })),
    }
  }

  const convertBiasesToObject = (arr) => {
    const obj = {}
    arr.forEach(({ option, value }) => {
      if (option) {
        obj[option] = value
      }
    })
    return obj
  }

  const loadDisplayBiases = () => {
    const character = props.character
    const biases = {}

    if (character.race_preferences && Object.keys(character.race_preferences).length > 0) {
      biases.race_preferences = character.race_preferences
    }
    if (character.class_preferences && Object.keys(character.class_preferences).length > 0) {
      biases.class_preferences = character.class_preferences
    }
    if (character.gender_preferences && Object.keys(character.gender_preferences).length > 0) {
      biases.gender_preferences = character.gender_preferences
    }
    if (character.size_preferences && Object.keys(character.size_preferences).length > 0) {
      biases.size_preferences = character.size_preferences
    }

    displayBiases.value = biases
  }

  const playCharacterVoiceSample = async () => {
    if (!props.character.voice_id || previewLoading.value) return

    try {
      const response = await apiService.getVoiceSample(props.character.voice_id)
      await playStreamingResponse(response, `character-${props.character.id}`)
    } catch (err) {
      console.error('Failed to play character voice sample:', err)
    }
  }

  // Bias management methods
  const addBiasPreference = (category) => {
    editForm.biases[category].push({ option: '', value: 0 })
  }

  const updateBiasPreference = (category, index, option, value) => {
    if (editForm.biases[category][index]) {
      editForm.biases[category][index].option = option
      editForm.biases[category][index].value = value
    }
  }

  const removeBiasPreference = (category, index) => {
    editForm.biases[category].splice(index, 1)
  }

  // Lifecycle and watchers
  onMounted(() => {
    loadDisplayBiases()
  })

  // Use watchEffect for automatic cleanup and better performance
  const stopCharacterIdWatcher = watchEffect(() => {
    if (props.character.id) {
      loadDisplayBiases()
    }
  })

  // Watch for changes in character bias properties
  const stopBiasWatcher = watch(
    () => [
      props.character.race_preferences,
      props.character.class_preferences,
      props.character.gender_preferences,
      props.character.size_preferences,
    ],
    () => {
      loadDisplayBiases()
    },
    { deep: true }
  )

  // Clean up on unmount to prevent memory leaks
  onUnmounted(() => {
    stopCharacterIdWatcher()
    stopBiasWatcher()
  })

  // Bias display configuration
  const biasesCategoryNames = {
    race_preferences: 'Race',
    class_preferences: 'Class',
    gender_preferences: 'Gender',
    alignment_preferences: 'Alignment',
    size_preferences: 'Size',
  }

  const getBiasClass = (value) => {
    if (value > 0) return 'bias-positive'
    if (value < 0) return 'bias-negative'
    return 'bias-neutral'
  }
</script>

<template>
  <div class="shared-card">
    <div v-if="!isEditing" class="character-content">
      <!-- Display content - keep existing template structure -->
      <div class="shared-avatar-section">
        <div class="shared-avatar-container">
          <img
            v-if="character.avatar"
            :src="character.avatar"
            :alt="character.name"
            class="shared-avatar-image"
          />
          <div v-else class="shared-avatar-placeholder">
            <span class="shared-avatar-initials">{{ getInitials(character.name) }}</span>
          </div>
        </div>
      </div>

      <h3 class="shared-title">{{ getGenderEmoji(character.gender) }} {{ character.name }}</h3>

      <!-- Keep existing character fields display structure -->
      <!-- ... rest of display template ... -->

      <div class="shared-actions">
        <button @click="startEdit" class="shared-btn shared-btn-primary">Edit</button>
        <button @click="deleteCharacter" class="shared-btn shared-btn-danger">Delete</button>
      </div>
    </div>

    <div v-else class="shared-form">
      <!-- Edit form - keep existing edit form structure -->
      <!-- ... existing edit form template ... -->

      <div class="shared-actions">
        <button @click="saveEdit" class="shared-btn shared-btn-success" :disabled="!isFormValid">
          Save
        </button>
        <button @click="cancelEdit" class="shared-btn shared-btn-secondary">Cancel</button>
      </div>
    </div>
  </div>
</template>

<style module>
  .card {
    background-color: var(--color-surface);
    border: 1px solid var(--color-border);
    padding: var(--space-4);
    border-radius: var(--radius-3);
  }
</style>
```

### 5.3. Convert App.vue to `<script setup>`

**File:** `src/App.vue`

```vue
<script setup>
  import AppLayout from './components/layout/AppLayout.vue'
  import NotificationContainer from './components/ui/NotificationContainer.vue'
</script>

<template>
  <AppLayout>
    <router-view />
  </AppLayout>
  <NotificationContainer />
</template>
```

### 5.4. Convert AppLayout to `<script setup>`

**File:** `src/components/layout/AppLayout.vue`

```vue
<script setup>
  import { computed, ref } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import WorldTabs from '../WorldTabs.vue'

  const route = useRoute()
  const router = useRouter()
  const successMessage = ref('')

  // Get navigation routes from router configuration
  const navigationRoutes = computed(() => {
    return router
      .getRoutes()
      .filter((route) => route.name && route.path !== '/')
      .map((route) => ({
        path: route.path,
        name: route.name,
      }))
  })

  const pageTitle = computed(() => {
    return route.name || 'DnD AI'
  })

  const showSuccessMessage = (message) => {
    successMessage.value = message
    setTimeout(() => {
      successMessage.value = ''
    }, 1500)
  }

  const handleWorldChange = (worldId) => {
    // Emit event to trigger data refresh in current page
    window.dispatchEvent(new CustomEvent('world-changed', { detail: { worldId } }))
  }
</script>

<template>
  <!-- Keep existing template structure -->
</template>

<style scoped>
  /* Keep existing styles but convert to use CSS variables */
</style>
```

---

## 6. Routing Improvements

### 6.1. Add Path Alias Configuration

**Update:** `vite.config.js`

```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    host: true,
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
```

### 6.2. Implement Route-Level Code Splitting

**Update:** `src/router/index.js`

```javascript
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/players',
  },
  {
    path: '/players',
    name: 'Players',
    component: () => import('@/views/PlayersPage.vue'),
    meta: {
      title: 'Players',
      requiresAuth: false,
    },
  },
  {
    path: '/characters',
    name: 'Characters',
    component: () => import('@/views/CharactersPage.vue'),
    meta: {
      title: 'Characters',
      requiresAuth: false,
    },
  },
  {
    path: '/memories',
    name: 'Memories',
    component: () => import('@/views/MemoriesPage.vue'),
    meta: {
      title: 'Memories',
      requiresAuth: false,
    },
  },
  {
    path: '/reveals',
    name: 'Reveals',
    component: () => import('@/views/RevealsPage.vue'),
    meta: {
      title: 'Reveals',
      requiresAuth: false,
    },
  },
  {
    path: '/encounters',
    name: 'Encounters',
    component: () => import('@/views/EncountersPage.vue'),
    meta: {
      title: 'Encounters',
      requiresAuth: false,
    },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Global navigation guard for meta handling
router.beforeEach((to, from, next) => {
  // Update document title
  if (to.meta.title) {
    document.title = `${to.meta.title} - DnD AI`
  }

  next()
})

export default router
```

---

## 7. Create Shared Composables

### 7.1. Create useAsync Composable

**New File:** `src/composables/useAsync.js`

```javascript
import { ref } from 'vue'

export const useAsync = (asyncFunction, immediate = false) => {
  const pending = ref(false)
  const error = ref(null)
  const data = ref(null)

  const execute = async (...args) => {
    pending.value = true
    error.value = null

    try {
      const result = await asyncFunction(...args)
      data.value = result
      return result
    } catch (err) {
      error.value = err
      throw err
    } finally {
      pending.value = false
    }
  }

  if (immediate) {
    execute()
  }

  return {
    pending,
    error,
    data,
    execute,
  }
}
```

### 7.2. Create useEntityStore Composable (Generic)

**New File:** `src/composables/useEntityStore.js`

```javascript
import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { useNotification } from './useNotification'
import { useWorldStore } from '@/stores/world'

export const createEntityStore = (entityName, apiMethods) => {
  return defineStore(`${entityName.toLowerCase()}s`, () => {
    const entities = ref([])
    const loading = ref(false)
    const error = ref('')
    const selectedEntityId = ref(null)
    const showCreateForm = ref(false)

    const worldStore = useWorldStore()
    const { showError, showSuccess } = useNotification()

    // Getters
    const selectedEntity = computed(
      () => entities.value.find((e) => e.id === selectedEntityId.value) || null
    )

    // Actions
    const loadEntities = async () => {
      loading.value = true
      error.value = ''
      try {
        entities.value = await apiMethods.getAll()
      } catch (err) {
        const errorMessage = `Failed to load ${entityName.toLowerCase()}s. Please try again.`
        error.value = errorMessage
        showError(errorMessage)
        console.error(`Error loading ${entityName.toLowerCase()}s:`, err)
      } finally {
        loading.value = false
      }
    }

    const createEntity = async (entityData) => {
      try {
        const newEntity = await apiMethods.create(entityData)
        entities.value.push(newEntity)
        selectedEntityId.value = newEntity.id
        showCreateForm.value = false
        showSuccess(`${entityName} created successfully!`)
        return newEntity
      } catch (err) {
        const errorMessage = `Failed to create ${entityName.toLowerCase()}. Please check your input.`
        error.value = errorMessage
        showError(errorMessage)
        console.error(`Error creating ${entityName.toLowerCase()}:`, err)
        throw err
      }
    }

    const updateEntity = async (entityId, entityData) => {
      try {
        const updatedEntity = await apiMethods.update(entityId, entityData)
        const index = entities.value.findIndex((e) => e.id === entityId)
        if (index !== -1) {
          entities.value[index] = updatedEntity
        }
        showSuccess(`${entityName} updated successfully!`)
        return updatedEntity
      } catch (err) {
        const errorMessage = `Failed to update ${entityName.toLowerCase()}. Please try again.`
        error.value = errorMessage
        showError(errorMessage)
        console.error(`Error updating ${entityName.toLowerCase()}:`, err)
        throw err
      }
    }

    const deleteEntity = async (entityId) => {
      try {
        await apiMethods.delete(entityId)
        entities.value = entities.value.filter((e) => e.id !== entityId)

        if (selectedEntityId.value === entityId) {
          if (entities.value.length > 0) {
            selectedEntityId.value = entities.value[0].id
          } else {
            selectedEntityId.value = null
          }
        }
        showSuccess(`${entityName} deleted successfully!`)
      } catch (err) {
        const errorMessage = `Failed to delete ${entityName.toLowerCase()}. Please try again.`
        error.value = errorMessage
        showError(errorMessage)
        console.error(`Error deleting ${entityName.toLowerCase()}:`, err)
        throw err
      }
    }

    const selectEntity = (entityId) => {
      selectedEntityId.value = entityId
      showCreateForm.value = false
    }

    const startCreate = () => {
      showCreateForm.value = true
      selectedEntityId.value = null
    }

    const cancelCreate = () => {
      showCreateForm.value = false
    }

    // Watch for world changes and reload data
    watch(
      () => worldStore.currentWorldId,
      () => {
        selectedEntityId.value = null
        showCreateForm.value = false
        loadEntities()
      }
    )

    return {
      entities,
      loading,
      error,
      selectedEntityId,
      selectedEntity,
      showCreateForm,
      loadEntities,
      createEntity,
      updateEntity,
      deleteEntity,
      selectEntity,
      startCreate,
      cancelCreate,
    }
  })
}
```

---

## 8. Linting and Formatting

### 8.1. Enhanced ESLint Configuration

**Update:** `.eslintrc.js`

```javascript
module.exports = {
  root: true,
  env: {
    node: true,
    browser: true,
    es2022: true,
  },
  extends: ['eslint:recommended', 'plugin:vue/vue3-recommended', '@vue/prettier'],
  parserOptions: {
    ecmaVersion: 2022,
    sourceType: 'module',
  },
  rules: {
    // Enforce modern JS practices as per refactor.md
    'func-style': ['error', 'expression'],
    'no-var': 'error',
    'prefer-const': 'error',
    'prefer-arrow-callback': 'error',
    'arrow-spacing': 'error',
    'no-unused-vars': [
      'error',
      {
        argsIgnorePattern: '^_',
        varsIgnorePattern: '^_',
      },
    ],

    // Vue-specific rules
    'vue/no-mutating-props': 'error',
    'vue/script-setup-uses-vars': 'error',
    'vue/component-name-in-template-casing': ['error', 'PascalCase'],
    'vue/define-props-declaration': ['error', 'type-based'],
    'vue/define-emits-declaration': ['error', 'type-based'],
    'vue/prefer-define-options': 'error',
    'vue/block-order': [
      'error',
      {
        order: ['script', 'template', 'style'],
      },
    ],

    // Import organization
    'import/order': [
      'error',
      {
        groups: ['builtin', 'external', 'internal', 'parent', 'sibling', 'index'],
        'newlines-between': 'never',
      },
    ],
  },
}
```

### 8.2. Prettier Configuration

**New File:** `.prettierrc`

```json
{
  "semi": false,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 100,
  "bracketSpacing": true,
  "arrowParens": "avoid",
  "endOfLine": "lf",
  "vueIndentScriptAndStyle": true
}
```

### 8.3. Add Package.json Scripts

**Update:** `package.json`

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "lint": "eslint src --ext .vue,.js,.ts --fix",
    "format": "prettier --write src/**/*.{vue,js,ts,css,scss,json,md}",
    "lint-staged": "lint-staged"
  },
  "lint-staged": {
    "*.{vue,js,ts}": ["eslint --fix", "prettier --write"],
    "*.{css,scss,json,md}": ["prettier --write"]
  }
}
```

---

## 9. Final Review and Cleanup

### 9.1. Post-Refactor Checklist

- [ ] All components converted to `<script setup>`
- [ ] All functions declared as `const fn = (args) => {}`
- [ ] No `var` declarations, only `const` or `let`
- [ ] Arrow functions used throughout
- [ ] Named exports preferred over default exports
- [ ] No direct HTTP calls in components (moved to stores)
- [ ] All props and emits explicitly defined with `defineProps` and `defineEmits`
- [ ] No duplicate styles (consolidated into shared system)
- [ ] All routes use lazy loading
- [ ] Shared tokens used instead of magic values
- [ ] No dead code or TODO comments
- [ ] All files properly organized by feature
- [ ] Path aliases (`@`) working correctly
- [ ] ESLint rules passing
- [ ] Prettier formatting applied

### 9.2. Migration Strategy

**Phase 1: Foundation (Week 1)**

1. Install Pinia and update main.js
2. Create style consolidation
3. Set up new folder structure
4. Configure ESLint and Prettier

**Phase 2: State Management (Week 2)**

1. Create world and gameData stores
2. Migrate one entity store (Characters)
3. Test the pattern thoroughly
4. Apply pattern to remaining entities

**Phase 3: Component Conversion (Week 2-3)**

1. Convert App.vue and AppLayout.vue
2. Convert one page component (CharactersPage)
3. Convert one feature component (CharacterCard)
4. Apply pattern to remaining components

**Phase 4: API and Routing (Week 3)**

1. Refactor API service
2. Update router configuration
3. Add shared composables
4. Test all functionality

**Phase 5: Polish and Testing (Week 4)**

1. Run full ESLint and Prettier passes
2. Test all features end-to-end
3. Performance optimization
4. Final cleanup and documentation

### 9.3. Testing Strategy

- **Unit Tests**: Test all new Pinia stores
- **Component Tests**: Test converted components with new store integration
- **Integration Tests**: Test full user flows with new architecture
- **E2E Tests**: Verify no regression in user experience

---

## 10. Benefits After Refactor

**Performance:**

- Lazy-loaded routes reduce initial bundle size
- Better tree-shaking with named exports
- Optimized reactivity with Pinia

**Developer Experience:**

- Consistent code style with ESLint/Prettier
- Type safety with proper prop definitions
- Better IDE support with `<script setup>`

**Maintainability:**

- Clear separation of concerns
- Centralized state management
- Consistent architectural patterns
- Easier to onboard new developers

**Scalability:**

- Feature-based organization
- Reusable composables
- Modular store architecture
- Consistent component patterns
