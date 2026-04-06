import { createApp } from "vue";
import "./style.css"; // Твой файл с @import "tailwindcss";
import App from "./App.vue";
import axios from "axios";


// Импорт PrimeVue и ресурсов
import PrimeVue from "primevue/config";
import Aura from "@primeuix/themes/aura";
import "primeicons/primeicons.css";
import ToastService from "primevue/toastservice";

axios.defaults.baseURL = "http://127.0.0.1:8000/api/";

const app = createApp(App);

// Подключаем сервисы
app.use(ToastService);

// Настройка PrimeVue 4.0+
app.use(PrimeVue, {
  ripple: true, // Включаем эффект ряби при клике
  theme: {
    preset: Aura,
    options: {
      prefix: "p",
      darkModeSelector: ".my-app-dark",
      cssLayer: false,
    },
  },
});

app.mount("#app");
