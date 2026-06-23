// Название файла: src/router/index.js
import { createRouter, createWebHistory } from "vue-router";
// ИСПРАВЛЕНО: Импортируем переменную с тем же именем, что используем в маршрутах
import LibraryDetailView from "../views/LibraryDetailView.vue";
import Profile from "../components/Profile.vue";
import AdminPanel from "../components/AdminPanel.vue";
import AudioDetailView from "../components/AudioDetailView.vue"; // ИСПРАВЛЕНО: имя переменной

const routes = [
  {
    path: "/",
    name: "Feed",
    component: () => import("../views/FeedView.vue"), // Лента новостей
  },
  {
    path: "/library",
    name: "library",
    component: LibraryDetailView, // Теперь переменная существует!
  },
  {
    path: "/library/:id",
    name: "audio-detail",
    component: AudioDetailView, // Теперь переменная существует!
  },
  {
    path: "/profile",
    name: "profile",
    component: Profile,
  },
  {
    path: "/admin",
    name: "admin",
    component: AdminPanel,
    meta: { requiresAdmin: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
