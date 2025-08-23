<template>
  <div class="character-field">
    <label class="shared-field-label">{{ label }}</label>
    <div class="character-selection">
      <!-- ALL option -->
      <div v-if="showAllOption" class="character-checkbox all-option">
        <label class="character-option">
          <input
            type="checkbox"
            :checked="isAllSelected"
            :indeterminate="isIndeterminate"
            @change="toggleAll"
            ref="allCheckbox"
          />
          <span>ALL - Select all characters</span>
        </label>
      </div>

      <!-- No Characters option -->
      <div v-if="showNoCharactersOption" class="character-checkbox all-option">
        <label class="character-option">
          <input
            type="checkbox"
            :value="'no-characters'"
            :checked="currentShowUnassigned"
            @change="toggleNoCharacters"
          />
          <span>NONE - Select items with no assignments</span>
        </label>
      </div>

      <!-- Separator -->
      <div v-if="showAllOption || showNoCharactersOption" class="separator"></div>

      <!-- Individual characters -->
      <div v-for="character in characters" :key="character.id" class="character-checkbox">
        <label class="character-option">
          <input
            type="checkbox"
            :value="character.id"
            :checked="currentCharacterIds.includes(character.id)"
            @change="toggleCharacter(character.id)"
          />
          <span>{{ character.name }}</span>
        </label>
      </div>
    </div>
  </div>
</template>

<script>
  import { ref, computed, watchEffect } from 'vue'

  export default {
    name: 'CharacterSelector',
    props: {
      modelValue: {
        type: Array,
        default: () => [],
      },
      characterIds: {
        type: Array,
        default: () => [],
      },
      showUnassigned: {
        type: Boolean,
        default: false,
      },
      characters: {
        type: Array,
        default: () => [],
      },
      label: {
        type: String,
        default: 'Characters',
      },
      showAllOption: {
        type: Boolean,
        default: true,
      },
      showNoCharactersOption: {
        type: Boolean,
        default: false,
      },
    },
    emits: ['update:modelValue', 'update:characterIds', 'update:showUnassigned'],
    setup(props, { emit }) {
      const allCheckbox = ref(null)

      // Use the appropriate prop based on which v-model is being used
      const currentCharacterIds = computed(() => {
        return props.characterIds !== undefined
          ? props.characterIds
          : props.modelValue.filter((id) => id !== 'no-characters')
      })

      const currentShowUnassigned = computed(() => {
        return props.showUnassigned !== undefined
          ? props.showUnassigned
          : props.modelValue.includes('no-characters')
      })

      // Computed properties
      const isAllSelected = computed(() => {
        return (
          props.characters.length > 0 &&
          currentCharacterIds.value.length === props.characters.length
        )
      })

      const isIndeterminate = computed(() => {
        return (
          currentCharacterIds.value.length > 0 &&
          currentCharacterIds.value.length < props.characters.length
        )
      })

      // Watch for indeterminate state changes
      watchEffect(() => {
        if (allCheckbox.value) {
          allCheckbox.value.indeterminate = isIndeterminate.value
        }
      })

      // Methods
      const toggleAll = () => {
        if (props.characterIds !== undefined) {
          // Using dual v-model
          if (isAllSelected.value) {
            emit('update:characterIds', [])
          } else {
            const allIds = props.characters.map((char) => char.id)
            emit('update:characterIds', allIds)
          }
        } else {
          // Using single v-model (legacy)
          if (isAllSelected.value) {
            emit('update:modelValue', [])
          } else {
            const allIds = props.characters.map((char) => char.id)
            emit('update:modelValue', allIds)
          }
        }
      }

      const toggleCharacter = (characterId) => {
        if (props.characterIds !== undefined) {
          // Using dual v-model
          const currentSelection = [...currentCharacterIds.value]
          const index = currentSelection.indexOf(characterId)

          if (index > -1) {
            currentSelection.splice(index, 1)
          } else {
            currentSelection.push(characterId)
          }

          emit('update:characterIds', currentSelection)
        } else {
          // Using single v-model (legacy)
          const currentSelection = [...props.modelValue]
          const index = currentSelection.indexOf(characterId)

          if (index > -1) {
            currentSelection.splice(index, 1)
          } else {
            currentSelection.push(characterId)
          }

          emit('update:modelValue', currentSelection)
        }
      }

      const toggleNoCharacters = () => {
        if (props.showUnassigned !== undefined) {
          // Using dual v-model
          emit('update:showUnassigned', !props.showUnassigned)
        } else {
          // Using single v-model (legacy)
          const currentSelection = [...props.modelValue]
          const index = currentSelection.indexOf('no-characters')

          if (index > -1) {
            currentSelection.splice(index, 1)
          } else {
            currentSelection.push('no-characters')
          }

          emit('update:modelValue', currentSelection)
        }
      }

      return {
        allCheckbox,
        currentCharacterIds,
        currentShowUnassigned,
        isAllSelected,
        isIndeterminate,
        toggleAll,
        toggleCharacter,
        toggleNoCharacters,
      }
    },
  }
</script>

<style scoped>
  .character-field {
    margin-bottom: var(--spacing-xxl);
  }

  .character-selection {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);
    max-height: 150px;
    overflow-y: auto;
    padding: var(--spacing-md);
    border: 2px solid var(--border-default);
    border-radius: var(--radius-lg);
    background: var(--bg-light);
  }

  .character-checkbox {
    display: flex;
    align-items: center;
  }

  .character-option {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    cursor: pointer;
    padding: var(--spacing-xs) var(--spacing-sm);
    border-radius: var(--radius-sm);
    transition: var(--transition-fast);
    width: 100%;
    font-size: var(--font-size-base);
  }

  .character-option:hover {
    background-color: var(--border-light);
  }

  .character-option input[type='checkbox'] {
    margin: 0;
    transform: scale(0.9);
  }

  .character-option span {
    font-weight: var(--font-weight-medium);
    color: var(--text-secondary);
  }

  /* ALL option specific styles */
  .all-option {
    background-color: var(--bg-white);
    margin-bottom: 0;
    padding: var(--spacing-xs) 0;
    border: 1px solid var(--border-default);
    border-radius: var(--radius-sm);
  }

  .all-option .character-option {
    font-weight: var(--font-weight-semibold);
    color: var(--text-label);
  }

  .all-option .character-option:hover {
    background-color: var(--bg-light);
  }

  /* Separator */
  .separator {
    height: 1px;
    background-color: var(--border-default);
    margin: var(--spacing-sm) 0;
  }

  /* Indeterminate checkbox styling */
  input[type='checkbox']:indeterminate {
    opacity: 0.6;
    position: relative;
  }

  input[type='checkbox']:indeterminate::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 8px;
    height: 2px;
    background-color: var(--primary-color);
  }
</style>
