<template>
  <div class="app-container">
    <!-- Page Header -->
    <header class="page-header custom-header">
      <div class="header-content custom-header-content">
        <div class="brand-section">
          <img :src="logoUrl" alt="RPG Encounters Logo" class="logo" />
          <h1 class="brand-title">RPG Encounters</h1>
        </div>
        <div class="header-actions">
          <button class="instructions-button" @click="showInstructions = true">Instructions</button>
        </div>
      </div>
    </header>

    <!-- World Tabs positioned in left margin -->
    <WorldTabs class="world-tabs-positioned" @world-changed="handleWorldChange" />

    <!-- Main Layout -->
    <div class="main-layout">
      <!-- Left Sidebar Navigation -->
      <nav class="sidebar">
        <router-link
          v-for="route in navigationRoutes"
          :key="route.path"
          :to="route.path"
          :class="['nav-button']"
          active-class="active"
        >
          {{ route.name }}
        </router-link>
      </nav>

      <!-- Main Content Area -->
      <main class="content-area">
        <!-- Success Toast -->
        <div v-if="successMessage" class="success-toast">
          {{ successMessage }}
        </div>

        <slot />
      </main>
    </div>

    <!-- Instructions Modal -->
    <InstructionsModal :is-open="showInstructions" @close="showInstructions = false" />
  </div>
</template>

<script setup>
  import { computed, ref } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import WorldTabs from '../WorldTabs.vue'
  import InstructionsModal from '../ui/InstructionsModal.vue'
  import { useWorldStore } from '@/stores/world'
  import logoUrl from '@/assets/images/logo.png'

  const route = useRoute()
  const router = useRouter()
  const successMessage = ref('')
  const showInstructions = ref(false)
  const worldStore = useWorldStore()

  // Get navigation routes from router configuration
  const navigationRoutes = computed(() => {
    return router
      .getRoutes()
      .filter((route) => route.name && route.path !== '/')
      .map((route) => ({
        path: route.path,
        name: route.name,
      }))
  })

  const showSuccessMessage = (message) => {
    successMessage.value = message
    setTimeout(() => {
      successMessage.value = ''
    }, 1500)
  }

  const handleWorldChange = (worldId) => {
    // Update the store directly - stores will handle their own reactive updates
    worldStore.setCurrentWorldId(worldId)
  }
</script>

<style scoped>
  .custom-header {
    padding: 0 !important;
  }

  .custom-header-content {
    justify-content: space-between !important;
    margin: 0 !important;
    max-width: none !important;
    padding-left: var(--spacing-md) !important;
    padding-right: var(--spacing-md) !important;
  }

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

  .header-actions {
    display: flex;
    align-items: center;
  }

  .instructions-button {
    background: none;
    border: none;
    color: var(--color-text-primary);
    font-size: 1.2rem;
    font-weight: 600;
    cursor: pointer;
    padding: 0;
    margin: 0;
    white-space: nowrap;
    transition: color 0.2s ease;
  }

  .instructions-button:hover {
    color: var(--color-text-secondary);
  }

  /* Tablet-specific navigation optimizations - maintain desktop layout */
  @media (min-width: 481px) and (max-width: 1023px) {
    .brand-section {
      gap: var(--spacing-lg);
    }

    .brand-title {
      font-size: 1.35rem; /* Responsive but not mobile-collapsed */
    }

    .logo {
      height: 55px !important;
    }

    .main-layout {
      margin-left: 70px; /* Maintain sidebar space */
      min-width: 800px; /* Prevent layout collapse */
    }

    .custom-header-content {
      padding-left: var(--spacing-lg) !important;
      padding-right: var(--spacing-lg) !important;
    }
  }

  /* Tablet landscape and desktop adjustments */
  @media (min-width: 1024px) and (max-width: 1366px) {
    .main-layout {
      max-width: calc(100vw - 90px);
    }
  }

  /* Only collapse to mobile layout for very small screens */
  @media (max-width: 480px) {
    .brand-title {
      font-size: 1.25rem;
    }

    .logo {
      height: 50px !important;
    }

    .main-layout {
      margin-left: 0;
      min-width: unset; /* Allow collapse only on very small screens */
    }

    .instructions-button {
      font-size: 1rem;
    }
  }
</style>
