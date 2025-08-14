<template>
  <SplitViewLayout
    :items="entities"
    :selected-item-id="selectedEntityId"
    list-title="Players"
    create-button-text="Add Player"
    empty-message="No players yet"
    @select-item="selectEntity"
    @create-item="startCreate"
  >
    <template #footer-actions>
      <ImportButton entity-type="Player" :importing="importing" @import="handleImportFile" />
    </template>

    <template #detail-content>
      <div v-if="loading" class="shared-loading">Loading players...</div>
      <div v-else-if="error" class="shared-error">{{ error }}</div>

      <EmptyState
        v-else-if="!selectedPlayer && !showCreateForm"
        icon="👤"
        title="No Player Selected"
        message="Select a player from the list to view details, or create a new one."
      />

      <div v-else-if="showCreateForm" class="shared-card">
        <div class="shared-form">
          <!-- Avatar Upload -->
          <EntityAvatarSection v-model="createForm.avatar" :name="createForm.name" />

          <!-- Name -->
          <input
            v-model="createForm.name"
            placeholder="Player name"
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

              <select v-model="createForm.class_name" class="shared-select">
                <option value="">Select Class</option>
                <option v-for="playerClass in classes" :key="playerClass" :value="playerClass">
                  {{ playerClass }}
                </option>
              </select>

              <div class="shared-word-counter-field">
                <textarea
                  v-model="createForm.appearance"
                  placeholder="Player appearance (max 40 words)"
                  class="shared-textarea"
                  @input="updateCreateWordCount"
                ></textarea>
                <div class="shared-word-counter" :class="{ 'over-limit': createWordCount > 40 }">
                  {{ createWordCount }}/40 words
                </div>
              </div>
            </div>

            <!-- Right Column -->
            <div class="shared-field-column">
              <select v-model="createForm.size" class="shared-select">
                <option value="">Select Size</option>
                <option v-for="size in sizes" :key="size" :value="size">{{ size }}</option>
              </select>

              <select v-model="createForm.alignment" class="shared-select">
                <option value="">Select Alignment</option>
                <option v-for="alignment in alignments" :key="alignment" :value="alignment">
                  {{ alignment }}
                </option>
              </select>
            </div>
          </div>

          <!-- Gender Field (Full Width) -->
          <select v-model="createForm.gender" class="shared-select">
            <option value="">Select Gender</option>
            <option v-for="gender in genders" :key="gender" :value="gender">{{ gender }}</option>
          </select>

          <!-- Reopen the field columns div for tags -->
          <div class="shared-field-columns"></div>

          <!-- Tags Section -->
          <div class="shared-tags-field">
            <div class="shared-tags-input-container">
              <input
                v-model="newCreateTagInput"
                placeholder="Add tag"
                class="shared-input shared-tag-input"
                @keyup.enter="addCreateTag"
              />
              <button @click="addCreateTag" class="shared-btn shared-btn-success" type="button">
                Add
              </button>
            </div>
            <div class="shared-tags-edit-display">
              <span
                v-for="(tag, index) in createForm.tags"
                :key="index"
                class="shared-tag-bubble editable"
              >
                {{ tag }}
                <button @click="removeCreateTag(index)" class="shared-tag-remove-btn" type="button">
                  ×
                </button>
              </span>
            </div>
          </div>

          <!-- Abilities Section -->
          <div class="abilities-skills-section">
            <h4 class="section-title">Abilities</h4>
            <div class="threshold-slider">
              <label class="threshold-label">Charisma: {{ createForm.abilities.Charisma }}</label>
              <input
                type="range"
                v-model.number="createForm.abilities.Charisma"
                min="0"
                max="30"
                step="1"
                class="slider"
              />
            </div>
          </div>

          <!-- Skills Section -->
          <div class="abilities-skills-section">
            <h4 class="section-title">Skills</h4>
            <div class="threshold-slider">
              <label class="threshold-label">Deception: {{ createForm.skills.Deception }}</label>
              <input
                type="range"
                v-model.number="createForm.skills.Deception"
                min="-5"
                max="25"
                step="1"
                class="slider"
              />
            </div>
            <div class="threshold-slider">
              <label class="threshold-label"
                >Intimidation: {{ createForm.skills.Intimidation }}</label
              >
              <input
                type="range"
                v-model.number="createForm.skills.Intimidation"
                min="-5"
                max="25"
                step="1"
                class="slider"
              />
            </div>
            <div class="threshold-slider">
              <label class="threshold-label"
                >Performance: {{ createForm.skills.Performance }}</label
              >
              <input
                type="range"
                v-model.number="createForm.skills.Performance"
                min="-5"
                max="25"
                step="1"
                class="slider"
              />
            </div>
            <div class="threshold-slider">
              <label class="threshold-label">Persuasion: {{ createForm.skills.Persuasion }}</label>
              <input
                type="range"
                v-model.number="createForm.skills.Persuasion"
                min="-5"
                max="25"
                step="1"
                class="slider"
              />
            </div>
          </div>

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

      <PlayerCard
        v-else-if="selectedPlayer"
        :player="selectedPlayer"
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
  import PlayerCard from '../components/PlayerCard.vue'
  import EntityAvatarSection from '../components/entity/EntityAvatarSection.vue'
  import ImportButton from '../components/ui/ImportButton.vue'
  import { useEntityCRUD } from '../utils/useEntityCRUD.js'
  import { useFileImport } from '../utils/useFileImport.js'
  import { useFormValidation } from '../utils/useFormValidation.js'
  import { useDropdownOptions } from '../composables/useDropdownOptions.js'
  import { useGameData } from '../composables/useGameData.js'

  export default {
    name: 'PlayersPage',
    components: {
      SplitViewLayout,
      EmptyState,
      PlayerCard,
      EntityAvatarSection,
      ImportButton,
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
      } = useEntityCRUD('Player')

      const { importing, handleImportFile: handleFileImport } = useFileImport('Player')

      const { gameData, loadGameData } = useGameData()

      const createForm = reactive({
        name: '',
        avatar: null,
        appearance: '',
        race: '',
        class_name: '',
        size: '',
        alignment: '',
        gender: '',
        tags: [],
        abilities: {
          Charisma: 0,
        },
        skills: {
          Deception: 0,
          Intimidation: 0,
          Performance: 0,
          Persuasion: 0,
        },
      })

      const newCreateTagInput = ref('')
      const createWordCount = ref(0)

      const { isFormValid: isCreateFormValid } = useFormValidation(createForm, 'PLAYER')

      const { genders } = useDropdownOptions()

      const selectedPlayer = computed(() => {
        return entities.value.find((p) => p.id === selectedEntityId.value) || null
      })

      const updateCreateWordCount = () => {
        createWordCount.value = createForm.appearance.trim()
          ? createForm.appearance.trim().split(/\s+/).length
          : 0
      }

      const convertToKebabCase = (text) => {
        const kebab = text.toLowerCase().replace(/\s+/g, '-').replace(/_/g, '-')
        return kebab.startsWith('#') ? kebab : `#${kebab}`
      }

      const addCreateTag = () => {
        if (newCreateTagInput.value.trim()) {
          const formattedTag = convertToKebabCase(newCreateTagInput.value.trim())
          if (!createForm.tags.includes(formattedTag)) {
            createForm.tags.push(formattedTag)
          }
          newCreateTagInput.value = ''
        }
      }

      const removeCreateTag = (index) => {
        createForm.tags.splice(index, 1)
      }

      const resetCreateForm = () => {
        createForm.name = ''
        createForm.avatar = null
        createForm.appearance = ''
        createForm.race = ''
        createForm.class_name = ''
        createForm.size = ''
        createForm.alignment = ''
        createForm.gender = ''
        createForm.tags = []
        createForm.abilities = {
          Charisma: 0,
        }
        createForm.skills = {
          Deception: 0,
          Intimidation: 0,
          Performance: 0,
          Persuasion: 0,
        }
        newCreateTagInput.value = ''
        createWordCount.value = 0
      }

      const saveCreate = async () => {
        if (isCreateFormValid.value) {
          try {
            await createEntity({
              name: createForm.name.trim(),
              avatar: createForm.avatar,
              appearance: createForm.appearance.trim(),
              race: createForm.race,
              class_name: createForm.class_name,
              size: createForm.size,
              alignment: createForm.alignment,
              gender: createForm.gender,
              tags: createForm.tags,
              abilities: createForm.abilities,
              skills: createForm.skills,
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
        loadEntities()
      })

      return {
        gameData,
        entities,
        loading,
        error,
        selectedEntityId,
        showCreateForm,
        selectedPlayer,
        createForm,
        newCreateTagInput,
        createWordCount,
        importing,
        races: computed(() => gameData.value.races),
        classes: computed(() => gameData.value.classes),
        genders,
        sizes: computed(() => gameData.value.sizes.player),
        alignments: computed(() => gameData.value.alignments),
        isCreateFormValid,
        selectEntity,
        startCreate,
        updateEntity,
        deleteEntity,
        updateCreateWordCount,
        addCreateTag,
        removeCreateTag,
        saveCreate,
        cancelCreate: handleCancelCreate,
        handleImportFile,
      }
    },
  }
</script>

<style scoped>
  /* No custom styles needed - everything comes from shared-styles.css */

  .abilities-skills-section {
    margin-bottom: var(--spacing-lg);
    padding-top: var(--spacing-lg);
    border-top: 2px solid var(--border-default);
  }

  .section-title {
    margin: 0 0 var(--spacing-lg) 0;
    color: var(--text-primary);
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-semibold);
    text-align: center;
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
    text-align: center;
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
</style>
