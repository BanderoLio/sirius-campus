import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory((import.meta as unknown as { env: { BASE_URL?: string } }).env?.BASE_URL ?? "/"),
  routes: [
    {
      path: "/",
      redirect: "/applications",
    },
    {
      path: "/applications",
      name: "applications",
      component: () => import("@/views/applications/ApplicationsListView.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/applications/new",
      name: "application-new",
      component: () => import("@/views/applications/ApplicationNewView.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/applications/:id",
      name: "application-detail",
      component: () => import("@/views/applications/ApplicationDetailView.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/login",
      name: "login",
      component: () => import("@/views/LoginView.vue"),
    },
  ],
});

router.beforeEach((to) => {
  const token = localStorage.getItem("access_token");
  if (to.meta.requiresAuth && !token) {
    return { name: "login", query: { redirect: to.fullPath } };
  }
  return true;
});

export default router;
