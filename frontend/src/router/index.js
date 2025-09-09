import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import LoginPage from '../views/LoginPage.vue'
import AuthCallbackPage from '../views/AuthCallbackPage.vue'
import PlayersPage from '../views/PlayersPage.vue'
import CharactersPage from '../views/CharactersPage.vue'
import MemoriesPage from '../views/MemoriesPage.vue'
import RevealsPage from '../views/RevealsPage.vue'
import EncountersPage from '../views/EncountersPage.vue'

const routes = [
  {
    path: '/',
    redirect: '/login',
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
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Navigation guard to check authentication
router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()

  // Allow public routes
  if (to.meta.public) {
    next()
    return
  }

  // Check authentication status
  if (authStore.isAuthenticated) {
    next()
  } else {
    next('/login')
  }
})

export default router
