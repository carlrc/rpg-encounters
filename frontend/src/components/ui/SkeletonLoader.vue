<template>
  <div class="skeleton-loader" :class="`skeleton-${type}`">
    <div v-if="type === 'card'" class="skeleton-card">
      <div class="skeleton-avatar"></div>
      <div class="skeleton-lines">
        <div class="skeleton-line skeleton-title"></div>
        <div class="skeleton-line"></div>
        <div class="skeleton-line"></div>
        <div class="skeleton-line skeleton-short"></div>
      </div>
    </div>
    <div v-else-if="type === 'list'" class="skeleton-list">
      <div v-for="i in count" :key="i" class="skeleton-list-item">
        <div class="skeleton-line"></div>
      </div>
    </div>
    <div v-else-if="type === 'table'" class="skeleton-table">
      <div class="skeleton-table-header">
        <div v-for="i in 4" :key="`header-${i}`" class="skeleton-line skeleton-header"></div>
      </div>
      <div v-for="i in count" :key="`row-${i}`" class="skeleton-table-row">
        <div v-for="j in 4" :key="`cell-${i}-${j}`" class="skeleton-line"></div>
      </div>
    </div>
    <div v-else-if="type === 'form'" class="skeleton-form">
      <div class="skeleton-avatar"></div>
      <div class="skeleton-line skeleton-input"></div>
      <div class="skeleton-form-row">
        <div class="skeleton-line skeleton-input"></div>
        <div class="skeleton-line skeleton-input"></div>
      </div>
      <div class="skeleton-line skeleton-textarea"></div>
      <div class="skeleton-line skeleton-textarea"></div>
      <div class="skeleton-form-actions">
        <div class="skeleton-line skeleton-button"></div>
        <div class="skeleton-line skeleton-button"></div>
      </div>
    </div>
  </div>
</template>

<script>
  export default {
    name: 'SkeletonLoader',
    props: {
      type: {
        type: String,
        default: 'card',
        validator: (value) => ['card', 'list', 'table', 'form'].includes(value),
      },
      count: {
        type: Number,
        default: 3,
        validator: (value) => value > 0 && value <= 20,
      },
    },
  }
</script>

<style scoped>
  .skeleton-loader {
    animation: pulse 1.5s ease-in-out infinite;
  }

  @keyframes pulse {
    0% {
      opacity: 1;
    }
    50% {
      opacity: 0.6;
    }
    100% {
      opacity: 1;
    }
  }

  .skeleton-line {
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
    border-radius: var(--radius-sm);
    height: 16px;
    margin-bottom: var(--spacing-sm);
  }

  @keyframes shimmer {
    0% {
      background-position: -200% 0;
    }
    100% {
      background-position: 200% 0;
    }
  }

  /* Card skeleton */
  .skeleton-card {
    background: var(--bg-white);
    border-radius: var(--radius-xl);
    padding: var(--spacing-xxl);
    box-shadow: var(--shadow-card);
    border: 1px solid var(--border-light);
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--spacing-lg);
  }

  .skeleton-avatar {
    width: 100px;
    height: 80px;
    border-radius: var(--radius-lg);
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
    margin-bottom: var(--spacing-lg);
  }

  .skeleton-lines {
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
  }

  .skeleton-title {
    height: 24px;
    width: 60%;
    margin: 0 auto var(--spacing-lg) auto;
  }

  .skeleton-short {
    width: 40%;
  }

  /* List skeleton */
  .skeleton-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
  }

  .skeleton-list-item {
    padding: var(--spacing-lg);
    background: var(--bg-white);
    border-radius: var(--radius-lg);
    border: 1px solid var(--border-light);
  }

  /* Table skeleton */
  .skeleton-table {
    background: var(--bg-white);
    border-radius: var(--radius-lg);
    border: 1px solid var(--border-light);
    overflow: hidden;
  }

  .skeleton-table-header {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: var(--spacing-md);
    padding: var(--spacing-lg);
    background: var(--bg-light);
    border-bottom: 1px solid var(--border-light);
  }

  .skeleton-table-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: var(--spacing-md);
    padding: var(--spacing-lg);
    border-bottom: 1px solid var(--border-light);
  }

  .skeleton-table-row:last-child {
    border-bottom: none;
  }

  .skeleton-header {
    height: 20px;
    background: linear-gradient(90deg, #e0e0e0 25%, #d0d0d0 50%, #e0e0e0 75%);
  }

  /* Form skeleton */
  .skeleton-form {
    background: var(--bg-white);
    border-radius: var(--radius-xl);
    padding: var(--spacing-xxl);
    box-shadow: var(--shadow-card);
    border: 1px solid var(--border-light);
    display: flex;
    flex-direction: column;
    gap: var(--spacing-lg);
  }

  .skeleton-form .skeleton-avatar {
    align-self: center;
  }

  .skeleton-input {
    height: 40px;
  }

  .skeleton-textarea {
    height: 80px;
  }

  .skeleton-form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--spacing-lg);
  }

  .skeleton-form-actions {
    display: flex;
    gap: var(--spacing-md);
    justify-content: center;
    padding-top: var(--spacing-lg);
    border-top: 2px solid var(--border-default);
  }

  .skeleton-button {
    height: 40px;
    width: 80px;
    border-radius: var(--radius-lg);
  }

  /* Responsive design */
  @media (max-width: 768px) {
    .skeleton-form-row {
      grid-template-columns: 1fr;
    }

    .skeleton-table-header,
    .skeleton-table-row {
      grid-template-columns: 1fr;
    }

    .skeleton-form-actions {
      flex-direction: column;
    }

    .skeleton-button {
      width: 100%;
    }
  }

  /* Accessibility */
  @media (prefers-reduced-motion: reduce) {
    .skeleton-loader,
    .skeleton-line,
    .skeleton-avatar {
      animation: none;
    }

    .skeleton-line,
    .skeleton-avatar {
      background: #f0f0f0;
    }
  }
</style>
