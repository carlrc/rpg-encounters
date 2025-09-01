<template>
  <div v-if="enableLevel1 || enableLevel2 || enableLevel3" class="threshold-manager">
    <!-- Level 1 Threshold -->
    <div v-if="enableLevel1" class="threshold-section">
      <div class="threshold-slider">
        <label class="threshold-label">
          Standard Content: {{ getDCLabel(standardThreshold) || `DC ${standardThreshold}` }}
        </label>
        <input
          type="range"
          :value="standardThreshold"
          @input="$emit('update:standardThreshold', parseInt($event.target.value))"
          :min="gameData.threshold_limits.min"
          :max="gameData.threshold_limits.max"
          :step="gameData.threshold_limits.step"
          class="slider"
        />
      </div>
    </div>

    <!-- Level 2 Threshold -->
    <div v-if="enableLevel2" class="threshold-section">
      <div class="threshold-slider">
        <label class="threshold-label">
          Privileged Content: {{ getDCLabel(privilegedThreshold) || `DC ${privilegedThreshold}` }}
        </label>
        <input
          type="range"
          :value="privilegedThreshold"
          @input="$emit('update:privilegedThreshold', parseInt($event.target.value))"
          :min="gameData.threshold_limits.min"
          :max="gameData.threshold_limits.max"
          :step="gameData.threshold_limits.step"
          class="slider"
        />
      </div>
    </div>

    <!-- Level 3 Threshold -->
    <div v-if="enableLevel3" class="threshold-section">
      <div class="threshold-slider">
        <label class="threshold-label">
          Exclusive Content: {{ getDCLabel(exclusiveThreshold) || `DC ${exclusiveThreshold}` }}
        </label>
        <input
          type="range"
          :value="exclusiveThreshold"
          @input="$emit('update:exclusiveThreshold', parseInt($event.target.value))"
          :min="gameData.threshold_limits.min"
          :max="gameData.threshold_limits.max"
          :step="gameData.threshold_limits.step"
          class="slider"
        />
      </div>
    </div>
  </div>
</template>

<script>
  import { storeToRefs } from 'pinia'
  import { useGameDataStore } from '../../stores/gameData.js'
  import { getDCLabel } from '../../utils/dcUtils.js'

  export default {
    name: 'ThresholdManager',
    props: {
      enableLevel1: Boolean,
      enableLevel2: Boolean,
      enableLevel3: Boolean,
      standardThreshold: {
        type: Number,
        required: true,
      },
      privilegedThreshold: {
        type: Number,
        required: true,
      },
      exclusiveThreshold: {
        type: Number,
        required: true,
      },
    },
    emits: ['update:standardThreshold', 'update:privilegedThreshold', 'update:exclusiveThreshold'],
    setup() {
      const gameDataStore = useGameDataStore()
      const { data: gameData } = storeToRefs(gameDataStore)

      return {
        gameData,
        getDCLabel: (value) => getDCLabel(value, gameData.value?.difficulty_classes),
      }
    },
  }
</script>

<style scoped>
  .threshold-manager {
    margin: var(--spacing-lg) 0;
  }

  .threshold-section {
    margin-bottom: var(--spacing-xl);
  }

  .threshold-slider {
    margin-bottom: var(--spacing-lg);
  }

  .threshold-slider:last-child {
    margin-bottom: 0;
  }

  .threshold-label {
    display: block;
    margin-bottom: var(--spacing-sm);
    font-weight: var(--font-weight-medium);
    color: var(--text-secondary);
    font-size: var(--font-size-base);
  }

  .slider {
    width: 100%;
    height: 6px;
    border-radius: 3px;
    background: var(--border-default);
    outline: none;
    -webkit-appearance: none;
  }

  .slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 20px;
    height: 20px;
    border-radius: var(--radius-round);
    background: var(--primary-color);
    cursor: pointer;
  }

  .slider::-moz-range-thumb {
    width: 20px;
    height: 20px;
    border-radius: var(--radius-round);
    background: var(--primary-color);
    cursor: pointer;
    border: none;
  }
</style>
