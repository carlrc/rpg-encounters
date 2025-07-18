<template>
  <SplitViewLayout
    :items="entities"
    :selected-item-id="selectedEntityId"
    list-title="Trust Nuggets"
    create-button-text="Add Nugget"
    empty-message="No trust nuggets yet"
    @select-item="selectEntity"
    @create-item="startCreate"
  >
    <template #detail-content>
      <div v-if="loading" class="loading">Loading nuggets...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      
      <EmptyState
        v-else-if="!selectedNugget && !showCreateForm"
        icon="🧠"
        title="No Nugget Selected"
        message="Select a trust nugget from the list to view details, or create a new one."
      />
      
      <div v-else-if="showCreateForm" class="shared-card">
        <div class="shared-form">
          <!-- Character Selection -->
          <div class="character-field">
            <label class="shared-field-label">Character</label>
            <select v-model="createForm.character_id" class="shared-select">
              <option value="">Select character...</option>
              <option 
                v-for="character in characters" 
                :key="character.id" 
                :value="character.id"
              >
                {{ character.name }}
              </option>
            </select>
          </div>
          
          <!-- Trust Level Selection -->
          <div class="trust-level-field">
            <label class="shared-field-label">Trust Level</label>
            <div class="trust-level-options">
              <label 
                v-for="level in 3" 
                :key="level"
                class="trust-level-option"
                :class="{ active: createForm.layer === level }"
              >
                <input 
                  type="radio" 
                  :value="level" 
                  v-model="createForm.layer"
                />
                <div class="trust-level-info">
                  <div class="trust-level-name">Level {{ level }}: {{ getLevelName(level) }}</div>
                  <div class="trust-level-desc">{{ getLevelDescription(level) }}</div>
                </div>
              </label>
            </div>
          </div>
          
          <!-- Content -->
          <div class="content-field">
            <label class="shared-field-label">Secret Content</label>
            <BaseTextareaWithCharacterCounter
              v-model="createForm.content"
              placeholder="Enter the secret content for this trust level..."
              :max-characters="500"
            />
          </div>
          
          <!-- Actions -->
          <div class="shared-actions">
            <button @click="saveCreate" class="shared-btn shared-btn-success" :disabled="!isCreateFormValid">Save</button>
            <button @click="cancelCreate" class="shared-btn shared-btn-secondary">Cancel</button>
          </div>
        </div>
      </div>
      
      <NuggetCard
        v-else-if="selectedNugget"
        :nugget="selectedNugget"
        :characters="characters"
        :current-trust-level="0.6"
        @update="updateEntity"
        @delete="deleteEntity"
      />
    </template>
  </SplitViewLayout>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import SplitViewLayout from '../components/layout/SplitViewLayout.vue'
import EmptyState from '../components/ui/EmptyState.vue'
import NuggetCard from '../components/NuggetCard.vue'
import BaseTextareaWithCharacterCounter from '../components/base/BaseTextareaWithCharacterCounter.vue'
import { useEntityCRUD } from '../utils/useEntityCRUD.js'
import apiService from '../services/api.js'

export default {
  name: 'NuggetsPage',
  components: {
    SplitViewLayout,
    EmptyState,
    NuggetCard,
    BaseTextareaWithCharacterCounter
  },
  setup() {
    const {
      entities,
      loading,
      error,
      selectedEntityId,
      showCreateForm,
      loadEntities,
      createEntity,
      updateEntity,
      deleteEntity,
      selectEntity,
      startCreate,
      cancelCreate
    } = useEntityCRUD('Nugget')

    const characters = ref([])

    const createForm = reactive({
      character_id: '',
      layer: 1,
      content: ''
    })

    const isCreateFormValid = computed(() => {
      return createForm.character_id && 
             createForm.layer && 
             createForm.content.trim() && 
             createForm.content.length <= 500
    })

    const selectedNugget = computed(() => {
      return entities.value.find(n => n.id === selectedEntityId.value) || null
    })

    const getLevelName = (level) => {
      const names = {
        1: 'Public',
        2: 'Privileged', 
        3: 'Exclusive'
      }
      return names[level] || 'Unknown'
    }
    
    const getLevelDescription = (level) => {
      const descriptions = {
        1: 'Always accessible',
        2: 'High trust required',
        3: 'Maximum trust required'
      }
      return descriptions[level] || 'Unknown level'
    }

    const loadCharacters = async () => {
      try {
        characters.value = await apiService.getCharacters()
      } catch (err) {
        console.error('Error loading characters:', err)
      }
    }

    const resetCreateForm = () => {
      Object.assign(createForm, {
        character_id: '',
        layer: 1,
        content: ''
      })
    }

    const saveCreate = async () => {
      if (isCreateFormValid.value) {
        try {
          await createEntity({
            character_id: parseInt(createForm.character_id),
            layer: createForm.layer,
            content: createForm.content.trim()
          })
          resetCreateForm()
        } catch (err) {
          // Error handling is done in useEntityCRUD
        }
      }
    }

    const handleCancelCreate = () => {
      cancelCreate()
      resetCreateForm()
    }

    onMounted(async () => {
      await loadEntities()
      await loadCharacters()
    })

    return {
      entities,
      loading,
      error,
      selectedEntityId,
      showCreateForm,
      selectedNugget,
      characters,
      createForm,
      isCreateFormValid,
      selectEntity,
      startCreate,
      updateEntity,
      deleteEntity,
      getLevelName,
      getLevelDescription,
      saveCreate,
      cancelCreate: handleCancelCreate
    }
  }
}
</script>

<style scoped>
.loading {
  text-align: center;
  padding: 40px;
  color: #666;
  font-size: 1.1em;
}

.error {
  text-align: left;
  padding: 20px;
  color: #dc3545;
  font-size: 0.95em;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 8px;
  margin: 20px;
  white-space: pre-line;
  max-height: 400px;
  overflow-y: auto;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  line-height: 1.5;
}

.character-field,
.trust-level-field,
.content-field {
  margin-bottom: 1.5rem;
}

.trust-level-options {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.trust-level-option {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border: 2px solid #dee2e6;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.trust-level-option:hover {
  border-color: #007bff;
  background: #f8f9fa;
}

.trust-level-option.active {
  border-color: #007bff;
  background: #e3f2fd;
}

.trust-level-option input[type="radio"] {
  margin: 0;
}

.trust-level-info {
  flex: 1;
}

.trust-level-name {
  font-weight: 600;
  color: #495057;
  margin-bottom: 0.25rem;
}

.trust-level-desc {
  font-size: 0.875rem;
  color: #6c757d;
}

.trust-level-option.active .trust-level-name {
  color: #007bff;
}
</style>
