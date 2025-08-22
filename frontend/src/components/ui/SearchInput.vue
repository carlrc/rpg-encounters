<template>
  <div class="search-container">
    <div class="search-input-wrapper">
      <input
        v-model="searchQuery"
        type="text"
        :placeholder="placeholder"
        class="shared-input search-input"
        @input="$emit('search', searchQuery)"
      />
      <button
        v-if="searchQuery"
        @click="clearSearch"
        class="search-clear-btn"
        type="button"
        title="Clear search"
      >
        ×
      </button>
    </div>
  </div>
</template>

<script>
  import { ref } from 'vue'

  export default {
    name: 'SearchInput',
    props: {
      placeholder: {
        type: String,
        default: 'Search...',
      },
    },
    emits: ['search'],
    setup(props, { emit }) {
      const searchQuery = ref('')

      const clearSearch = () => {
        searchQuery.value = ''
        emit('search', '')
      }

      return {
        searchQuery,
        clearSearch,
      }
    },
  }
</script>

<style scoped>
  .search-container {
    padding: var(--spacing-md) var(--spacing-lg);
    border-bottom: 1px solid var(--border-default);
    background: white;
  }

  .search-input-wrapper {
    position: relative;
    display: flex;
    align-items: center;
  }

  .search-input {
    width: 100%;
    padding-right: 2.5rem; /* Make room for clear button */
    font-size: var(--font-size-base);
    margin: 0;
  }

  .search-clear-btn {
    position: absolute;
    right: var(--spacing-sm);
    top: 50%;
    transform: translateY(-50%);
    background: none;
    border: none;
    font-size: 1.2em;
    color: var(--text-muted);
    cursor: pointer;
    padding: var(--spacing-xs);
    border-radius: var(--radius-round);
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all var(--transition-fast);
  }

  .search-clear-btn:hover {
    background: var(--bg-light);
    color: var(--text-secondary);
    transform: translateY(-50%) scale(1.1);
  }

  .search-clear-btn:active {
    transform: translateY(-50%) scale(0.95);
  }
</style>
