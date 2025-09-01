<template>
  <div class="app-container">
    <!-- Page Header -->
    <header class="page-header">
      <div class="header-content">
        <h1 class="page-title">{{ pageTitle }}</h1>
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

  const pageTitle = computed(() => {
    return route.name || 'DnD AI'
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
  /* All layout styles now use shared classes - minimal component-specific overrides only */
</style>
