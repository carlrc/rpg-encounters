<template>
  <div class="filter-panel">
    <!-- Tabbed interface for complex filtering -->
    <div v-if="enableTabs" class="filter-panel-content">
      <FilterTabs
        :tabs="availableTabs"
        :active-tab="activeTab"
        :filters="filters"
        @update:active-tab="activeTab = $event"
      />

      <div class="tab-content">
        <!-- Race filters -->
        <div v-if="activeTab === 'race'" class="filter-section">
          <div class="filter-section-header">
            <h4>Filter by Race</h4>
            <button
              v-if="filters.race?.length > 0"
              @click="clearFilter('race')"
              class="clear-filter-btn"
              type="button"
            >
              Clear
            </button>
          </div>
          <FilterMultiSelect
            v-if="gameData"
            :options="gameData.races || []"
            v-model="filters.race"
            placeholder="Select races..."
            :label="''"
          />
        </div>

        <!-- Alignment filters -->
        <div v-if="activeTab === 'alignment'" class="filter-section">
          <div class="filter-section-header">
            <h4>Filter by Alignment</h4>
            <button
              v-if="filters.alignment?.length > 0"
              @click="clearFilter('alignment')"
              class="clear-filter-btn"
              type="button"
            >
              Clear
            </button>
          </div>
          <FilterMultiSelect
            v-if="gameData"
            :options="gameData.alignments || []"
            v-model="filters.alignment"
            placeholder="Select alignments..."
            :label="''"
          />
        </div>

        <!-- Size filters -->
        <div v-if="activeTab === 'size'" class="filter-section">
          <div class="filter-section-header">
            <h4>Filter by Size</h4>
            <button
              v-if="filters.size?.length > 0"
              @click="clearFilter('size')"
              class="clear-filter-btn"
              type="button"
            >
              Clear
            </button>
          </div>
          <FilterMultiSelect
            v-if="gameData"
            :options="gameData.sizes?.character || []"
            v-model="filters.size"
            placeholder="Select sizes..."
            :label="''"
          />
        </div>

        <!-- Gender filters -->
        <div v-if="activeTab === 'gender'" class="filter-section">
          <div class="filter-section-header">
            <h4>Filter by Gender</h4>
            <button
              v-if="filters.gender?.length > 0"
              @click="clearFilter('gender')"
              class="clear-filter-btn"
              type="button"
            >
              Clear
            </button>
          </div>
          <FilterMultiSelect
            v-if="genders"
            :options="genders"
            v-model="filters.gender"
            placeholder="Select genders..."
            :label="''"
          />
        </div>

        <!-- Class filters -->
        <div v-if="activeTab === 'class'" class="filter-section">
          <div class="filter-section-header">
            <h4>Filter by Class</h4>
            <button
              v-if="filters.class?.length > 0"
              @click="clearFilter('class')"
              class="clear-filter-btn"
              type="button"
            >
              Clear
            </button>
          </div>
          <FilterMultiSelect
            v-if="gameData"
            :options="gameData.classes || []"
            v-model="filters.class"
            placeholder="Select classes..."
            :label="''"
          />
        </div>

        <!-- Characters filters (for memories/reveals pages) -->
        <div v-if="activeTab === 'characters'" class="filter-section">
          <div class="filter-section-header">
            <h4>Filter by Characters</h4>
            <button
              v-if="filters.characterIds?.length > 0 || filters.showUnassigned"
              @click="clearCharactersFilter"
              class="clear-filter-btn"
              type="button"
            >
              Clear
            </button>
          </div>
          <CharacterSelector
            v-model:character-ids="filters.characterIds"
            v-model:show-unassigned="filters.showUnassigned"
            :characters="charactersFromParent"
            :label="''"
            :show-all-option="true"
            :show-no-characters-option="true"
          />
        </div>
      </div>
    </div>

    <!-- Simple interface for character-only filtering -->
    <div v-else class="filter-panel-content simple">
      <slot />
    </div>

    <!-- Active filters summary -->
    <div v-if="hasActiveFilters" class="active-filters-summary">
      <div class="filter-info">
        <span class="filter-count">
          {{ totalActiveFilters }} filter{{ totalActiveFilters === 1 ? '' : 's' }} active
        </span>
      </div>
      <button @click="clearAllFilters" class="clear-all-btn" type="button">Clear All</button>
    </div>
  </div>
</template>

