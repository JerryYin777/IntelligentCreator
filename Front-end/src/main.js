import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './assets/css/tailwindcss.css'
import ArcoVue from '@arco-design/web-vue'
import '@arco-design/web-vue/dist/arco.css'
import http from './api'

const app = createApp(App)
app.use(router)
app.use(ArcoVue)
app.config.globalProperties.$http = http
app.mount('#app')
