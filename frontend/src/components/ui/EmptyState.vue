<template>
  <div class="empty-detail-state">
    <div class="empty-icon">{{ icon }}</div>
    <h3>{{ title }}</h3>
    <p>{{ message }}</p>
  </div>
</template>

<script>
  export default {
    name: 'EmptyState',
    props: {
      icon: {
        type: String,
        default: '📄',
      },
      title: {
        type: String,
        required: true,
      },
      message: {
        type: String,
        required: true,
      },
    },
  }
</script>

<style scoped>
  /* Component-specific styles only - shared styles handled globally */
  .empty-detail-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: var(--text-muted);
    text-align: center;
    padding: 40px;
  }

  .empty-icon {
    font-size: 4em;
    margin-bottom: var(--spacing-xl);
    opacity: 0.5;
  }

  .empty-detail-state h3 {
    margin: 0 0 var(--spacing-md) 0;
    font-size: var(--font-size-xl);
    color: var(--text-secondary);
  }

  .empty-detail-state p {
    margin: 0;
    font-size: var(--font-size-base);
    line-height: 1.5;
  }
</style>
