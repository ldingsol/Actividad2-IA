import { createApp } from 'vue';
import App from './App.vue';
import router from './router'; // <-- Importación

const app = createApp(App);

app.use(router); // <-- Uso

app.mount('#app');