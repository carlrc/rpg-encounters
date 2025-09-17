<template>
  <div :class="['filter-multiselect', { expanded }]">
    <label v-if="label" class="filter-label">{{ label }}</label>
    <div v-if="expanded" class="expanded-panel">
      <div class="dropdown-header">
        <button
          v-if="showSelectAll"
          @click="selectAll"
          class="header-btn"
          type="button"
          :disabled="disableSelectAll"
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
        <label
          v-for="(option, index) in normalizedOptions"
          :key="optionKey(option, index)"
          class="option-item"
        >
          <input
            type="checkbox"
            :value="option.value"
            :checked="isSelected(option.value)"
            @change="toggleOption(option.value)"
          />
          <span class="option-text">{{ option.label }}</span>
        </label>
      </div>
    </div>
    <div v-else class="multiselect-wrapper" ref="wrapperRef">
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
            v-if="showSelectAll"
            @click="selectAll"
            class="header-btn"
            type="button"
            :disabled="disableSelectAll"
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
          <label
            v-for="(option, index) in normalizedOptions"
            :key="optionKey(option, index)"
            class="option-item"
          >
            <input
              type="checkbox"
              :value="option.value"
              :checked="isSelected(option.value)"
              @change="toggleOption(option.value)"
            />
            <span class="option-text">{{ option.label }}</span>
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
      expanded: {
        type: Boolean,
        default: false,
      },
      optionLabelKey: {
        type: String,
        default: 'label',
      },
      optionValueKey: {
        type: String,
        default: 'value',
      },
      excludeFromSelectAllKey: {
        type: String,
        default: 'excludeFromSelectAll',
      },
      showSelectAll: {
        type: Boolean,
        default: true,
      },
    },
    emits: ['update:modelValue'],
    setup(props, { emit }) {
      const isOpen = ref(false)
      const wrapperRef = ref(null)

      const normalizeValue = (value) => {
        if (typeof value === 'number') return value
        if (typeof value === 'string') {
          const parsed = Number(value)
          return Number.isNaN(parsed) ? value : parsed
        }
        return value
      }

      const normalizedOptions = computed(() => {
        return (props.options || []).map((option, index) => {
          if (option && typeof option === 'object' && !Array.isArray(option)) {
            const label = option[props.optionLabelKey]
            const value = option[props.optionValueKey]
            const exclude = Boolean(option[props.excludeFromSelectAllKey])
            return {
              label: typeof label === 'undefined' ? String(value ?? '') : String(label),
              value: typeof value === 'undefined' ? index : value,
              excludeFromSelectAll: exclude,
            }
          }

          const label = option
          return {
            label: String(label),
            value: option,
            excludeFromSelectAll: false,
          }
        })
      })

      const selectedItems = computed(() => props.modelValue || [])

      const selectableOptions = computed(() =>
        normalizedOptions.value.filter((option) => !option.excludeFromSelectAll)
      )

      const labelMap = computed(() => {
        const map = new Map()
        normalizedOptions.value.forEach((option) => {
          map.set(normalizeValue(option.value), option.label)
        })
        return map
      })

      const isSelected = (value) => {
        return selectedItems.value.some((item) => normalizeValue(item) === normalizeValue(value))
      }

      const displayText = computed(() => {
        if (selectedItems.value.length === 0) {
          return props.placeholder
        }

        if (selectedItems.value.length === 1) {
          const first = normalizeValue(selectedItems.value[0])
          return labelMap.value.get(first) ?? props.placeholder
        }

        if (
          selectableOptions.value.length > 0 &&
          selectableOptions.value.every((option) => isSelected(option.value))
        ) {
          return 'All selected'
        }

        return `${selectedItems.value.length} selected`
      })

      const toggleDropdown = () => {
        isOpen.value = !isOpen.value
      }

      const toggleOption = (option) => {
        const newSelection = [...selectedItems.value]
        const index = newSelection.findIndex(
          (item) => normalizeValue(item) === normalizeValue(option)
        )

        if (index > -1) {
          newSelection.splice(index, 1)
        } else {
          newSelection.push(option)
        }

        emit('update:modelValue', newSelection)
      }

      const selectAll = () => {
        if (selectableOptions.value.length === 0) return
        const values = selectableOptions.value.map((option) => option.value)
        emit('update:modelValue', values)
      }

      const clearAll = () => {
        emit('update:modelValue', [])
      }

      const disableSelectAll = computed(() => {
        if (!props.showSelectAll) return true
        if (selectableOptions.value.length === 0) return true
        return selectableOptions.value.every((option) => isSelected(option.value))
      })

      const optionKey = (option, index) => {
        const key = option.value ?? index
        return `${String(key)}-${index}`
      }

      const handleClickOutside = (event) => {
        if (wrapperRef.value && !wrapperRef.value.contains(event.target)) {
          isOpen.value = false
        }
      }

      onMounted(() => {
        if (!props.expanded) {
          document.addEventListener('click', handleClickOutside)
        }
      })

      onUnmounted(() => {
        if (!props.expanded) {
          document.removeEventListener('click', handleClickOutside)
        }
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
        normalizedOptions,
        optionKey,
        isSelected,
        disableSelectAll,
      }
    },
  }
