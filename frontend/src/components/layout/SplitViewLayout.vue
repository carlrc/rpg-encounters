<template>
  <div class="split-view">
    <!-- Left Pane - Entity List -->
    <div class="list-pane">
      <div class="list-header">
        <h3>{{ listTitle }}</h3>
      </div>

      <!-- Custom header content (for FilterBar - deprecated) -->
      <slot name="header-content" />

      <!-- Search and Filter Controls -->
      <div class="filter-controls">
        <SearchInput :placeholder="`Search ${listTitle.toLowerCase()}...`" @search="handleSearch" />

        <!-- Filter toggle button -->
        <button
          v-if="(enableCharacterFilter && characters?.length > 0) || enableAttributeFilter"
          @click="toggleFilterPanel"
          :class="['filter-toggle-btn', { 'has-active-filters': hasAnyActiveFilters }]"
          :title="filterButtonTitle"
        >
          ⚙️
        </button>
      </div>

      <!-- Collapsible filter panel -->
      <div v-if="showFilterPanel" class="filter-panel-container" @click.self="toggleFilterPanel">
        <!-- Character filter panel (for memories/reveals) -->
        <div v-if="enableCharacterFilter && !enableAttributeFilter" class="filter-panel">
          <div class="filter-header">
            <span>Filter by Characters</span>
            <button
              v-if="selectedCharacterIds.length > 0 || showUnassigned"
              @click="clearCharacterFilters"
              class="shared-btn shared-btn-secondary"
              style="padding: var(--spacing-xs) var(--spacing-sm); font-size: var(--font-size-sm)"
            >
              Clear
            </button>
            <button class="close-btn" type="button" @click="toggleFilterPanel">×</button>
          </div>

          <!-- Reuse CharacterSelector in filter mode -->
          <CharacterSelector
            v-model:character-ids="selectedCharacterIds"
            v-model:show-unassigned="showUnassigned"
            :characters="characters"
            :label="''"
            :show-all-option="true"
            :show-no-characters-option="true"
          />
        </div>

        <!-- Attribute filter panel (for characters page) -->
        <div v-else-if="enableAttributeFilter" class="attribute-filter-panel">
          <div class="filter-header">
            <span>Filters</span>
            <button class="close-btn" type="button" @click="toggleFilterPanel">×</button>
          </div>
          <slot name="filter-content" />
        </div>
      </div>

      <div class="list-content">
        <div
          v-for="item in filteredItems"
          :key="item.id"
          :class="['list-item', { active: selectedItemId === item.id }]"
          @click="$emit('select-item', item.id)"
        >
          {{ item.rl_name || item.name || item.title }}
        </div>

        <div v-if="filteredItems.length === 0 && searchQuery" class="empty-state">
          No {{ listTitle.toLowerCase() }} found matching "{{ searchQuery }}"
        </div>

        <div v-else-if="!loading && filteredItems.length === 0" class="empty-state">
          {{ emptyMessage }}
        </div>
      </div>

      <div class="list-footer">
        <button v-if="createButtonText" @click="$emit('create-item')" class="add-btn">
          <span class="plus-icon">+</span>
          {{ createButtonText }}
        </button>

        <slot name="footer-actions" />
      </div>
    </div>

    <!-- Right Pane - Detail View -->
    <div class="detail-pane">
      <slot name="detail-content" />
    </div>
  </div>
</template>

