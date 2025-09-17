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
      <FilterMultiSelect
        v-model="selectionProxy"
        :options="characterOptions"
        :expanded="true"
        :option-label-key="'label'"
        :option-value-key="'value'"
        :exclude-from-select-all-key="'excludeFromSelectAll'"
        :show-select-all="showAllOption"
        placeholder="Select characters..."
        label=""
      />
    </div>
  </div>
</template>

<script>
  import { ref, computed } from 'vue'
  import FilterMultiSelect from '../filters/FilterMultiSelect.vue'
  import { storeToRefs } from 'pinia'
  import { useGameDataStore } from '../../stores/gameData.js'
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
      const gameDataStore = useGameDataStore()
      const { data: gameData } = storeToRefs(gameDataStore)

      // Filter state
      const filters = ref({
        race: [],
        alignment: [],
      })

      // Load game data asynchronously if filtering is enabled
      if (props.enableFiltering) {
        gameDataStore.load()
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

      const NO_CHAR_SENTINEL = 'no-characters'

      const characterOptions = computed(() => {
        const options = []
        const seen = new Set()

        if (props.showNoCharactersOption) {
          options.push({
            label: 'NONE - Select items with no assignments',
            value: NO_CHAR_SENTINEL,
            excludeFromSelectAll: true,
          })
        }

        const addCharacter = (character) => {
          if (!character) return
          const id = character.id
          if (seen.has(id)) return
          seen.add(id)
          options.push({ label: character.name || `Character ${id}`, value: id })
        }

        filteredCharacters.value.forEach(addCharacter)

        // Ensure previously selected characters remain visible even if filtered out
        props.characters
          .filter((char) => currentCharacterIds.value.includes(Number(char.id)))
          .forEach(addCharacter)

        return options
      })

      const selectionProxy = computed({
        get() {
          const selection = [...currentCharacterIds.value]
          if (currentShowUnassigned.value) {
            selection.push(NO_CHAR_SENTINEL)
          }
          return selection
        },
        set(newSelection) {
          const includeNone = newSelection.some((value) => value === NO_CHAR_SENTINEL)
          const normalizedIds = newSelection
            .filter((value) => value !== NO_CHAR_SENTINEL)
            .map((value) => Number(value))
            .filter((value) => !Number.isNaN(value))

          const uniqueIds = Array.from(new Set(normalizedIds))
          if (includeNone) {
            emit('update:modelValue', [...uniqueIds, NO_CHAR_SENTINEL])
          } else {
            emit('update:modelValue', uniqueIds)
          }
        },
      })

      return {
        gameData,
        filters,
        filteredCharacters,
        hasActiveFilters,
        activeFilterCount,
        clearAllFilters,
        currentCharacterIds,
        currentShowUnassigned,
        characterOptions,
        selectionProxy,
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
    margin-top: var(--spacing-md);
  }

  .character-selection :deep(.filter-multiselect.expanded) {
    width: 100%;
  }
</style>
