<template>
  <div class="traits-display-grid">
    <div v-for="(values, category) in traits" :key="category" class="trait-category-display">
      <div class="trait-category-title">{{ formatCategoryName(category) }}</div>
      <div class="trait-values-list">
        <span
          v-for="(value, name) in values"
          :key="name"
          class="trait-value-item"
          :class="getValueClass(value, category)"
        >
          {{ name }}: {{ formatValue(value) }}
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
    },
    setup(props) {
      const formatCategoryName = (category) => {
        return props.categoryNames[category] || category
      }

      const formatValue = (value) => {
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
  .traits-display-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    margin-top: 1rem;
    width: 100%;
    max-width: 100%;
    box-sizing: border-box;
  }

  .trait-category-display {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: 0.75rem;
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
    margin-bottom: 0.5rem;
    font-size: var(--font-size-sm);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    white-space: nowrap;
  }

  .trait-values-list {
    display: flex;
    flex-wrap: wrap;
    gap: 0.25rem;
    justify-content: center;
    width: 100%;
    max-width: 100%;
  }

  .trait-value-item {
    display: inline-block;
    padding: 0.2rem 0.4rem;
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
    background-color: #d4edda;
    border-color: #c3e6cb;
    color: #155724;
  }

  .trait-value-item.trait-negative,
  .trait-value-item.bias-negative {
    background-color: #f8d7da;
    border-color: #f5c6cb;
    color: #721c24;
  }

  .trait-value-item.trait-neutral,
  .trait-value-item.bias-neutral {
    background-color: #e2e3e5;
    border-color: #d6d8db;
    color: #383d41;
  }

  @media (max-width: 768px) {
    .traits-display-grid {
      grid-template-columns: 1fr;
      gap: 0.75rem;
    }

    .trait-category-display {
      padding: 0.5rem;
      min-height: 60px;
    }

    .trait-value-item {
      font-size: var(--font-size-xs);
      padding: 0.15rem 0.3rem;
    }
  }
</style>