<script>
  import { ref, computed } from 'vue'
  import SearchInput from '../ui/SearchInput.vue'
  import CharacterSelector from '../entity/CharacterSelector.vue'

  export default {
    name: 'SplitViewLayout',
    components: {
      SearchInput,
      CharacterSelector,
    },
    props: {
      items: {
        type: Array,
        required: true,
      },
      selectedItemId: {
        type: [Number, String],
        default: null,
      },
      listTitle: {
        type: String,
        required: true,
      },
      createButtonText: {
        type: String,
        required: true,
      },
      emptyMessage: {
        type: String,
        default: 'No items yet',
      },
      characters: {
        type: Array,
        default: () => [],
      },
      enableCharacterFilter: {
        type: Boolean,
        default: false,
      },
      enableAttributeFilter: {
        type: Boolean,
        default: false,
      },
      attributeFilters: {
        type: Object,
        default: () => ({}),
      },
      loading: {
        type: Boolean,
        default: false,
      },
    },
    emits: ['select-item', 'create-item'],
    setup(props) {
      const searchQuery = ref('')
      const showFilterPanel = ref(false)
      const selectedCharacterIds = ref([])
      const showUnassigned = ref(false)

      const filteredItems = computed(() => {
        let items = props.items

        // Apply text search filter (existing)
        if (searchQuery.value) {
          const query = searchQuery.value.toLowerCase()
          items = items.filter((item) => {
            const name = item.name || item.title || ''
            const rlName = item.rl_name || ''
            return name.toLowerCase().includes(query) || rlName.toLowerCase().includes(query)
          })
        }

        // Apply character filter (new)
        if (selectedCharacterIds.value.length > 0 || showUnassigned.value) {
          items = items.filter((item) => {
            const hasNoCharacters = !item.character_ids || item.character_ids.length === 0

            // Check unassigned filter
            if (showUnassigned.value && hasNoCharacters) {
              return true
            }

            // Check character filters
            if (selectedCharacterIds.value.length > 0 && item.character_ids) {
              return item.character_ids.some((id) => selectedCharacterIds.value.includes(id))
            }

            return false
          })
        }

        return items
      })

      const hasActiveCharacterFilters = computed(() => {
        return selectedCharacterIds.value.length > 0 || showUnassigned.value
      })

      const hasActiveAttributeFilters = computed(() => {
        if (!props.attributeFilters) return false
        return Object.values(props.attributeFilters).some((filterValue) => {
          if (Array.isArray(filterValue)) {
            return filterValue.length > 0
          }
          return Boolean(filterValue)
        })
      })

      const hasAnyActiveFilters = computed(() => {
        return hasActiveCharacterFilters.value || hasActiveAttributeFilters.value
      })

      const filterButtonTitle = computed(() => {
        if (props.enableAttributeFilter) {
          return 'Filter by attributes'
        }
        return 'Filter by characters'
      })

      const handleSearch = (query) => {
        searchQuery.value = query
      }

      const toggleFilterPanel = () => {
        showFilterPanel.value = !showFilterPanel.value
      }

      const clearCharacterFilters = () => {
        selectedCharacterIds.value = []
        showUnassigned.value = false
      }

      return {
        searchQuery,
        showFilterPanel,
        selectedCharacterIds,
        showUnassigned,
        filteredItems,
        hasActiveCharacterFilters,
        hasActiveAttributeFilters,
        hasAnyActiveFilters,
        filterButtonTitle,
        handleSearch,
        toggleFilterPanel,
        clearCharacterFilters,
      }
    },
  }
</script>

