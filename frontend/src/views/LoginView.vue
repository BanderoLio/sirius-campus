<script setup lang="ts">
import { ref } from "vue";
import { useRouter, useRoute } from "vue-router";

const router = useRouter();
const route = useRoute();
const token = ref(localStorage.getItem("access_token") || "dev-token");

function submit() {
  localStorage.setItem("access_token", token.value);
  const redirect = (route.query.redirect as string) || "/applications";
  router.push(redirect);
}
</script>

<template>
  <div class="mx-auto max-w-sm rounded-lg border bg-white p-6 shadow">
    <h2 class="mb-4 text-lg font-semibold">Вход (MVP)</h2>
    <p class="mb-4 text-sm text-gray-600">
      Для разработки укажите любой токен или оставьте dev-token.
    </p>
    <form @submit.prevent="submit" class="space-y-4">
      <div>
        <label class="mb-1 block text-sm font-medium">Токен</label>
        <input
          v-model="token"
          type="text"
          class="w-full rounded border px-3 py-2"
          placeholder="dev-token"
        />
      </div>
      <button
        type="submit"
        class="w-full rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
      >
        Войти
      </button>
    </form>
  </div>
</template>
