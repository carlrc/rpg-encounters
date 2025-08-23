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
                :placeholder="`Character background (max ${gameData.validation_limits.character_background} characters)`"
                :max-characters="gameData.validation_limits.character_background"
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
            :placeholder="`Communication style (max ${gameData.validation_limits.character_communication} characters)`"
            :max-characters="gameData.validation_limits.character_communication"
          />

          <!-- Motivation Field (Full Width) -->
          <BaseTextareaWithCharacterCounter
            v-model="createForm.motivation"
            :placeholder="`Character motivation (max ${gameData.validation_limits.character_motivation} characters)`"
            :max-characters="gameData.validation_limits.character_motivation"
          />

          <div class="shared-actions">
            <button
              @click="saveCreate"
              class="shared-btn shared-btn-success"
              :disabled="!isCreateFormValid"
            >
              Save
            </button>
            <button @click="cancelCreate" class="shared-btn shared-btn-secondary">Cancel</button>
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

<script>
  import { ref, reactive, computed, onMounted, watch } from 'vue'
  import { useRoute } from 'vue-router'
  import SplitViewLayout from '../components/layout/SplitViewLayout.vue'
  import EmptyState from '../components/ui/EmptyState.vue'
  import CharacterCard from '../components/CharacterCard.vue'
  import EntityAvatarSection from '../components/entity/EntityAvatarSection.vue'
  import ImportButton from '../components/ui/ImportButton.vue'
  import FilterPanel from '../components/filters/FilterPanel.vue'
  import { useEntityCRUD } from '../utils/useEntityCRUD.js'
  import { useFileImport } from '../utils/useFileImport.js'
  import { useFormValidation } from '../utils/useFormValidation.js'
  import { useDropdownOptions } from '../composables/useDropdownOptions.js'
  import { useGameData } from '../composables/useGameData.js'
  import { applyFilters, createEmptyFilters } from '../utils/filterUtils.js'
  import BaseTextareaWithCharacterCounter from '../components/base/BaseTextareaWithCharacterCounter.vue'

  export default {
    name: 'CharactersPage',
    components: {
      SplitViewLayout,
      EmptyState,
      CharacterCard,
      EntityAvatarSection,
      ImportButton,
      FilterPanel,
      BaseTextareaWithCharacterCounter,
    },
    setup() {
      const route = useRoute()

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
        cancelCreate,
      } = useEntityCRUD('Character')

      const { importing, handleImportFile: handleFileImport } = useFileImport('Character')

      const { gameData, loadGameData } = useGameData()

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

      // Filter state management (tabbed filtering - search is handled by SplitViewLayout)
      const activeFilters = ref({
        race: [],
        alignment: [],
        size: [],
        gender: [],
        class: [],
      })

      // Computed filtered entities (only apply FilterBar filters, search is handled by SplitViewLayout)
      const filteredEntities = computed(() => {
        return applyFilters(entities.value, activeFilters.value)
      })

      const selectedCharacter = computed(() => {
        return entities.value.find((c) => c.id === selectedEntityId.value) || null
      })

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
              appearance_keywords: [],
              storytelling_keywords: [],
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

      const handleImportFile = (event) => {
        handleFileImport(
          event,
          createEntity,
          (message) => {
            // Success message - could emit to parent or use toast
            console.log('Import success:', message)
          },
          (errorMessage) => {
            error.value = errorMessage
          }
        )
      }

      onMounted(async () => {
        await loadGameData()
        await loadEntities()

        // Auto-select character if ID is provided in query params
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

      return {
        gameData,
        entities,
        filteredEntities,
        activeFilters,
        characterFilterTabs,
        loading,
        error,
        selectedEntityId,
        showCreateForm,
        selectedCharacter,
        createForm,
        importing,
        races: computed(() => gameData.value.races),
        characterSizes: computed(() => gameData.value.sizes.character),
        alignments: computed(() => gameData.value.alignments),
        genders,
        isCreateFormValid,
        selectEntity,
        startCreate,
        updateEntity,
        deleteEntity,
        saveCreate,
        cancelCreate: handleCancelCreate,
        handleImportFile,
      }
    },
  }
</script>

<style scoped>
  .import-characters-btn {
    width: 100%;
    padding: 10px 16px;
    background: linear-gradient(135deg, #007bff, #0056b3);
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.85em;
    font-weight: 600;
    transition: all 0.2s ease;
    box-shadow: 0 2px 4px rgba(0, 123, 255, 0.3);
    margin-top: 8px;
  }

  .import-characters-btn:hover:not(:disabled) {
    background: linear-gradient(135deg, #0056b3, #004085);
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 123, 255, 0.4);
  }

  .import-characters-btn:disabled {
    background: #6c757d;
    cursor: not-allowed;
    opacity: 0.6;
    transform: none;
    box-shadow: none;
  }
</style>
