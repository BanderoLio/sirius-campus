<script setup lang="ts">
import { RouterView, RouterLink } from "vue-router";
</script>

<template>
  <div class="min-h-screen bg-gray-50 text-gray-900">
    <header class="border-b bg-white px-4 py-3 shadow-sm">
      <div class="mx-auto flex max-w-5xl items-center justify-between">
        <RouterLink to="/" class="text-xl font-semibold text-gray-900">
          Кампус Сириус
        </RouterLink>
        <nav class="flex gap-4 text-sm">
          <RouterLink
            to="/coworkings"
            class="text-gray-600 hover:text-gray-900"
            active-class="font-medium text-gray-900"
          >
            Коворкинги
          </RouterLink>
          <RouterLink
            to="/bookings/my"
            class="text-gray-600 hover:text-gray-900"
            active-class="font-medium text-gray-900"
          >
            Мои брони
          </RouterLink>
          <RouterLink
            to="/bookings/active"
            class="text-gray-600 hover:text-gray-900"
            active-class="font-medium text-gray-900"
          >
            Дашборд
          </RouterLink>
          <RouterLink
            to="/bookings/history"
            class="text-gray-600 hover:text-gray-900"
            active-class="font-medium text-gray-900"
          >
            История
          </RouterLink>
        </nav>
      </div>
    </header>
    <main class="mx-auto max-w-5xl px-4 py-6">
      <RouterView />
    </main>
  </div>
</template>
