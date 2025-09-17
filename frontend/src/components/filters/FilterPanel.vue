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
            v-model="characterSelectorValue"
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
  </div>
</template>

<script>
  import { ref, computed, watch, nextTick } from 'vue'
  import { storeToRefs } from 'pinia'
  import FilterTabs from './FilterTabs.vue'
  import FilterMultiSelect from './FilterMultiSelect.vue'
  import CharacterSelector from '../entity/CharacterSelector.vue'
  import { useGameDataStore } from '../../stores/gameData.js'
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
      const gameDataStore = useGameDataStore()
      const { data: gameData } = storeToRefs(gameDataStore)
      const { genders } = useDropdownOptions()

      const activeTab = ref(props.availableTabs[0]?.id || 'race')

      // Normalize and clone incoming filter state to avoid shared references
      // between parent/child and to keep consistent shapes for comparison.
      // This prevents identity churn and accidental mutation loops.
      const buildFilterState = (value = {}) => ({
        race: Array.isArray(value.race) ? [...value.race] : [],
        alignment: Array.isArray(value.alignment) ? [...value.alignment] : [],
        size: Array.isArray(value.size) ? [...value.size] : [],
        gender: Array.isArray(value.gender) ? [...value.gender] : [],
        class: Array.isArray(value.class) ? [...value.class] : [],
        characterIds: Array.isArray(value.characterIds) ? [...value.characterIds] : [],
        showUnassigned: value.showUnassigned === true,
      })

      // Local reactive copy of the filters used by the panel UI
      const filters = ref(buildFilterState(props.modelValue))

      // Guard flag: when we are syncing from props -> local state,
      // do not emit updates back to the parent to avoid loops.
      let syncingFromModelValue = false

      const charactersFromParent = computed(() => props.characters)

      // Computed helper used to v-model the CharacterSelector while
      // mapping the 'no-characters' sentinel to/from our boolean flag.
      const characterSelectorValue = computed({
        get() {
          const value = [...filters.value.characterIds]
          if (filters.value.showUnassigned) {
            value.push('no-characters')
          }
          return value
        },
        set(newValue) {
          filters.value.characterIds = newValue.filter((id) => id !== 'no-characters')
          filters.value.showUnassigned = newValue.includes('no-characters')
        },
      })

      // Deep-watch local filters and emit normalized updates to the parent.
      // Skip while we are applying a prop-driven sync to prevent ping-pong.
      watch(
        filters,
        () => {
          if (syncingFromModelValue) return
          emit('update:modelValue', buildFilterState(filters.value))
        },
        { deep: true }
      )

      // Sync down external changes from v-model (parent -> child).
      // Use a microtask deferral to re-enable emissions after assignment.
      watch(
        () => props.modelValue,
        (newValue) => {
          syncingFromModelValue = true
          filters.value = buildFilterState(newValue)
          nextTick(() => {
            syncingFromModelValue = false
          })
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
        characterSelectorValue,
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
  /* Component-specific styles only - shared styles handled globally */
  .filter-panel {
    background: var(--bg-white);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-xl);
    box-shadow: var(--shadow-card);
    display: flex;
    flex-direction: column;
    gap: var(--spacing-lg);
  }

  .filter-panel-content {
    padding: var(--spacing-lg);
    flex: 1;
    overflow-y: visible;
  }

  .filter-panel-content.simple {
    padding: var(--spacing-md);
  }

  .filter-section {
    animation: fadeIn var(--transition-fast);
    flex-shrink: 0;
  }

  .filter-section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-md);
  }

  .filter-section-header h4 {
    margin: 0;
    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-semibold);
    color: var(--text-primary);
  }

  .clear-filter-btn {
    padding: var(--spacing-xs) var(--spacing-sm);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-md);
    background: var(--bg-white);
    color: var(--text-muted);
    font-size: var(--font-size-xs);
    cursor: pointer;
    transition: all var(--transition-fast);
  }

  .clear-filter-btn:hover {
    background: var(--bg-light);
    border-color: var(--text-muted);
    color: var(--text-primary);
  }

  /* Character filter section */
  .character-filter-section {
    padding: 0;
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
    background: var(--bg-light);
    border-radius: 3px;
  }

  .filter-panel-content::-webkit-scrollbar-thumb {
    background: var(--border-default);
    border-radius: 3px;
  }

  .filter-panel-content::-webkit-scrollbar-thumb:hover {
    background: var(--text-muted);
  }

  /* Responsive adjustments */
  @media (max-width: 768px) {
    .filter-panel {
      max-height: 300px;
    }

    .filter-panel-content {
      padding: var(--spacing-md);
    }
  }
</style>
