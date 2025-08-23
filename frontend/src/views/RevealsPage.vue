<template>
  <SplitViewLayout
    :items="filteredEntities"
    :selected-item-id="selectedEntityId"
    :loading="loading"
    :enable-attribute-filter="true"
    :attribute-filters="activeFilters"
    list-title="Reveals"
    create-button-text="Add Reveal"
    empty-message="No reveals yet"
    @select-item="selectEntity"
    @create-item="startCreate"
  >
    <template #filter-content>
      <FilterPanel
        v-model="activeFilters"
        :enable-tabs="true"
        :available-tabs="revealFilterTabs"
        :characters="characters"
      />
    </template>
    <template #detail-content>
      <div v-if="loading" class="shared-loading">Loading reveals...</div>
      <div v-else-if="error" class="shared-error">{{ error }}</div>

      <EmptyState
        v-else-if="!selectedReveal && !showCreateForm"
        icon="🧠"
        title="No Reveal Selected"
        message="Select an influence reveal from the list to view details, or create a new one."
      />

      <div v-else-if="showCreateForm" class="shared-card">
        <div class="shared-form">
          <!-- Title -->
          <input
            v-model="createForm.title"
            placeholder="Reveal title"
            class="shared-input shared-input-name"
          />

          <!-- Character Selection -->
          <CharacterSelector
            v-model="createForm.character_ids"
            :characters="characters"
            :enable-filtering="true"
            label="Characters"
          />

          <!-- Level 1 Content (Always Required) -->
          <div class="shared-field shared-field-full-width">
            <label class="shared-field-label"
              >Level 1: Standard Content <span class="required">*</span></label
            >
            <BaseTextareaWithCharacterCounter
              v-model="createForm.level_1_content"
              placeholder="Enter standard content..."
              :max-characters="500"
            />
          </div>

          <!-- Level 1 Threshold -->
          <div class="threshold-section">
            <div class="threshold-slider">
              <label class="threshold-label">
                Standard Content:
                {{
                  getDCLabel(createForm.standard_threshold) || `DC ${createForm.standard_threshold}`
                }}
              </label>
              <input
                type="range"
                v-model.number="createForm.standard_threshold"
                :min="gameData.threshold_limits.min"
                :max="gameData.threshold_limits.max"
                :step="gameData.threshold_limits.step"
                class="slider"
              />
            </div>
          </div>

          <!-- Level 2 Toggle -->
          <div class="level-toggle">
            <label class="level-toggle-option">
              <input
                type="checkbox"
                v-model="createForm.enable_level_2"
                @change="handleLevel2Toggle"
              />
              <span>Add Level 2: Privileged Content</span>
            </label>
          </div>

          <!-- Level 2 Content -->
          <div v-if="createForm.enable_level_2" class="shared-field shared-field-full-width">
            <label class="shared-field-label">Level 2: Privileged Content</label>
            <BaseTextareaWithCharacterCounter
              v-model="createForm.level_2_content"
              placeholder="Enter privileged content (high influence required)..."
              :max-characters="500"
            />
          </div>

          <!-- Level 2 Threshold -->
          <div v-if="createForm.enable_level_2" class="threshold-section">
            <div class="threshold-slider">
              <label class="threshold-label">
                Privileged Content:
                {{
                  getDCLabel(createForm.privileged_threshold) ||
                  `DC ${createForm.privileged_threshold}`
                }}
              </label>
              <input
                type="range"
                v-model.number="createForm.privileged_threshold"
                :min="gameData.threshold_limits.min"
                :max="gameData.threshold_limits.max"
                :step="gameData.threshold_limits.step"
                class="slider"
              />
            </div>
          </div>

          <!-- Level 3 Content -->
          <div class="shared-field shared-field-full-width">
            <div class="level-toggle level-toggle-in-divider">
              <label class="level-toggle-option">
                <input
                  type="checkbox"
                  v-model="createForm.enable_level_3"
                  @change="handleLevel3Toggle"
                />
                <span>Add Level 3: Exclusive Content</span>
              </label>
            </div>

            <div v-if="createForm.enable_level_3">
              <label class="shared-field-label">Level 3: Exclusive Content</label>
              <BaseTextareaWithCharacterCounter
                v-model="createForm.level_3_content"
                placeholder="Enter exclusive content (maximum influence required)..."
                :max-characters="500"
              />
            </div>
          </div>

          <!-- Level 3 Threshold -->
          <div v-if="createForm.enable_level_3" class="threshold-section">
            <div class="threshold-slider">
              <label class="threshold-label">
                Exclusive Content:
                {{
                  getDCLabel(createForm.exclusive_threshold) ||
                  `DC ${createForm.exclusive_threshold}`
                }}
              </label>
              <input
                type="range"
                v-model.number="createForm.exclusive_threshold"
                :min="gameData.threshold_limits.min"
                :max="gameData.threshold_limits.max"
                :step="gameData.threshold_limits.step"
                class="slider"
              />
            </div>
          </div>

          <!-- Actions -->
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

      <RevealCard
        v-else-if="selectedReveal"
        :reveal="selectedReveal"
        :characters="characters"
        :current-influence-level="18"
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
  import RevealCard from '../components/RevealCard.vue'
  import BaseTextareaWithCharacterCounter from '../components/base/BaseTextareaWithCharacterCounter.vue'
  import CharacterSelector from '../components/entity/CharacterSelector.vue'
  import FilterPanel from '../components/filters/FilterPanel.vue'
  import { useEntityCRUD } from '../utils/useEntityCRUD.js'
  import { useRevealValidation } from '../composables/useRevealValidation.js'
  import { applyCharacterFilters } from '../utils/filterUtils.js'
  import apiService from '../services/api.js'
  import { useGameData } from '../composables/useGameData.js'
  import { getDCLabel } from '../utils/dcUtils.js'

  export default {
    name: 'RevealsPage',
    components: {
      SplitViewLayout,
      EmptyState,
      RevealCard,
      BaseTextareaWithCharacterCounter,
      CharacterSelector,
      FilterPanel,
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
        cancelCreate,
      } = useEntityCRUD('Reveal')

      const { gameData, loadGameData } = useGameData()
      const characters = ref([])

      // Reveal filter tabs configuration
      const revealFilterTabs = [{ id: 'characters', label: 'Characters' }]

      // Character filtering state
      const activeFilters = ref({
        characters: [], // Use 'characters' to match the tab id
        characterIds: [], // Keep for compatibility with applyCharacterFilters
        showUnassigned: false,
      })

      const createForm = reactive({
        title: '',
        character_ids: [],
        level_1_content: '',
        level_2_content: '',
        level_3_content: '',
        enable_level_2: false,
        enable_level_3: false,
        standard_threshold: 0, // Will be set from gameData
        privileged_threshold: 0, // Will be set from gameData
        exclusive_threshold: 0, // Will be set from gameData
      })

      const { isFormValid: isCreateFormValid } = useRevealValidation(createForm)

      const selectedReveal = computed(() => {
        return entities.value.find((n) => n.id === selectedEntityId.value) || null
      })

      const loadCharacters = async () => {
        try {
          characters.value = await apiService.getCharacters()
        } catch (err) {
          console.error('Error loading characters:', err)
        }
      }

      const resetCreateForm = () => {
        Object.assign(createForm, {
          title: '',
          character_ids: [],
          level_1_content: '',
          level_2_content: '',
          level_3_content: '',
          enable_level_2: false,
          enable_level_3: false,
          standard_threshold: gameData.value.default_thresholds.standard,
          privileged_threshold: gameData.value.default_thresholds.privileged,
          exclusive_threshold: gameData.value.default_thresholds.exclusive,
        })
      }

      const saveCreate = async () => {
        if (isCreateFormValid.value) {
          try {
            const revealData = {
              title: createForm.title.trim(),
              character_ids: createForm.character_ids.map((id) => parseInt(id)),
              level_1_content: createForm.level_1_content.trim(),
              level_2_content: createForm.enable_level_2 ? createForm.level_2_content.trim() : null,
              level_3_content: createForm.enable_level_3 ? createForm.level_3_content.trim() : null,
            }

            // Always include all thresholds since we always show sliders
            revealData.standard_threshold = createForm.standard_threshold
            revealData.privileged_threshold = createForm.enable_level_2
              ? createForm.privileged_threshold
              : null
            revealData.exclusive_threshold = createForm.enable_level_3
              ? createForm.exclusive_threshold
              : null

            await createEntity(revealData)
            resetCreateForm()
          } catch (err) {
            // Error handling is done in useEntityCRUD
          }
        }
      }

      const handleLevel2Toggle = () => {
        if (!createForm.enable_level_2) {
          createForm.level_2_content = ''
        }
      }

      const handleLevel3Toggle = () => {
        if (!createForm.enable_level_3) {
          createForm.level_3_content = ''
        }
      }

      const handleCancelCreate = () => {
        cancelCreate()
        resetCreateForm()
      }

      onMounted(async () => {
        await loadGameData()
        // Update form defaults after game data is loaded
        createForm.standard_threshold = gameData.value.default_thresholds.standard
        createForm.privileged_threshold = gameData.value.default_thresholds.privileged
        createForm.exclusive_threshold = gameData.value.default_thresholds.exclusive
        await loadEntities()
        await loadCharacters()
      })

      // Filtered entities based on character filters
      const filteredEntities = computed(() => {
        return applyCharacterFilters(entities.value, activeFilters.value)
      })

      const hasActiveCharacterFilters = computed(() => {
        return activeFilters.value.characterIds.length > 0 || activeFilters.value.showUnassigned
      })

      const clearCharacterFilters = () => {
        activeFilters.value.characterIds = []
        activeFilters.value.showUnassigned = false
      }

      return {
        gameData,
        entities,
        filteredEntities,
        activeFilters,
        revealFilterTabs,
        loading,
        error,
        selectedEntityId,
        showCreateForm,
        selectedReveal,
        characters,
        createForm,
        isCreateFormValid,
        hasActiveCharacterFilters,
        selectEntity,
        startCreate,
        updateEntity,
        deleteEntity,
        saveCreate,
        cancelCreate: handleCancelCreate,
        handleLevel2Toggle,
        handleLevel3Toggle,
        clearCharacterFilters,
        getDCLabel: (value) => getDCLabel(value, gameData.value?.difficulty_classes),
      }
    },
  }
