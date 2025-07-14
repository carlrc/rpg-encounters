import { createRouter, createWebHistory } from 'vue-router'
import PlayersPage from '../views/PlayersPage.vue'
import CharactersPage from '../views/CharactersPage.vue'
import MemoriesPage from '../views/MemoriesPage.vue'

const routes = [
    {
        path: '/',
        redirect: '/players'
    },
    {
        path: '/players',
        name: 'Players',
        component: PlayersPage
    },
    {
        path: '/characters',
        name: 'Characters',
        component: CharactersPage
    },
    {
        path: '/memories',
        name: 'Memories',
        component: MemoriesPage
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router
