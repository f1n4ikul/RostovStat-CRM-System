import { createRouter, createWebHistory } from "vue-router";
import LibraryView from "../views/LibraryView.vue";
import Profile from "../components/Profile.vue";
import AdminPanel from "../components/AdminPanel.vue";

const routes = [
  {
    path: "/",
    name: "Feed",
    component: () => import("../views/FeedView.vue"), // Лента новостей
  },
  {
    path: "/library",
    name: "library",
    component: LibraryView,
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
    // Опционально: мета-поле для проверки прав в будущем
    meta: { requiresAdmin: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
