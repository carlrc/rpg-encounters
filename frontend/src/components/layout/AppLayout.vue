<template>
  <div class="app-container">
    <!-- Page Header -->
    <header class="page-header">
      <div class="header-content">
        <h1 class="page-title">{{ pageTitle }}</h1>
      </div>
    </header>

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

<script>
  import { computed, ref } from 'vue'
  import { useRoute, useRouter } from 'vue-router'

  export default {
    name: 'AppLayout',
    setup() {
      const route = useRoute()
      const router = useRouter()
      const successMessage = ref('')

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

      return {
        navigationRoutes,
        pageTitle,
        successMessage,
        showSuccessMessage,
      }
    },
  }
</script>

<style scoped>
  .app-container {
    min-height: 100vh;
    background: #f8f9fa;
    display: flex;
    flex-direction: column;
  }

  .page-header {
    background: white;
    border-bottom: 2px solid #e9ecef;
    padding: 0 24px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    position: sticky;
    top: 0;
    z-index: 100;
  }

  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    max-width: 1400px;
    margin: 0 auto;
    height: 70px;
  }

  .page-title {
    margin: 0;
    font-size: 1.8em;
    font-weight: 700;
    color: #2c3e50;
    background: linear-gradient(135deg, #007bff, #0056b3);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .main-layout {
    display: flex;
    flex: 1;
    max-width: 1400px;
    margin: 0 auto;
    width: 100%;
  }

  .sidebar {
    width: 200px;
    background: white;
    border-right: 2px solid #e9ecef;
    padding: 20px 0;
    display: flex;
    flex-direction: column;
    gap: 4px;
    box-shadow: 2px 0 4px rgba(0, 0, 0, 0.05);
  }

  .nav-button {
    display: block;
    padding: 12px 24px;
    color: #495057;
    text-decoration: none;
    font-weight: 500;
    transition: all 0.2s ease;
    border-left: 3px solid transparent;
    margin: 0 8px;
    border-radius: 6px;
  }

  .nav-button:hover {
    background: #e3f2fd;
    color: #1976d2;
    border-left-color: #bbdefb;
  }

  .nav-button.active {
    background: linear-gradient(135deg, #007bff, #0056b3);
    color: white;
    border-left-color: #004085;
    font-weight: 600;
    box-shadow: 0 2px 4px rgba(0, 123, 255, 0.3);
  }

  .nav-button.active:hover {
    background: linear-gradient(135deg, #0056b3, #004085);
  }

  .content-area {
    flex: 1;
    background: #ffffff;
    position: relative;
  }

  .success-toast {
    position: fixed;
    top: 20px;
    right: 20px;
    background: linear-gradient(135deg, #28a745, #218838);
    color: white;
    padding: 12px 20px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
    font-size: 0.9em;
    font-weight: 600;
    z-index: 1000;
    animation: slideInRight 0.3s ease-out;
  }

  @keyframes slideInRight {
    from {
      transform: translateX(100%);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }

  @media (max-width: 768px) {
    .main-layout {
      flex-direction: column;
    }

    .sidebar {
      width: 100%;
      flex-direction: row;
      padding: 12px 0;
      overflow-x: auto;
    }

    .nav-button {
      white-space: nowrap;
      margin: 0 4px;
    }
  }
</style>
