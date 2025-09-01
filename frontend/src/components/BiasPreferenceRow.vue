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
        min="-5"
        max="5"
        step="1"
        class="bias-slider"
        @input="onSliderChange"
      />
      <span class="bias-value">{{ formatDCValue(sliderValue) }}</span>
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

      const formatDCValue = (value) => {
        const sign = value >= 0 ? '+' : ''
        return `${sign}${value}`
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
        formatDCValue,
      }
    },
  }
</script>

<style scoped>
  /* All BiasPreferenceRow styles now use shared classes from components.css */
</style>
