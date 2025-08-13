<template>
  <div v-if="enableLevel2 || enableLevel3" class="threshold-manager">
    <!-- Level 2 Threshold -->
    <div v-if="enableLevel2" class="threshold-section">
      <h4 class="threshold-title">Level 2: Privileged Content Threshold</h4>
      <div class="threshold-options">
        <label class="shared-radio-option">
          <input
            type="radio"
            value="default"
            :checked="privilegedMode === 'default'"
            @change="$emit('update:privilegedMode', 'default')"
          />
          <span>Use Default Threshold</span>
        </label>
        <label class="shared-radio-option">
          <input
            type="radio"
            value="custom"
            :checked="privilegedMode === 'custom'"
            @change="$emit('update:privilegedMode', 'custom')"
          />
          <span>Custom Threshold</span>
        </label>
      </div>

      <div v-if="privilegedMode === 'custom'" class="custom-thresholds">
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
    </div>

    <!-- Level 3 Threshold -->
    <div v-if="enableLevel3" class="threshold-section">
      <h4 class="threshold-title">Level 3: Exclusive Content Threshold</h4>
      <div class="threshold-options">
        <label class="shared-radio-option">
          <input
            type="radio"
            value="default"
            :checked="exclusiveMode === 'default'"
            @change="$emit('update:exclusiveMode', 'default')"
          />
          <span>Use Default Threshold</span>
        </label>
        <label class="shared-radio-option">
          <input
            type="radio"
            value="custom"
            :checked="exclusiveMode === 'custom'"
            @change="$emit('update:exclusiveMode', 'custom')"
          />
          <span>Custom Threshold</span>
        </label>
      </div>

      <div v-if="exclusiveMode === 'custom'" class="custom-thresholds">
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
  </div>
</template>

<script>
  import { useGameData } from '../../composables/useGameData.js'

  export default {
    name: 'ThresholdManager',
    props: {
      enableLevel2: Boolean,
      enableLevel3: Boolean,
      privilegedThreshold: {
        type: Number,
        required: true,
      },
      exclusiveThreshold: {
        type: Number,
        required: true,
      },
      privilegedMode: {
        type: String,
        default: 'default',
      },
      exclusiveMode: {
        type: String,
        default: 'default',
      },
    },
    emits: [
      'update:privilegedThreshold',
      'update:exclusiveThreshold',
      'update:privilegedMode',
      'update:exclusiveMode',
    ],
    setup() {
      const { gameData } = useGameData()

      const getDCLabel = (value) => {
        const dcEntries = Object.entries(gameData.value.difficulty_classes)
        const entry = dcEntries.find(([key, dcValue]) => dcValue === value)
        return entry ? `${entry[0].replace(/_/g, ' ')} (${value})` : `DC ${value}`
      }

      return {
        gameData,
        getDCLabel,
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

  .threshold-title {
    margin: 0 0 var(--spacing-md) 0;
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-primary);
  }

  .threshold-options {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
    margin-bottom: var(--spacing-lg);
  }

  .custom-thresholds {
    padding: var(--spacing-lg);
    border: 2px solid var(--border-default);
    border-radius: var(--radius-lg);
    background: var(--bg-light);
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
