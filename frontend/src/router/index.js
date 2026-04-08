import { createRouter, createWebHistory } from "vue-router";
import LibraryView from "../views/LibraryView.vue";
import Profile from "../components/Profile.vue";

const routes = [
  {
    path: "/",
    name: "library",
    component: LibraryView,
  },
  {
    path: "/profile",
    name: "profile",
    component: Profile,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