</script>

<style scoped>
  .character-field {
    margin-bottom: 1.5rem;
  }

  .character-selection {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    max-height: 150px;
    overflow-y: auto;
    padding: 0.75rem;
    border: 2px solid #dee2e6;
    border-radius: 8px;
    background: #f8f9fa;
  }

  .character-checkbox {
    display: flex;
    align-items: center;
  }

  .character-option {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    transition: background-color 0.2s ease;
    width: 100%;
    font-size: 0.9rem;
  }

  .character-option:hover {
    background-color: #e9ecef;
  }

  .character-option input[type='checkbox'] {
    margin: 0;
    transform: scale(0.9);
  }

  .character-option span {
    font-weight: 500;
    color: #495057;
  }

  /* Level toggle styles */
  .level-toggle {
    margin-bottom: 1rem;
  }

  .level-toggle-option {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
    padding: 0.75rem;
    border: 2px solid #dee2e6;
    border-radius: 8px;
    background: #f8f9fa;
    transition: all 0.2s ease;
    font-size: 0.9rem;
    font-weight: 500;
    color: #495057;
  }

  .level-toggle-option:hover {
    border-color: #007bff;
    background: #e3f2fd;
  }

  .level-toggle-option input[type='checkbox'] {
    margin: 0;
    transform: scale(1.1);
  }

  /* Threshold section styles using shared design tokens */
  .threshold-section {
    margin-bottom: var(--spacing-xl);
  }

  .threshold-slider {
    margin-bottom: var(--spacing-lg);
  }

  .threshold-slider:last-child {
    margin-bottom: 0;
  }

  .threshold-label {
    display: block;
    margin-bottom: var(--spacing-sm);
    font-weight: var(--font-weight-medium);
    color: var(--text-secondary);
    font-size: var(--font-size-base);
  }

  .slider {
    width: 100%;
    height: 6px;
    border-radius: 3px;
    background: var(--border-default);
    outline: none;
    -webkit-appearance: none;
  }

  .slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 20px;
    height: 20px;
    border-radius: var(--radius-round);
    background: var(--primary-color);
    cursor: pointer;
  }

  .slider::-moz-range-thumb {
    width: 20px;
    height: 20px;
    border-radius: var(--radius-round);
    background: var(--primary-color);
    cursor: pointer;
    border: none;
  }

  .required {
    color: #dc3545;
    font-weight: bold;
  }

  /* Level 3 divider toggle styles */
  .level-toggle-in-divider {
    position: relative;
    margin: var(--spacing-xl) 0 var(--spacing-lg) 0;
  }

  .level-toggle-in-divider::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 0;
    right: 0;
    height: 1px;
    background: var(--border-default);
    z-index: 1;
  }

  .level-toggle-in-divider .level-toggle-option {
    position: relative;
    z-index: 2;
    background: var(--bg-white);
    margin: 0 auto;
    width: fit-content;
    padding: var(--spacing-sm) var(--spacing-lg);
  }

  /* Ensure text areas take full width */
  .shared-field-full-width :deep(.shared-word-counter-field) {
    width: 100% !important;
  }

  .shared-field-full-width :deep(.shared-textarea) {
    width: 100% !important;
    box-sizing: border-box;
    min-width: 100%;
  }
</style>
