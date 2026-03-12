<template>
  <div class="brand-section">
    <img :src="logoUrl" alt="RPG Encounters Logo" width="579" height="672" class="logo" />
    <h1 class="brand-title">RPG Encounters</h1>
  </div>
</template>

<script setup>
  import logoUrl from '../../assets/images/logo.png'
</script>

<style scoped>
  .brand-section {
    display: flex;
    align-items: center;
    gap: clamp(8px, 3vw, var(--spacing-lg));
    min-width: 0;
    max-width: 100%;
  }

  .logo {
    height: clamp(32px, 6vw, 50px);
    width: auto;
    flex-shrink: 0;
  }

  .brand-title {
    font-size: clamp(0.95rem, 2.4vw, 1.1rem);
    font-weight: 600;
    color: var(--dev-text-primary);
    margin: 0;
    min-width: 0;
    max-width: 100%;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
</style>
