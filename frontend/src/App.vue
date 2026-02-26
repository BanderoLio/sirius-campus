<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { RouterView, RouterLink, useRouter } from "vue-router";

const DEV = import.meta.env.DEV;

const roles = [
  { key: "student", label: "Студент" },
  { key: "educator", label: "Воспитатель" },
  { key: "admin", label: "Админ" },
] as const;

function currentRoleKey(): string {
  const token = localStorage.getItem("access_token") ?? "";
  const prefix = token.split(":")[0];
  return roles.some((r) => r.key === prefix) ? prefix : "student";
}

const activeRole = ref(currentRoleKey());
const activeLabel = computed(
  () => roles.find((r) => r.key === activeRole.value)?.label ?? "Студент",
);

const isEducator = computed(() =>
  ["educator", "admin"].includes(activeRole.value),
);

const router = useRouter();

watch(activeRole, (role) => {
  localStorage.setItem("access_token", `${role}:dev`);
  router.go(0);
});
</script>

<template>
  <div class="min-h-screen bg-gray-50 text-gray-900">
    <header class="border-b bg-white px-4 py-3 shadow-sm">
      <div class="mx-auto flex max-w-5xl items-center justify-between">
        <RouterLink to="/" class="text-xl font-semibold text-gray-900">
          Кампус Сириус
        </RouterLink>
        <nav class="flex items-center gap-4 text-sm">
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
            v-if="isEducator"
            to="/bookings/active"
            class="text-gray-600 hover:text-gray-900"
            active-class="font-medium text-gray-900"
          >
            Дашборд
          </RouterLink>
          <RouterLink
            v-if="isEducator"
            to="/bookings/history"
            class="text-gray-600 hover:text-gray-900"
            active-class="font-medium text-gray-900"
          >
            История
          </RouterLink>

          <div v-if="DEV" class="ml-4 flex items-center gap-1.5 rounded border border-dashed border-amber-400 bg-amber-50 px-2 py-1 text-xs">
            <span class="text-amber-700">Роль:</span>
            <select
              v-model="activeRole"
              class="rounded border-none bg-transparent py-0 pr-5 pl-0.5 text-xs font-medium text-amber-800 focus:ring-1 focus:ring-amber-400"
            >
              <option v-for="r in roles" :key="r.key" :value="r.key">
                {{ r.label }}
              </option>
            </select>
          </div>
        </nav>
      </div>
    </header>
    <main class="mx-auto max-w-5xl px-4 py-6">
      <RouterView />
    </main>
  </div>
</template>
