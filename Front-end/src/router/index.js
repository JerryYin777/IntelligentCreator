import { createRouter, createWebHashHistory } from "vue-router"


const routes = [
    { path: "/", redirect: "/home" },
    { path: "/home", name: "home", component: () => import('../views/index.vue') },
]

export const router = createRouter({
    routes: routes,
    history: createWebHashHistory(),
})

export default router