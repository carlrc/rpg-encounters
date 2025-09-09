<template>
  <div class="brand-section">
    <img :src="logoUrl" alt="RPG Encounters Logo" class="logo" />
    <h1 class="brand-title">RPG Encounters</h1>
  </div>
</template>

<script setup>
  import logoUrl from '@/assets/images/logo.png'
</script>

<style scoped>
  .brand-section {
    display: flex;
    align-items: center;
    gap: var(--spacing-xl);
  }

  .logo {
    height: 60px !important;
    width: auto;
    flex-shrink: 0;
  }

  .brand-title {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--color-text-primary);
    margin: 0;
    white-space: nowrap;
  }

  /* Responsive styles for tablets */
  @media (min-width: 481px) and (max-width: 1023px) {
    .brand-section {
      gap: var(--spacing-lg);
    }

    .brand-title {
      font-size: 1.35rem;
    }

    .logo {
      height: 55px !important;
    }
  }

  /* Responsive styles for mobile */
  @media (max-width: 480px) {
    .brand-title {
      font-size: 1.25rem;
    }

    .logo {
      height: 50px !important;
    }
  }
</style>