<script>
  import { ref, computed, watch } from 'vue'
  import FilterTabs from './FilterTabs.vue'
  import FilterMultiSelect from './FilterMultiSelect.vue'
  import CharacterSelector from '../entity/CharacterSelector.vue'
  import { useGameData } from '../../composables/useGameData.js'
  import { useDropdownOptions } from '../../composables/useDropdownOptions.js'

  export default {
    name: 'FilterPanel',
    components: {
      FilterTabs,
      FilterMultiSelect,
      CharacterSelector,
    },
    props: {
      modelValue: {
        type: Object,
        default: () => ({}),
      },
      enableTabs: {
        type: Boolean,
        default: false,
      },
      availableTabs: {
        type: Array,
        default: () => [],
      },
      characters: {
        type: Array,
        default: () => [],
      },
    },
    emits: ['update:modelValue'],
    setup(props, { emit }) {
      const { gameData } = useGameData()
      const { genders } = useDropdownOptions()

      const activeTab = ref(props.availableTabs[0]?.id || 'race')

      const filters = ref({
        race: props.modelValue.race || [],
        alignment: props.modelValue.alignment || [],
        size: props.modelValue.size || [],
        gender: props.modelValue.gender || [],
        class: props.modelValue.class || [],
        characterIds: props.modelValue.characterIds || [],
        showUnassigned: props.modelValue.showUnassigned || false,
      })

      const charactersFromParent = computed(() => props.characters)

      // Watch for changes and emit updates
      watch(
        filters,
        () => {
          emit('update:modelValue', { ...filters.value })
        },
        { deep: true }
      )

      // Watch for external changes to modelValue
      watch(
        () => props.modelValue,
        (newValue) => {
          filters.value = {
            race: newValue.race || [],
            alignment: newValue.alignment || [],
            size: newValue.size || [],
            gender: newValue.gender || [],
            class: newValue.class || [],
            characterIds: newValue.characterIds || [],
            showUnassigned: newValue.showUnassigned || false,
          }
        },
        { deep: true }
      )

      const hasActiveFilters = computed(() => {
        return Object.values(filters.value).some((filterValue) => {
          if (Array.isArray(filterValue)) {
            return filterValue.length > 0
          }
          return Boolean(filterValue)
        })
      })

      const totalActiveFilters = computed(() => {
        return Object.values(filters.value).reduce((count, filterValue) => {
          if (Array.isArray(filterValue)) {
            return count + (filterValue.length > 0 ? 1 : 0)
          }
          return count + (filterValue ? 1 : 0)
        }, 0)
      })

      const clearFilter = (filterType) => {
        if (Array.isArray(filters.value[filterType])) {
          filters.value[filterType] = []
        } else {
          filters.value[filterType] = ''
        }
      }

      const clearAllFilters = () => {
        filters.value = {
          race: [],
          alignment: [],
          size: [],
          gender: [],
          class: [],
          characterIds: [],
          showUnassigned: false,
        }
      }

      const clearCharactersFilter = () => {
        filters.value.characterIds = []
        filters.value.showUnassigned = false
      }

      return {
        gameData,
        genders,
        charactersFromParent,
        activeTab,
        filters,
        hasActiveFilters,
        totalActiveFilters,
        clearFilter,
        clearAllFilters,
        clearCharactersFilter,
      }
    },
  }
</script>

<style scoped>
  .filter-panel {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 0.75rem;
    overflow: hidden;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    max-height: 400px;
    display: flex;
    flex-direction: column;
  }

  .filter-panel-content {
    padding: 1rem;
    flex: 1;
    overflow-y: auto;
    min-height: 0;
  }

  .filter-panel-content.simple {
    padding: 0.75rem;
  }

  .filter-section {
    animation: fadeIn 0.2s ease;
    flex-shrink: 0;
  }

  .filter-section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
  }

  .filter-section-header h4 {
    margin: 0;
    font-size: 0.875rem;
    font-weight: 600;
    color: #374151;
  }

  .clear-filter-btn {
    padding: 0.25rem 0.5rem;
    border: 1px solid #d1d5db;
    border-radius: 0.375rem;
    background: white;
    color: #6b7280;
    font-size: 0.75rem;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .clear-filter-btn:hover {
    background: #f9fafb;
    border-color: #9ca3af;
    color: #374151;
  }

  /* Character filter section */
  .character-filter-section {
    padding: 0;
  }

  .active-filters-summary {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 1rem;
    border-top: 1px solid #e5e7eb;
    background: #f9fafb;
    flex-shrink: 0;
  }

  .filter-info {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .filter-count {
    font-size: 0.875rem;
    color: #6b7280;
    font-weight: 500;
  }

  .clear-all-btn {
    padding: 0.5rem 0.75rem;
    border: 1px solid #ef4444;
    border-radius: 0.375rem;
    background: white;
    color: #ef4444;
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .clear-all-btn:hover {
    background: #ef4444;
    color: white;
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  /* Scrollbar styling for filter content */
  .filter-panel-content::-webkit-scrollbar {
    width: 6px;
  }

  .filter-panel-content::-webkit-scrollbar-track {
    background: #f1f5f9;
    border-radius: 3px;
  }

  .filter-panel-content::-webkit-scrollbar-thumb {
    background: #cbd5e1;
    border-radius: 3px;
  }

  .filter-panel-content::-webkit-scrollbar-thumb:hover {
    background: #94a3b8;
  }

  /* Responsive adjustments */
  @media (max-width: 768px) {
    .filter-panel {
      max-height: 300px;
    }

    .filter-panel-content {
      padding: 0.75rem;
    }

    .active-filters-summary {
      flex-direction: column;
      gap: 0.5rem;
      align-items: stretch;
    }

    .clear-all-btn {
      width: 100%;
      justify-content: center;
    }
  }
</style>