</script>

<style scoped>
  .filter-multiselect {
    position: relative;
    min-width: 200px;
  }

  .filter-multiselect.expanded {
    width: 100%;
    min-width: unset;
  }

  .filter-label {
    display: block;
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--text-primary);
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
    border: 2px solid var(--border-default);
    border-radius: 0.5rem;
    background: var(--bg-white);
    font-size: 0.875rem;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .multiselect-trigger:hover {
    border-color: var(--text-muted);
  }

  .multiselect-trigger.has-selection {
    border-color: var(--primary-color);
    background: var(--primary-alpha-05);
  }

  .multiselect-trigger.is-open {
    border-color: var(--primary-color);
    border-bottom-left-radius: 0;
    border-bottom-right-radius: 0;
  }

  .trigger-text {
    flex: 1;
    text-align: left;
    color: var(--text-primary);
  }

  .trigger-arrow {
    margin-left: 0.5rem;
    transition: transform 0.2s ease;
    color: var(--text-muted);
  }

  .trigger-arrow.is-open {
    transform: rotate(180deg);
  }

  .multiselect-dropdown {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    border: 2px solid var(--primary-color);
    border-top: none;
    border-radius: 0 0 0.5rem 0.5rem;
    background: var(--bg-white);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    z-index: 1000;
    max-height: 250px;
    overflow: hidden;
  }

  .filter-multiselect.expanded .expanded-panel {
    border: 1px solid var(--border-default);
    border-radius: var(--radius-lg);
    background: var(--bg-white);
    display: flex;
    flex-direction: column;
    padding: var(--spacing-sm);
    gap: var(--spacing-sm);
  }

  .dropdown-header {
    display: flex;
    padding: 0.5rem;
    border-bottom: 1px solid var(--border-default);
    background: var(--bg-light);
  }

  .filter-multiselect.expanded .dropdown-header {
    border-radius: var(--radius-md);
    background: var(--bg-white);
  }

  .header-btn {
    flex: 1;
    padding: 0.25rem 0.5rem;
    border: 1px solid var(--border-default);
    border-radius: 0.25rem;
    background: var(--bg-white);
    font-size: 0.75rem;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .header-btn:first-child {
    margin-right: 0.25rem;
  }

  .header-btn:hover:not(:disabled) {
    background: var(--bg-light);
    border-color: var(--text-muted);
  }

  .header-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .options-list {
    max-height: 180px;
    overflow-y: auto;
  }

  .filter-multiselect.expanded .options-list {
    max-height: none;
    padding: 0.25rem 0.5rem;
    background: var(--bg-white);
    border-radius: var(--radius-md);
    overflow-y: visible;
  }

  .option-item {
    display: flex;
    align-items: center;
    padding: 0.5rem 0.75rem;
    cursor: pointer;
    transition: background-color 0.2s ease;
  }

  .option-item:hover {
    background: var(--bg-light);
  }

  .option-item input[type='checkbox'] {
    margin-right: 0.5rem;
    transform: scale(0.9);
  }

  .option-text {
    font-size: 0.875rem;
    color: var(--text-primary);
  }

  /* Scrollbar styling */
  .options-list::-webkit-scrollbar {
    width: 6px;
  }

  .options-list::-webkit-scrollbar-track {
    background: var(--bg-light);
  }

  .options-list::-webkit-scrollbar-thumb {
    background: var(--border-default);
    border-radius: 3px;
  }

  .options-list::-webkit-scrollbar-thumb:hover {
    background: var(--text-muted);
  }
</style>
