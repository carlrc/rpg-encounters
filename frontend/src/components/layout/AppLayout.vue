<template>
  <!-- Auth pages get minimal container -->
  <div v-if="!isAuthenticated" class="auth-app-container">
    <!-- Page Header for auth pages -->
    <header class="page-header custom-header">
      <div class="header-content custom-header-content">
        <AppBanner />
        <div class="header-actions">
          <!-- Empty space for alignment -->
        </div>
      </div>
    </header>
    <div class="auth-content">
      <slot />
    </div>
  </div>

  <!-- Full app layout for authenticated users -->
  <div v-else class="app-container">
    <!-- Page Header -->
    <header class="page-header custom-header">
      <div class="header-content custom-header-content">
        <AppBanner />
        <div class="header-actions">
          <button class="instructions-button" @click="showInstructions = true">Instructions</button>
          <button class="logout-button" @click="handleLogout">Logout</button>
        </div>
      </div>
    </header>

    <!-- World Tabs -->
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
  import { useAuthStore } from '@/stores/auth'
  import WorldTabs from '../WorldTabs.vue'
  import InstructionsModal from '../ui/InstructionsModal.vue'
  import AppBanner from '../ui/AppBanner.vue'
  import { logout } from '@/services/api'

  const router = useRouter()
  const authStore = useAuthStore()
  const successMessage = ref('')
  const showInstructions = ref(false)

  // Use auth store for authentication check
  const isAuthenticated = computed(() => authStore.isAuthenticated === true)

  // Get navigation routes from router configuration
  const navigationRoutes = computed(() => {
    return router
      .getRoutes()
      .filter((route) => route.name && route.path !== '/login' && route.path !== '/auth')
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

  const handleLogout = async () => {
    try {
      await logout()
      router.push('/login')
    } catch (error) {
      console.error('Logout failed:', error)
      // Force redirect anyway
      window.location.href = '/login'
    }
  }

  const handleWorldChange = async (worldId) => {
    // Lazy load world store to avoid accessing it on login page
    const { useWorldStore } = await import('@/stores/world')
    const worldStore = useWorldStore()
    worldStore.setCurrentWorldId(worldId)
  }
</script>

<style scoped>
  .auth-app-container {
    width: 100%;
    height: 100vh;
    display: flex;
    flex-direction: column;
    background: var(--bg-light);
    overflow: hidden;
  }

  .auth-content {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
  }

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

  .logout-button {
    background: none;
    border: none;
    color: var(--color-text-primary);
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    padding: 0;
    margin-left: var(--spacing-lg);
    white-space: nowrap;
    transition: color 0.2s ease;
  }

  .logout-button:hover {
    color: var(--danger-color);
  }

  .content-area.full-width {
    margin-left: 0;
    max-width: 100%;
  }

  /* Tablet-specific navigation optimizations - maintain desktop layout */
  @media (min-width: 481px) and (max-width: 1023px) {
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
    .main-layout {
      margin-left: 0;
      min-width: unset; /* Allow collapse only on very small screens */
    }

    .instructions-button {
      font-size: 1rem;
    }
  }
</style>
