import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(
    (import.meta as unknown as { env: { BASE_URL?: string } }).env?.BASE_URL ??
      "/",
  ),
  routes: [
    {
      path: "/",
      redirect: "/coworkings",
    },
    {
      path: "/coworkings",
      name: "coworkings",
      component: () => import("@/views/coworkings/CoworkingsListView.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/bookings/new/:coworkingId?",
      name: "booking-new",
      component: () => import("@/views/bookings/BookingNewView.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/bookings/my",
      name: "my-bookings",
      component: () => import("@/views/bookings/MyBookingsView.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/bookings/active",
      name: "active-bookings",
      component: () => import("@/views/bookings/ActiveBookingsView.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/bookings/history",
      name: "booking-history",
      component: () => import("@/views/bookings/BookingHistoryView.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/bookings/:id",
      name: "booking-detail",
      component: () => import("@/views/bookings/BookingDetailView.vue"),
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
