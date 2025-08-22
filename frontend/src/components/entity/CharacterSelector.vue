<template>
  <div class="character-field">
    <label class="shared-field-label">{{ label }}</label>
    <div class="character-selection">
      <!-- ALL option -->
      <div class="character-checkbox all-option">
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

      <!-- Separator -->
      <div class="separator"></div>

      <!-- Individual characters -->
      <div v-for="character in characters" :key="character.id" class="character-checkbox">
        <label class="character-option">
          <input
            type="checkbox"
            :value="character.id"
            :checked="modelValue.includes(character.id)"
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
      characters: {
        type: Array,
        default: () => [],
      },
      label: {
        type: String,
        default: 'Characters',
      },
    },
    emits: ['update:modelValue'],
    setup(props, { emit }) {
      const allCheckbox = ref(null)

      // Computed properties
      const isAllSelected = computed(() => {
        return props.characters.length > 0 && props.modelValue.length === props.characters.length
      })

      const isIndeterminate = computed(() => {
        return props.modelValue.length > 0 && props.modelValue.length < props.characters.length
      })

      // Watch for indeterminate state changes
      watchEffect(() => {
        if (allCheckbox.value) {
          allCheckbox.value.indeterminate = isIndeterminate.value
        }
      })

      // Methods
      const toggleAll = () => {
        if (isAllSelected.value) {
          // Deselect all
          emit('update:modelValue', [])
        } else {
          // Select all
          const allIds = props.characters.map((char) => char.id)
          emit('update:modelValue', allIds)
        }
      }

      const toggleCharacter = (characterId) => {
        const currentSelection = [...props.modelValue]
        const index = currentSelection.indexOf(characterId)

        if (index > -1) {
          currentSelection.splice(index, 1)
        } else {
          currentSelection.push(characterId)
        }

        emit('update:modelValue', currentSelection)
      }

      return {
        allCheckbox,
        isAllSelected,
        isIndeterminate,
        toggleAll,
        toggleCharacter,
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

  /* ALL option specific styles */
  .all-option {
    background-color: #f0f4f8;
    margin-bottom: 0;
    padding: 0.25rem 0;
  }

  .all-option .character-option {
    font-weight: 600;
    color: #2c3e50;
  }

  .all-option .character-option:hover {
    background-color: #e2e8f0;
  }

  /* Separator */
  .separator {
    height: 1px;
    background-color: #dee2e6;
    margin: 0.5rem 0;
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
    background-color: #007bff;
  }
</style>
