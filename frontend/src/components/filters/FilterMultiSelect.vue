<template>
  <div class="filter-multiselect">
    <label v-if="label" class="filter-label">{{ label }}</label>
    <div class="multiselect-wrapper" ref="wrapperRef">
      <button
        @click="toggleDropdown"
        class="multiselect-trigger"
        :class="{ 'has-selection': selectedItems.length > 0, 'is-open': isOpen }"
        type="button"
      >
        <span class="trigger-text">
          {{ displayText }}
        </span>
        <span class="trigger-arrow" :class="{ 'is-open': isOpen }">▼</span>
      </button>

      <div v-if="isOpen" class="multiselect-dropdown">
        <div class="dropdown-header">
          <button
            @click="selectAll"
            class="header-btn"
            type="button"
            :disabled="selectedItems.length === options.length"
          >
            Select All
          </button>
          <button
            @click="clearAll"
            class="header-btn"
            type="button"
            :disabled="selectedItems.length === 0"
          >
            Clear
          </button>
        </div>

        <div class="options-list">
          <label v-for="option in options" :key="option" class="option-item">
            <input
              type="checkbox"
              :value="option"
              :checked="selectedItems.includes(option)"
              @change="toggleOption(option)"
            />
            <span class="option-text">{{ option }}</span>
          </label>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import { ref, computed, onMounted, onUnmounted } from 'vue'

  export default {
    name: 'FilterMultiSelect',
    props: {
      label: {
        type: String,
        default: '',
      },
      options: {
        type: Array,
        required: true,
      },
      modelValue: {
        type: Array,
        default: () => [],
      },
      placeholder: {
        type: String,
        default: 'Select options',
      },
    },
    emits: ['update:modelValue'],
    setup(props, { emit }) {
      const isOpen = ref(false)
      const wrapperRef = ref(null)

      const selectedItems = computed(() => props.modelValue || [])

      const displayText = computed(() => {
        if (selectedItems.value.length === 0) {
          return props.placeholder
        }
        if (selectedItems.value.length === 1) {
          return selectedItems.value[0]
        }
        if (selectedItems.value.length === props.options.length) {
          return 'All selected'
        }
        return `${selectedItems.value.length} selected`
      })

      const toggleDropdown = () => {
        isOpen.value = !isOpen.value
      }

      const toggleOption = (option) => {
        const newSelection = [...selectedItems.value]
        const index = newSelection.indexOf(option)

        if (index > -1) {
          newSelection.splice(index, 1)
        } else {
          newSelection.push(option)
        }

        emit('update:modelValue', newSelection)
      }

      const selectAll = () => {
        emit('update:modelValue', [...props.options])
      }

      const clearAll = () => {
        emit('update:modelValue', [])
      }

      const handleClickOutside = (event) => {
        if (wrapperRef.value && !wrapperRef.value.contains(event.target)) {
          isOpen.value = false
        }
      }

      onMounted(() => {
        document.addEventListener('click', handleClickOutside)
      })

      onUnmounted(() => {
        document.removeEventListener('click', handleClickOutside)
      })

      return {
        isOpen,
        wrapperRef,
        selectedItems,
        displayText,
        toggleDropdown,
        toggleOption,
        selectAll,
        clearAll,
      }
    },
  }
</script>

<style scoped>
  .filter-multiselect {
    position: relative;
    min-width: 200px;
  }

  .filter-label {
    display: block;
    font-size: 0.875rem;
    font-weight: 500;
    color: #374151;
    margin-bottom: 0.5rem;
  }

  .multiselect-wrapper {
    position: relative;
  }

  .multiselect-trigger {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    padding: 0.5rem 0.75rem;
    border: 2px solid #d1d5db;
    border-radius: 0.5rem;
    background: white;
    font-size: 0.875rem;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .multiselect-trigger:hover {
    border-color: #9ca3af;
  }

  .multiselect-trigger.has-selection {
    border-color: #3b82f6;
    background: #eff6ff;
  }

  .multiselect-trigger.is-open {
    border-color: #3b82f6;
    border-bottom-left-radius: 0;
    border-bottom-right-radius: 0;
  }

  .trigger-text {
    flex: 1;
    text-align: left;
    color: #374151;
  }

  .trigger-arrow {
    margin-left: 0.5rem;
    transition: transform 0.2s ease;
    color: #6b7280;
  }

  .trigger-arrow.is-open {
    transform: rotate(180deg);
  }

  .multiselect-dropdown {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    border: 2px solid #3b82f6;
    border-top: none;
    border-radius: 0 0 0.5rem 0.5rem;
    background: white;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    z-index: 1000;
    max-height: 250px;
    overflow: hidden;
  }

  .dropdown-header {
    display: flex;
    padding: 0.5rem;
    border-bottom: 1px solid #e5e7eb;
    background: #f9fafb;
  }

  .header-btn {
    flex: 1;
    padding: 0.25rem 0.5rem;
    border: 1px solid #d1d5db;
    border-radius: 0.25rem;
    background: white;
    font-size: 0.75rem;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .header-btn:first-child {
    margin-right: 0.25rem;
  }

  .header-btn:hover:not(:disabled) {
    background: #f3f4f6;
    border-color: #9ca3af;
  }

  .header-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .options-list {
    max-height: 180px;
    overflow-y: auto;
  }

  .option-item {
    display: flex;
    align-items: center;
    padding: 0.5rem 0.75rem;
    cursor: pointer;
    transition: background-color 0.2s ease;
  }

  .option-item:hover {
    background: #f3f4f6;
  }

  .option-item input[type='checkbox'] {
    margin-right: 0.5rem;
    transform: scale(0.9);
  }

  .option-text {
    font-size: 0.875rem;
    color: #374151;
  }

  /* Scrollbar styling */
  .options-list::-webkit-scrollbar {
    width: 6px;
  }

  .options-list::-webkit-scrollbar-track {
    background: #f1f1f1;
  }

  .options-list::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 3px;
  }

  .options-list::-webkit-scrollbar-thumb:hover {
    background: #a8a8a8;
  }
</style>
