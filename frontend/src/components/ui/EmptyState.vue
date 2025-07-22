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
  .empty-detail-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: #6c757d;
    text-align: center;
    padding: 40px;
  }

  .empty-icon {
    font-size: 4em;
    margin-bottom: 20px;
    opacity: 0.5;
  }

  .empty-detail-state h3 {
    margin: 0 0 12px 0;
    font-size: 1.5em;
    color: #495057;
  }

  .empty-detail-state p {
    margin: 0;
    font-size: 1em;
    line-height: 1.5;
  }
</style>
