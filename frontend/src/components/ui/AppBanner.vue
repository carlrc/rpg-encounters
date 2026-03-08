<template>
  <div class="brand-section">
    <img :src="logoUrl" alt="RPG Encounters Logo" class="logo" />
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
    font-size: clamp(1rem, 4vw, 1.35rem);
    font-weight: 600;
    color: var(--color-text-primary);
    margin: 0;
    min-width: 0;
    max-width: 100%;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
</style>
