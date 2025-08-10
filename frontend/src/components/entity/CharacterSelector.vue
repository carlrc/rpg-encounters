<template>
  <div class="character-field">
    <label class="shared-field-label">{{ label }}</label>
    <div class="character-selection">
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
</style>
