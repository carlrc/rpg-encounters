<template>
  <div class="filter-tabs">
    <div class="tab-list">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        :class="[
          'tab-button',
          {
            active: activeTab === tab.id,
            'has-filters': hasActiveFilters(tab.id),
          },
        ]"
        @click="$emit('update:activeTab', tab.id)"
        type="button"
      >
        <span class="tab-label">{{ tab.label }}</span>
        <span v-if="hasActiveFilters(tab.id)" class="filter-badge">
          {{ getFilterCount(tab.id) }}
        </span>
      </button>
    </div>
  </div>
</template>

<script>
  import { computed } from 'vue'

  export default {
    name: 'FilterTabs',
    props: {
      tabs: {
        type: Array,
        required: true,
      },
      activeTab: {
        type: String,
        required: true,
      },
      filters: {
        type: Object,
        required: true,
      },
    },
    emits: ['update:activeTab'],
    setup(props) {
      const hasActiveFilters = (tabId) => {
        const filterValue = props.filters[tabId]
        if (Array.isArray(filterValue)) {
          return filterValue.length > 0
        }
        return Boolean(filterValue)
      }

      const getFilterCount = (tabId) => {
        const filterValue = props.filters[tabId]
        if (Array.isArray(filterValue)) {
          return filterValue.length
        }
        return filterValue ? 1 : 0
      }

      return {
        hasActiveFilters,
        getFilterCount,
      }
    },
  }
</script>

<style scoped>
  .filter-tabs {
    border-bottom: 2px solid var(--border-default);
    margin-bottom: 1rem;
  }

  .tab-list {
    display: flex;
    gap: 0;
    overflow-x: auto;
  }

  .tab-button {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1rem;
    border: none;
    border-bottom: 3px solid transparent;
    background: transparent;
    color: var(--text-muted);
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    white-space: nowrap;
    position: relative;
  }

  .tab-button:hover {
    color: var(--text-primary);
    background: var(--bg-light);
  }

  .tab-button.active {
    color: var(--primary-color);
    border-bottom-color: var(--primary-color);
    background: var(--primary-alpha-05);
  }

  .tab-button.has-filters {
    color: var(--primary-dark);
    font-weight: 600;
  }

  .tab-button.has-filters:not(.active) {
    background: var(--primary-alpha-10);
  }

  .tab-label {
    flex: 1;
  }

  .filter-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 1.5rem;
    height: 1.5rem;
    padding: 0 0.375rem;
    background: var(--primary-color);
    color: white;
    font-size: 0.75rem;
    font-weight: 600;
    border-radius: 0.75rem;
  }

  .tab-button.active .filter-badge {
    background: var(--primary-dark);
  }

  /* Scrollbar styling for tabs */
  .tab-list::-webkit-scrollbar {
    height: 3px;
  }

  .tab-list::-webkit-scrollbar-track {
    background: var(--bg-light);
  }

  .tab-list::-webkit-scrollbar-thumb {
    background: var(--border-default);
    border-radius: 1.5px;
  }

  .tab-list::-webkit-scrollbar-thumb:hover {
    background: var(--text-muted);
  }
</style>
