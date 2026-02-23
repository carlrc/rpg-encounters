<template>
  <div class="traits-display-grid">
    <div v-for="(values, category) in traits" :key="category" class="trait-category-display">
      <div v-if="showCategoryTitle" class="trait-category-title">
        {{ formatCategoryName(category) }}
      </div>
      <div class="trait-values-list">
        <span
          v-for="(value, name) in values"
          :key="name"
          class="trait-value-item"
          :class="getValueClass(value, category)"
        >
          {{ showTraitNames ? `${name}: ${formatValue(value)}` : formatValue(value) }}
        </span>
      </div>
    </div>
  </div>
</template>

<script>
  export default {
    name: 'TraitsDisplay',
    props: {
      traits: {
        type: Object,
        required: true,
      },
      categoryNames: {
        type: Object,
        default: () => ({}),
      },
      valueClassifier: {
        type: Function,
        default: null,
      },
      valueFormatter: {
        type: Function,
        default: null,
      },
      showCategoryTitle: {
        type: Boolean,
        default: true,
      },
      showTraitNames: {
        type: Boolean,
        default: true,
      },
    },
    setup(props) {
      const formatCategoryName = (category) => {
        return props.categoryNames[category] || category
      }

      const formatValue = (value) => {
        if (props.valueFormatter) {
          return props.valueFormatter(value)
        }
        const sign = value >= 0 ? '+' : ''
        return `${sign}${value}`
      }

      const getValueClass = (value, category) => {
        if (props.valueClassifier) {
          return props.valueClassifier(value, category)
        }

        // Default classification
        if (value > 0) return 'trait-positive'
        if (value < 0) return 'trait-negative'
        return 'trait-neutral'
      }

      return {
        formatCategoryName,
        formatValue,
        getValueClass,
      }
    },
  }
</script>

<style scoped>
  /* Component-specific styles only - shared styles handled globally */
  .traits-display-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--spacing-lg);
    margin-top: var(--spacing-lg);
    width: 100%;
    max-width: 100%;
    box-sizing: border-box;
  }

  .trait-category-display {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: var(--spacing-md);
    background: var(--bg-light);
    border-radius: var(--radius-lg);
    border: 1px solid var(--border-default);
    min-height: 80px;
    box-sizing: border-box;
    overflow: hidden;
  }

  .trait-category-title {
    font-weight: var(--font-weight-semibold);
    color: var(--text-secondary);
    margin-bottom: var(--spacing-sm);
    font-size: var(--font-size-sm);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    white-space: nowrap;
  }

  .trait-values-list {
    display: flex;
    flex-wrap: wrap;
    gap: var(--spacing-xs);
    justify-content: center;
    width: 100%;
    max-width: 100%;
  }

  .trait-value-item {
    display: inline-block;
    padding: var(--spacing-xs);
    border-radius: var(--radius-sm);
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-medium);
    border: 1px solid;
    white-space: nowrap;
    max-width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
    box-sizing: border-box;
  }

  .trait-value-item.trait-positive,
  .trait-value-item.bias-positive {
    background-color: var(--color-bias-positive-bg);
    border-color: var(--color-bias-positive-border);
    color: var(--color-bias-positive-text);
  }

  .trait-value-item.trait-negative,
  .trait-value-item.bias-negative {
    background-color: var(--color-bias-negative-bg);
    border-color: var(--color-bias-negative-border);
    color: var(--color-bias-negative-text);
  }

  .trait-value-item.trait-neutral,
  .trait-value-item.bias-neutral {
    background-color: var(--color-bias-neutral-bg);
    border-color: var(--color-bias-neutral-border);
    color: var(--color-bias-neutral-text);
  }

  @media (max-width: 768px) {
    .traits-display-grid {
      grid-template-columns: 1fr;
      gap: var(--spacing-md);
    }

    .trait-category-display {
      padding: var(--spacing-sm);
      min-height: 60px;
    }

    .trait-value-item {
      font-size: var(--font-size-xs);
      padding: var(--spacing-xs);
    }
  }
</style>
