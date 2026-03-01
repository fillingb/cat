import { createApp } from 'vue'
import App from './App.vue'
import './index.css'
import { inject } from '@vercel/analytics'

inject() // 初始化统计

createApp(App).mount('#app')
