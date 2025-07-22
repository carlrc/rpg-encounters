<template>
  <div class="bias-preference-row">
    <select v-model="selectedOption" @change="onOptionChange" class="bias-dropdown">
      <option value="">{{ placeholder }}</option>
      <option v-for="option in availableOptions" :key="option" :value="option">
        {{ option }}
      </option>
    </select>

    <div
      v-if="selectedOption && !selectedOption.startsWith('__temp_')"
      class="bias-slider-container"
    >
      <input
        type="range"
        v-model.number="sliderValue"
        min="-0.3"
        max="0.3"
        step="0.1"
        class="bias-slider"
        @input="onSliderChange"
      />
      <span class="bias-value">{{ sliderValue.toFixed(1) }}</span>
      <button @click="onRemove" class="bias-remove-btn" type="button">×</button>
    </div>
  </div>
</template>

<script>
  import { ref, computed, watch } from 'vue'

  export default {
    name: 'BiasPreferenceRow',
    props: {
      options: {
        type: Array,
        required: true,
      },
      usedOptions: {
        type: Array,
        default: () => [],
      },
      placeholder: {
        type: String,
        default: 'Select option',
      },
      initialOption: {
        type: String,
        default: '',
      },
      initialValue: {
        type: Number,
        default: 0.0,
      },
    },
    emits: ['change', 'remove'],
    setup(props, { emit }) {
      // Don't show temporary keys in the dropdown initially
      const selectedOption = ref(
        props.initialOption && props.initialOption.startsWith('__temp_') ? '' : props.initialOption
      )
      const sliderValue = ref(props.initialValue)

      const availableOptions = computed(() => {
        return props.options.filter(
          (option) => !props.usedOptions.includes(option) || option === selectedOption.value
        )
      })

      const onOptionChange = () => {
        if (selectedOption.value) {
          // If this was a temporary key, we need to remove it first
          if (props.initialOption && props.initialOption.startsWith('__temp_')) {
            emit('remove', props.initialOption)
          }
          emit('change', selectedOption.value, sliderValue.value)
        }
      }

      const onSliderChange = () => {
        if (selectedOption.value) {
          emit('change', selectedOption.value, sliderValue.value)
        }
      }

      const onRemove = () => {
        emit('remove', selectedOption.value)
      }

      // Watch for changes in initialOption and initialValue (for editing existing preferences)
      watch(
        () => props.initialOption,
        (newVal) => {
          // Don't show temporary keys in the dropdown
          if (newVal && newVal.startsWith('__temp_')) {
            selectedOption.value = ''
          } else {
            selectedOption.value = newVal
          }
        }
      )

      watch(
        () => props.initialValue,
        (newVal) => {
          sliderValue.value = newVal
        }
      )

      return {
        selectedOption,
        sliderValue,
        availableOptions,
        onOptionChange,
        onSliderChange,
        onRemove,
      }
    },
  }
</script>

<style scoped>
  .bias-preference-row {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 0.5rem;
    padding: 0.75rem;
    border: 1px solid #dee2e6;
    border-radius: 4px;
    background: white;
  }

  .bias-dropdown {
    min-width: 150px;
    padding: 0.375rem 0.75rem;
    border: 1px solid #ced4da;
    border-radius: 4px;
    background: white;
    font-size: 0.875rem;
  }

  .bias-slider-container {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex: 1;
  }

  .bias-slider {
    flex: 1;
    max-width: 150px;
  }

  .bias-value {
    font-weight: 600;
    color: #495057;
    min-width: 30px;
    text-align: center;
    font-size: 0.875rem;
  }

  .bias-remove-btn {
    background: #dc3545;
    color: white;
    border: none;
    border-radius: 50%;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    font-size: 16px;
    line-height: 1;
  }

  .bias-remove-btn:hover {
    background: #c82333;
  }
</style>