<style scoped>
  .split-view {
    display: flex;
    height: calc(100vh - var(--header-height)); /* Fallback for older browsers */
    height: calc(100dvh - var(--header-height)); /* Dynamic viewport height for iOS */
    max-height: calc(100vh - var(--header-height));
    max-height: calc(100dvh - var(--header-height));
    gap: 0;
    /* No overflow or min-width rules - let body handle all horizontal scrolling */
  }

  .list-pane {
    width: clamp(280px, 30%, 400px); /* Flexible width between 280px and 400px */
    flex-shrink: 0;
    display: flex;
    flex-direction: column;
    background: var(--bg-light);
    border-right: 2px solid var(--border-default);
    overflow: hidden;
  }

  .list-header {
    padding: var(--spacing-xl) var(--spacing-lg) var(--spacing-lg) var(--spacing-lg);
    border-bottom: 1px solid var(--border-default);
    background: var(--bg-white);
  }

  .list-header h3 {
    margin: 0;
    font-size: var(--font-size-xl);
    font-weight: var(--font-weight-bold);
    color: var(--text-label);
    text-align: center;
  }

  .filter-controls {
    display: flex;
    gap: var(--spacing-sm);
    align-items: stretch;
  }

  .filter-controls :deep(.search-container) {
    flex: 1;
    padding: var(--spacing-md) var(--spacing-lg);
    margin: 0;
  }

  .filter-toggle-btn {
    padding: var(--spacing-sm) var(--spacing-md);
    background: var(--bg-white);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-md);
    cursor: pointer;
    font-size: var(--font-size-xl);
    transition: var(--transition-fast);
    margin: var(--spacing-md) var(--spacing-lg) var(--spacing-md) 0;
    align-self: center;
  }

  .filter-toggle-btn:hover {
    background: var(--bg-light);
    border-color: var(--primary-color);
  }

  .filter-toggle-btn.has-active-filters {
    background: var(--primary-color);
    border-color: var(--primary-color);
  }

  .filter-panel-container {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: var(--spacing-lg);
    z-index: var(--z-modal);
  }

  .filter-panel {
    width: min(520px, 100%);
    max-height: 90vh;
    overflow-y: auto;
    padding: var(--spacing-xl);
    background: var(--bg-white);
    border-radius: var(--radius-xl);
    box-shadow: var(--shadow-card-hover);
    border: 1px solid var(--border-light);
  }

  .attribute-filter-panel {
    width: min(520px, 100%);
    max-height: 90vh;
    overflow-y: auto;
    padding: var(--spacing-xl);
    background: var(--bg-white);
    border-radius: var(--radius-xl);
    box-shadow: var(--shadow-card-hover);
    border: 1px solid var(--border-light);
  }

  .filter-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-md);
    font-weight: var(--font-weight-semibold);
    color: var(--text-secondary);
  }

  .close-btn {
    background: none;
    border: none;
    font-size: var(--font-size-xl);
    cursor: pointer;
    color: var(--text-muted);
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: var(--radius-round);
    transition: var(--transition-fast);
  }

  .close-btn:hover {
    background: var(--bg-light);
    color: var(--text-primary);
  }

  .list-content {
    flex: 1;
    overflow-y: auto;
    padding: var(--spacing-sm) 0;
    -webkit-overflow-scrolling: touch;
    /* Allow both horizontal and vertical panning for better touch scrolling */
    touch-action: auto;
  }

  .list-item {
    padding: var(--spacing-md) var(--spacing-lg);
    cursor: pointer;
    transition: var(--transition-fast);
    border-left: 3px solid transparent;
    font-weight: var(--font-weight-medium);
    color: var(--text-secondary);
    background: var(--bg-white);
    margin: 2px var(--spacing-sm);
    border-radius: var(--radius-md);
    border: 1px solid transparent;
  }

  .list-item:hover {
    background: var(--color-encounter-hover);
    color: var(--primary-color);
    border-color: var(--primary-alpha-30);
  }

  .list-item.active {
    background: var(--primary-color);
    color: white;
    border-left-color: var(--primary-darker);
    font-weight: var(--font-weight-semibold);
    box-shadow: var(--shadow-button);
  }

  .list-item.active:hover {
    background: var(--primary-dark);
  }

  .empty-state {
    padding: 40px var(--spacing-lg);
    text-align: center;
    color: var(--text-muted);
    font-style: italic;
    font-size: var(--font-size-base);
  }

  .list-footer {
    padding: var(--spacing-lg);
    border-top: 1px solid var(--border-default);
    background: var(--bg-white);
  }

  .add-btn {
    width: 100%;
    padding: var(--spacing-md) var(--spacing-lg);
    background: var(--success-color);
    color: white;
    border: none;
    border-radius: var(--radius-lg);
    cursor: pointer;
    font-size: var(--font-size-base);
    font-weight: var(--font-weight-semibold);
    transition: background-color var(--transition-fast);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--spacing-sm);
    box-shadow: var(--shadow-success);
  }

  .add-btn:hover {
    background: var(--success-dark);
  }

  .plus-icon {
    font-size: var(--font-size-xl);
    font-weight: var(--font-weight-bold);
  }

  .detail-pane {
    flex: 1;
    /* Removed min-width to prevent forced horizontal scrolling */
    padding: var(--spacing-xl);
    padding-bottom: calc(var(--spacing-xl) + var(--spacing-lg));
    overflow-y: auto;
    /* No overflow-x rules - body handles horizontal scrolling */
    background: var(--bg-white);
    -webkit-overflow-scrolling: touch;
    /* Allow both horizontal and vertical panning for better touch scrolling */
    touch-action: auto;
  }

  /* Scrollbar styling for list */
  .list-content::-webkit-scrollbar {
    width: 6px;
  }

  .list-content::-webkit-scrollbar-track {
    background: var(--bg-light);
  }

  .list-content::-webkit-scrollbar-thumb {
    background: var(--border-default);
    border-radius: 3px;
  }

  .list-content::-webkit-scrollbar-thumb:hover {
    background: var(--text-muted);
  }

  /* Split view now inherits sizing from main-layout grid */

  /* Enhanced touch targets for tablets */
  @media (min-width: 768px) and (max-width: 1023px) {
    .filter-toggle-btn {
      min-width: 44px;
      min-height: 44px;
      padding: var(--spacing-md);
    }

    .list-item {
      padding: var(--spacing-lg) var(--spacing-xl);
      margin: var(--spacing-xs) var(--spacing-sm);
    }
  }

  /* Even on small screens, maintain horizontal layout with scroll */
  @media (max-width: 767px) {
    /* No split-view specific rules needed - body handles scrolling */

    .filter-panel-container {
      padding: var(--spacing-md);
    }

    .filter-panel,
    .attribute-filter-panel {
      width: 100%;
      max-width: 520px;
      max-height: 95vh;
      border-radius: var(--radius-lg);
      padding: var(--spacing-lg);
    }
  }
</style>
