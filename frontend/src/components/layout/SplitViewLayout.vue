<template>
  <div class="split-view">
    <!-- Left Pane - Entity List -->
    <div class="list-pane">
      <div class="list-header">
        <h3>{{ listTitle }}</h3>
      </div>

      <!-- Search Input -->
      <SearchInput :placeholder="`Search ${listTitle.toLowerCase()}...`" @search="handleSearch" />

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

        <div v-else-if="filteredItems.length === 0" class="empty-state">
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

  export default {
    name: 'SplitViewLayout',
    components: {
      SearchInput,
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
    },
    emits: ['select-item', 'create-item'],
    setup(props) {
      const searchQuery = ref('')

      const filteredItems = computed(() => {
        if (!searchQuery.value) {
          return props.items
        }

        const query = searchQuery.value.toLowerCase()
        return props.items.filter((item) => {
          const name = item.name || item.title || ''
          const rlName = item.rl_name || ''
          return name.toLowerCase().includes(query) || rlName.toLowerCase().includes(query)
        })
      })

      const handleSearch = (query) => {
        searchQuery.value = query
      }

      return {
        searchQuery,
        filteredItems,
        handleSearch,
      }
    },
  }
</script>

<style scoped>
  .split-view {
    display: flex;
    height: 100%;
    gap: 0;
  }

  .list-pane {
    width: 25%;
    min-width: 250px;
    display: flex;
    flex-direction: column;
    background: #f8f9fa;
    border-right: 2px solid #e9ecef;
  }

  .list-header {
    padding: 20px 16px 16px 16px;
    border-bottom: 1px solid #e9ecef;
    background: white;
  }

  .list-header h3 {
    margin: 0;
    font-size: 1.1em;
    font-weight: 700;
    color: #2c3e50;
    text-align: center;
  }

  .list-content {
    flex: 1;
    overflow-y: auto;
    padding: 8px 0;
  }

  .list-item {
    padding: 12px 16px;
    cursor: pointer;
    transition: all 0.2s ease;
    border-left: 3px solid transparent;
    font-weight: 500;
    color: #495057;
    background: white;
    margin: 2px 8px;
    border-radius: 6px;
    border: 1px solid transparent;
  }

  .list-item:hover {
    background: #e3f2fd;
    color: #1976d2;
    border-color: #bbdefb;
  }

  .list-item.active {
    background: linear-gradient(135deg, #007bff, #0056b3);
    color: white;
    border-left-color: #004085;
    font-weight: 600;
    box-shadow: 0 2px 4px rgba(0, 123, 255, 0.3);
  }

  .list-item.active:hover {
    background: linear-gradient(135deg, #0056b3, #004085);
  }

  .empty-state {
    padding: 40px 16px;
    text-align: center;
    color: #6c757d;
    font-style: italic;
    font-size: 0.9em;
  }

  .list-footer {
    padding: 16px;
    border-top: 1px solid #e9ecef;
    background: white;
  }

  .add-btn {
    width: 100%;
    padding: 12px 16px;
    background: linear-gradient(135deg, #28a745, #218838);
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.9em;
    font-weight: 600;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    box-shadow: 0 2px 4px rgba(40, 167, 69, 0.3);
  }

  .add-btn:hover {
    background: linear-gradient(135deg, #218838, #1e7e34);
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(40, 167, 69, 0.4);
  }

  .plus-icon {
    font-size: 1.2em;
    font-weight: bold;
  }

  .detail-pane {
    flex: 1;
    padding: 20px;
    overflow-y: auto;
    background: #ffffff;
  }

  /* Scrollbar styling for list */
  .list-content::-webkit-scrollbar {
    width: 6px;
  }

  .list-content::-webkit-scrollbar-track {
    background: #f1f1f1;
  }

  .list-content::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 3px;
  }

  .list-content::-webkit-scrollbar-thumb:hover {
    background: #a8a8a8;
  }

  @media (max-width: 768px) {
    .split-view {
      flex-direction: column;
    }

    .list-pane {
      width: 100%;
      min-width: unset;
      max-height: 200px;
    }

    .detail-pane {
      flex: 1;
      padding: 16px;
    }
  }
</style>
