// Название файла: main.js
import { createApp } from "vue";
import "./style.css";
import App from "./App.vue";
import axios from "axios";
import router from "./router";

// Импорт PrimeVue и ресурсов
import PrimeVue from "primevue/config";
// ИСПРАВЛЕНО: Правильный пакет для темы Aura в PrimeVue 4
import Aura from "@primevue/themes/aura";
import "primeicons/primeicons.css";
import ToastService from "primevue/toastservice";
import ConfirmationService from "primevue/confirmationservice";

axios.defaults.baseURL = "http://127.0.0.1:8000/api/";

const app = createApp(App);

// Добавляем глобальный перехватчик ошибок для Vue, чтобы они точно писались в консоль
app.config.errorHandler = (err, instance, info) => {
  console.error("Глобальная ошибка Vue:", err);
  console.error("Компонент:", instance);
  console.error("Инфо:", info);
};

app.use(router);
app.use(ToastService);
app.use(ConfirmationService);

// Настройка PrimeVue 4.0+
app.use(PrimeVue, {
  ripple: true,
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
