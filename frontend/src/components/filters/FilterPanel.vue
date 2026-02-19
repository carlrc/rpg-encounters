<template>
  <div class="filter-panel">
    <div v-if="enableTabs" class="filter-panel-content">
      <FilterTabs
        :tabs="availableTabs"
        :active-tab="activeTab"
        :filters="filters"
        @update:active-tab="activeTab = $event"
      />

      <div class="tab-content">
        <div v-if="activeTabConfig" class="filter-section">
          <div class="filter-section-header">
            <h4>{{ activeTabConfig.title }}</h4>
          </div>

          <FilterMultiSelect
            v-if="activeTabConfig.id === 'characters'"
            v-model="characterSelectorValue"
            :options="characterOptions"
            placeholder="Select characters..."
            :expanded="true"
            :label="''"
          />

          <FilterMultiSelect
            v-else
            v-model="filters[activeTabConfig.model]"
            :options="activeTabConfig.options"
            :placeholder="activeTabConfig.placeholder"
            :expanded="true"
            :label="''"
          />
        </div>
      </div>
    </div>

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
  import { useGameDataStore } from '../../stores/gameData.js'
  import { useDropdownOptions } from '../../composables/useDropdownOptions.js'

  export default {
    name: 'FilterPanel',
    components: {
      FilterTabs,
      FilterMultiSelect,
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

      const buildFilterState = (value = {}) => ({
        race: Array.isArray(value.race) ? [...value.race] : [],
        alignment: Array.isArray(value.alignment) ? [...value.alignment] : [],
        size: Array.isArray(value.size) ? [...value.size] : [],
        gender: Array.isArray(value.gender) ? [...value.gender] : [],
        class: Array.isArray(value.class) ? [...value.class] : [],
        characterIds: Array.isArray(value.characterIds) ? [...value.characterIds] : [],
        showUnassigned: value.showUnassigned === true,
      })

      const filters = ref(buildFilterState(props.modelValue))
      let syncingFromModelValue = false

      const charactersFromParent = computed(() => props.characters)

      const characterOptions = computed(() => {
        const options = [
          {
            label: 'NONE - Select items with no assignments',
            value: 'no-characters',
          },
        ]

        charactersFromParent.value.forEach((character) => {
          options.push({
            label: character.name || `Character ${character.id}`,
            value: character.id,
          })
        })

        return options
      })

      const tabConfigMap = computed(() => ({
        race: {
          id: 'race',
          title: 'Filter by Race',
          model: 'race',
          placeholder: 'Select races...',
          options: gameData.value?.races || [],
        },
        alignment: {
          id: 'alignment',
          title: 'Filter by Alignment',
          model: 'alignment',
          placeholder: 'Select alignments...',
          options: gameData.value?.alignments || [],
        },
        size: {
          id: 'size',
          title: 'Filter by Size',
          model: 'size',
          placeholder: 'Select sizes...',
          options: gameData.value?.sizes?.character || [],
        },
        gender: {
          id: 'gender',
          title: 'Filter by Gender',
          model: 'gender',
          placeholder: 'Select genders...',
          options: genders || [],
        },
        class: {
          id: 'class',
          title: 'Filter by Class',
          model: 'class',
          placeholder: 'Select classes...',
          options: gameData.value?.classes || [],
        },
        characters: {
          id: 'characters',
          title: 'Filter by Characters',
          model: 'characterIds',
          placeholder: 'Select characters...',
          options: characterOptions.value,
        },
      }))

      const activeTabConfig = computed(() => tabConfigMap.value[activeTab.value] || null)

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

      watch(
        filters,
        () => {
          if (syncingFromModelValue) return
          emit('update:modelValue', buildFilterState(filters.value))
        },
        { deep: true }
      )

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

      watch(
        () => props.availableTabs,
        (tabs) => {
          if (!tabs.some((tab) => tab.id === activeTab.value)) {
            activeTab.value = tabs[0]?.id || 'race'
          }
        },
        { deep: true }
      )

      return {
        gameData,
        activeTab,
        activeTabConfig,
        filters,
        characterOptions,
        characterSelectorValue,
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
