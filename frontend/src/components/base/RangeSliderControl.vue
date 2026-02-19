<template>
  <div class="threshold-slider">
    <label class="threshold-label">{{ resolvedLabel }}</label>
    <input
      type="range"
      :value="modelValue"
      :min="min"
      :max="max"
      :step="step"
      class="slider"
      @input="handleInput"
    />
  </div>
</template>

<script setup>
  import { computed } from 'vue'

  const props = defineProps({
    label: {
      type: String,
      required: true,
    },
    modelValue: {
      type: Number,
      required: true,
    },
    min: {
      type: Number,
      required: true,
    },
    max: {
      type: Number,
      required: true,
    },
    step: {
      type: Number,
      default: 1,
    },
    formatter: {
      type: Function,
      default: null,
    },
  })

  const emit = defineEmits(['update:modelValue'])

  const resolvedLabel = computed(() => {
    const valueText = props.formatter ? props.formatter(props.modelValue) : String(props.modelValue)
    return `${props.label}: ${valueText}`
  })

  const handleInput = (event) => {
    emit('update:modelValue', Number(event.target.value))
  }
</script>

<style scoped>
  .threshold-slider {
    margin-bottom: var(--spacing-md);
  }

  .threshold-label {
    display: block;
    margin-bottom: var(--spacing-sm);
    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-medium);
    color: var(--text-secondary);
  }

  .slider {
    width: 100%;
    height: 6px;
    border-radius: 3px;
    outline: none;
    cursor: pointer;
    -webkit-appearance: none;
    appearance: none;
    background: var(--border-default);
  }

  .slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: var(--primary-color);
    cursor: pointer;
    border: 2px solid var(--bg-white);
    box-shadow: var(--shadow-sm);
  }

  .slider::-moz-range-thumb {
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: var(--primary-color);
    cursor: pointer;
    border: 2px solid var(--bg-white);
    box-shadow: var(--shadow-sm);
  }
</style>
