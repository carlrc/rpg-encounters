<template>
  <div class="app-container">
    <!-- Page Header -->
    <header class="page-header custom-header">
      <div class="header-content custom-header-content">
        <div class="brand-section">
          <img :src="logoUrl" alt="RPG Encounters Logo" class="logo" />
          <h1 class="brand-title">RPG Encounters</h1>
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
  </div>
</template>

<script setup>
  import { computed, ref } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import WorldTabs from '../WorldTabs.vue'
  import { useWorldStore } from '@/stores/world'
  import logoUrl from '@/assets/images/logo.png'

  const route = useRoute()
  const router = useRouter()
  const successMessage = ref('')
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
    justify-content: flex-start !important;
    margin: 0 !important;
    max-width: none !important;
    padding-left: var(--spacing-sm) !important;
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

  @media (max-width: 768px) {
    .brand-title {
      font-size: 1.25rem;
    }

    .logo {
      height: 50px !important;
    }
  }
</style>
