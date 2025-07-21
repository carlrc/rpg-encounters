import { createRouter, createWebHistory } from 'vue-router'
import PlayersPage from '../views/PlayersPage.vue'
import CharactersPage from '../views/CharactersPage.vue'
import NuggetsPage from '../views/NuggetsPage.vue'
import EncountersPage from '../views/EncountersPage.vue'

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
        path: '/nuggets',
        name: 'Trust Nuggets',
        component: NuggetsPage
    },
    {
        path: '/encounters',
        name: 'Encounters',
        component: EncountersPage
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router
