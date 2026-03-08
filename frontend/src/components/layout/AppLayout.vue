<template>
  <!-- Public landing gets a full-bleed container -->
  <div v-if="isLandingRoute" class="landing-app-container">
    <slot />
  </div>

  <!-- Auth pages get minimal container -->
  <div v-else-if="!isAuthenticated" class="auth-app-container">
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

  <!-- Player layout - minimal interface -->
  <div v-else-if="isPlayerRoute" class="player-app-container">
    <!-- Simple Header with only logout -->
    <header class="page-header custom-header">
      <div class="header-content custom-header-content">
        <AppBanner />
        <div class="header-actions">
          <button class="logout-button" @click="handleLogout">Logout</button>
        </div>
      </div>
    </header>

    <!-- Player Content Area -->
    <main class="player-content-area">
      <slot />
    </main>
  </div>

  <!-- Full app layout for authenticated DM users -->
  <div v-else class="app-container">
    <!-- Page Header -->
    <header class="page-header custom-header">
      <div class="header-content custom-header-content">
        <AppBanner />
        <div class="header-actions">
          <button class="instructions-button" @click="showInstructions = true">Instructions</button>
          <button class="profile-button" @click="showProfile = true">Profile</button>
        </div>
      </div>
    </header>

    <!-- Main Layout -->
    <div class="main-layout">
      <!-- World Tabs (now part of unified grid) -->
      <WorldTabs @world-changed="handleWorldChange" />

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
        <slot />
      </main>
    </div>

    <!-- Instructions Modal -->
    <InstructionsModal :is-open="showInstructions" @close="showInstructions = false" />
    <ProfileModal
      :is-open="showProfile"
      @close="showProfile = false"
      @logout="handleProfileLogout"
    />
  </div>
</template>

<script setup>
  import { computed, ref } from 'vue'
  import { useRouter, useRoute } from 'vue-router'
  import { serializeError } from 'serialize-error'
  import { useAuthStore } from '../../stores/auth'
  import WorldTabs from '../WorldTabs.vue'
  import InstructionsModal from '../ui/InstructionsModal.vue'
  import ProfileModal from '../ui/ProfileModal.vue'
  import AppBanner from '../ui/AppBanner.vue'
  import { logout } from '../../services/api'

  const router = useRouter()
  const route = useRoute()
  const authStore = useAuthStore()
  const showInstructions = ref(false)
  const showProfile = ref(false)

  // Use auth store for authentication check
  const isAuthenticated = computed(() => authStore.isAuthenticated === true)
  const isLandingRoute = computed(() => route.path === '/')

  // Check if current route is a player route
  const isPlayerRoute = computed(() => {
    return route.name === 'PlayerAuthCallback' || route.name === 'PlayerEncounter'
  })

  // Get navigation routes from router configuration (exclude player-only routes)
  const navigationRoutes = computed(() => {
    const playerOnlyRoutes = ['PlayerAuthCallback', 'PlayerEncounter']
    return router
      .getRoutes()
      .filter(
        (route) =>
          route.name &&
          route.path !== '/' &&
          route.path !== '/login' &&
          route.path !== '/auth' &&
          !playerOnlyRoutes.includes(route.name)
      )
      .map((route) => ({
        path: route.path,
        name: route.name,
      }))
  })

  const handleLogout = async () => {
    try {
      await logout()
      await authStore.logout()
      router.push('/login')
    } catch (error) {
      console.error('Logout failed:', JSON.stringify(serializeError(error)))
      // Force redirect anyway
      await authStore.logout()
      router.push('/login')
    }
  }

  const handleProfileLogout = async () => {
    showProfile.value = false
    await handleLogout()
  }

  const handleWorldChange = async (worldId) => {
    // Lazy load world store to avoid accessing it on login page
    const { useWorldStore } = await import('../../stores/world')
    const worldStore = useWorldStore()
    worldStore.setCurrentWorldId(worldId)
  }
</script>

<style scoped>
  .landing-app-container {
    width: 100%;
    min-height: 100vh;
    min-height: 100dvh;
  }

  .auth-app-container {
    width: 100%;
    height: 100vh; /* Fallback for older browsers */
    height: 100dvh; /* Dynamic viewport height for iOS */
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

  .player-app-container {
    width: 100%;
    height: 100vh; /* Fallback for older browsers */
    height: 100dvh; /* Dynamic viewport height for iOS */
    display: flex;
    flex-direction: column;
    background: var(--bg-primary);
  }

  .player-content-area {
    flex: 1;
    overflow: auto;
    -webkit-overflow-scrolling: touch;
    /* Allow both horizontal and vertical touch scrolling */
    touch-action: auto;
    padding-bottom: env(safe-area-inset-bottom);
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

  .profile-button {
    background: none;
    border: none;
    color: var(--color-text-primary);
    font-size: 1.2rem;
    font-weight: 600;
    cursor: pointer;
    padding: 0;
    margin-left: var(--spacing-lg);
    white-space: nowrap;
    transition: color 0.2s ease;
  }

  .profile-button:hover {
    color: var(--color-text-secondary);
  }

  .content-area.full-width {
    margin-left: 0;
    max-width: 100%;
  }

  /* Tablet: Consistent with main layout system */
  @media (min-width: 768px) and (max-width: 1023px) {
    .custom-header-content {
      padding-left: var(--spacing-lg) !important;
      padding-right: var(--spacing-lg) !important;
    }
  }

  /* Mobile: Stack layout */
  @media (max-width: 767px) {
    .instructions-button {
      font-size: 1rem;
    }
  }

  .player-app-container .page-header {
    padding: 0 var(--spacing-lg) !important;
  }

  .player-app-container .header-content {
    height: 56px;
  }

  @media (max-width: 360px) {
    .player-app-container :deep(.brand-title) {
      display: none;
    }
  }
</style>
