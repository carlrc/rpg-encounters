<template>
  <div class="character-field">
    <label class="shared-field-label">{{ label }}</label>

    <!-- Filter Section -->
    <div v-if="enableFiltering" class="character-filters">
      <div class="filter-row">
        <FilterMultiSelect
          v-model="filters.race"
          :options="gameData?.races || []"
          placeholder="Filter by race..."
          label=""
        />
        <FilterMultiSelect
          v-model="filters.alignment"
          :options="gameData?.alignments || []"
          placeholder="Filter by alignment..."
          label=""
        />
      </div>
      <div v-if="hasActiveFilters" class="filter-summary">
        <span class="filter-count"
          >{{ activeFilterCount }} filter{{ activeFilterCount === 1 ? '' : 's' }} active</span
        >
        <button @click="clearAllFilters" class="clear-filters-btn" type="button">Clear All</button>
      </div>
    </div>

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
      <div v-for="character in filteredCharacters" :key="character.id" class="character-checkbox">
        <label class="character-option">
          <input
            type="checkbox"
            :value="character.id"
            :checked="isCharacterSelected(character.id)"
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
  import FilterMultiSelect from '../filters/FilterMultiSelect.vue'
  import { useGameData } from '../../composables/useGameData.js'
  import { applyFilters } from '../../utils/filterUtils.js'

  export default {
    name: 'CharacterSelector',
    components: {
      FilterMultiSelect,
    },
    props: {
      enableFiltering: {
        type: Boolean,
        default: false,
      },
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
      showAllOption: {
        type: Boolean,
        default: true,
      },
      showNoCharactersOption: {
        type: Boolean,
        default: false,
      },
    },
    emits: ['update:modelValue'],
    setup(props, { emit }) {
      const allCheckbox = ref(null)
      const { gameData, loadGameData } = useGameData()

      // Filter state
      const filters = ref({
        race: [],
        alignment: [],
      })

      // Load game data asynchronously if filtering is enabled
      if (props.enableFiltering) {
        loadGameData()
      }

      // Filtered characters based on active filters
      const filteredCharacters = computed(() => {
        if (!props.enableFiltering || !hasActiveFilters.value || !gameData.value) {
          return props.characters
        }
        return applyFilters(props.characters, filters.value)
      })

      // Check if any filters are active
      const hasActiveFilters = computed(() => {
        return filters.value.race.length > 0 || filters.value.alignment.length > 0
      })

      // Count active filters
      const activeFilterCount = computed(() => {
        let count = 0
        if (filters.value.race.length > 0) count++
        if (filters.value.alignment.length > 0) count++
        return count
      })

      // Clear all filters
      const clearAllFilters = () => {
        filters.value.race = []
        filters.value.alignment = []
      }

      // Get current character IDs from modelValue
      const currentCharacterIds = computed(() => {
        const ids = (props.modelValue || []).filter((id) => id !== 'no-characters')

        // Normalize all IDs to numbers for consistent comparison
        return ids.map((id) => {
          const numId = typeof id === 'string' ? parseInt(id, 10) : Number(id)
          return isNaN(numId) ? id : numId
        })
      })

      const currentShowUnassigned = computed(() => {
        return (props.modelValue || []).includes('no-characters')
      })

      // Helper function to check if character is selected with proper type handling
      const isCharacterSelected = (characterId) => {
        // Ensure both values are numbers for comparison
        const normalizedCharId = Number(characterId)
        return currentCharacterIds.value.some((id) => {
          const normalizedId = Number(id)
          return normalizedId === normalizedCharId
        })
      }

      // Computed properties - based on visible filtered characters
      const isAllSelected = computed(() => {
        return (
          filteredCharacters.value.length > 0 &&
          filteredCharacters.value.every((char) => isCharacterSelected(char.id))
        )
      })

      const isIndeterminate = computed(() => {
        const visibleSelectedCount = filteredCharacters.value.filter((char) =>
          isCharacterSelected(char.id)
        ).length
        return visibleSelectedCount > 0 && visibleSelectedCount < filteredCharacters.value.length
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
          emit('update:modelValue', [])
        } else {
          // Select all visible filtered characters
          const allIds = filteredCharacters.value.map((char) => char.id)
          emit('update:modelValue', allIds)
        }
      }

      const toggleCharacter = (characterId) => {
        // Ensure characterId is a number for consistent handling
        const normalizedCharId = Number(characterId)

        const currentSelection = [...currentCharacterIds.value]
        const index = currentSelection.findIndex((id) => Number(id) === normalizedCharId)

        if (index > -1) {
          currentSelection.splice(index, 1)
        } else {
          currentSelection.push(normalizedCharId)
        }

        emit('update:modelValue', currentSelection)
      }

      const toggleNoCharacters = () => {
        const currentSelection = [...currentCharacterIds.value]
        const showUnassigned = currentShowUnassigned.value

        if (showUnassigned) {
          // Remove no-characters
          emit('update:modelValue', currentSelection)
        } else {
          // Add no-characters
          emit('update:modelValue', [...currentSelection, 'no-characters'])
        }
      }

      return {
        gameData,
        filters,
        filteredCharacters,
        hasActiveFilters,
        activeFilterCount,
        clearAllFilters,
        allCheckbox,
        currentCharacterIds,
        currentShowUnassigned,
        isCharacterSelected,
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

  /* Filter section styles */
  .character-filters {
    margin-bottom: var(--spacing-lg);
    padding: var(--spacing-md);
    border: 2px solid var(--border-default);
    border-radius: var(--radius-lg);
    background: var(--bg-white);
  }

  .filter-row {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--spacing-sm);
    margin-bottom: var(--spacing-sm);
  }

  .filter-summary {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: var(--spacing-sm);
    border-top: 1px solid var(--border-light);
  }

  .filter-count {
    font-size: var(--font-size-sm);
    color: var(--text-muted);
    font-weight: var(--font-weight-medium);
  }

  .clear-filters-btn {
    padding: var(--spacing-xs) var(--spacing-sm);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-sm);
    background: var(--bg-white);
    color: var(--text-secondary);
    font-size: var(--font-size-sm);
    cursor: pointer;
    transition: var(--transition-fast);
  }

  .clear-filters-btn:hover {
    background: var(--bg-light);
    border-color: var(--primary-color);
    color: var(--primary-color);
  }

  /* Responsive adjustments for filters */
  @media (max-width: 768px) {
    .filter-row {
      grid-template-columns: 1fr;
    }
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
