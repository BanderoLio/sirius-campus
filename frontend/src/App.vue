<script setup lang="ts">
import { RouterView } from "vue-router";
</script>

<template>
  <div class="min-h-screen bg-gray-50 text-gray-900">
    <header class="border-b bg-white px-4 py-3 shadow-sm">
      <div class="mx-auto flex max-w-4xl items-center justify-between">
        <h1 class="text-xl font-semibold">Кампус Сириус</h1>
        <nav class="flex gap-4">
          <router-link
            to="/applications"
            class="text-gray-600 hover:text-gray-900"
            active-class="font-medium text-gray-900"
            >Заявления</router-link
          >
        </nav>
      </div>
    </header>
    <main class="mx-auto max-w-4xl px-4 py-6">
      <RouterView />
    </main>
  </div>
</template>
