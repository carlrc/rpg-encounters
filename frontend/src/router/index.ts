import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import LandingPage from '../views/LandingPage.vue'
import LoginPage from '../views/LoginPage.vue'
import AuthCallbackPage from '../views/AuthCallbackPage.vue'
import PlayersPage from '../views/PlayersPage.vue'
import CharactersPage from '../views/CharactersPage.vue'
import MemoriesPage from '../views/MemoriesPage.vue'
import RevealsPage from '../views/RevealsPage.vue'
import EncountersPage from '../views/EncountersPage.vue'
import PlayerAuthCallbackPage from '../views/PlayerAuthCallbackPage.vue'
import PlayerEncounterView from '../views/PlayerEncounterView.vue'

const routes = [
  {
    path: '/',
    name: 'Landing',
    component: LandingPage,
    meta: { public: true },
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginPage,
    meta: { public: true },
  },
  {
    path: '/auth',
    name: 'AuthCallback',
    component: AuthCallbackPage,
    meta: { public: true },
  },
  {
    path: '/players',
    name: 'Players',
    component: PlayersPage,
  },
  {
    path: '/characters',
    name: 'Characters',
    component: CharactersPage,
  },
  {
    path: '/memories',
    name: 'Memories',
    component: MemoriesPage,
  },
  {
    path: '/reveals',
    name: 'Reveals',
    component: RevealsPage,
  },
  {
    path: '/encounters',
    name: 'Encounters',
    component: EncountersPage,
  },
  {
    path: '/players/:playerId/login',
    name: 'PlayerAuthCallback',
    component: PlayerAuthCallbackPage,
    meta: { public: true },
  },
  {
    path: '/players/:playerId/encounter',
    name: 'PlayerEncounter',
    component: PlayerEncounterView,
    meta: { public: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Navigation guard to check authentication
router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore()

  if (to.path === '/' || to.path === '/login') {
    if (!authStore.isInitialized) {
      await authStore.initializeAuth()
    }

    if (authStore.isAuthenticated) {
      next('/players')
      return
    }

    next()
    return
  }

  // Allow public routes
  if (to.meta.public) {
    next()
    return
  }

  // Initialize auth if not already done
  if (!authStore.isInitialized) {
    await authStore.initializeAuth()
  }

  // Check authentication status
  if (authStore.isAuthenticated) {
    next()
  } else {
    next('/login')
  }
})

export default router
