<script setup lang="ts">
import { onMounted } from "vue";
import { useRouter } from "vue-router";
import { storeToRefs } from "pinia";
import { useCoworkingsStore } from "@/stores/coworkings.store";
import { formatDateTime } from "@/utils/date.utils";

const router = useRouter();
const store = useCoworkingsStore();
const { activeBookings, loading, error } = storeToRefs(store);

function studentName(
  s: { last_name: string; first_name: string; patronymic: string | null } | null,
): string {
  if (!s) return "—";
  return `${s.last_name} ${s.first_name} ${s.patronymic || ""}`.trim();
}

function openDetail(id: string) {
  router.push({ name: "booking-detail", params: { id } });
}

onMounted(() => {
  store.fetchActiveBookings();
});
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h2 class="text-xl font-semibold">Активные бронирования</h2>
      <button
        type="button"
        class="rounded border px-3 py-1.5 text-sm hover:bg-gray-100"
        @click="store.fetchActiveBookings()"
      >
        Обновить
      </button>
    </div>

    <p
      v-if="error"
      class="text-red-600"
    >
      {{ error }}
    </p>
    <p
      v-if="loading"
      class="text-gray-600"
    >
      Загрузка...
    </p>

    <div
      v-else
      class="overflow-x-auto rounded border bg-white shadow-sm"
    >
      <table class="w-full text-left text-sm">
        <thead class="border-b bg-gray-50">
          <tr>
            <th class="px-4 py-3 font-medium">Коворкинг</th>
            <th class="px-4 py-3 font-medium">Студент</th>
            <th class="px-4 py-3 font-medium">Комната</th>
            <th class="px-4 py-3 font-medium">Получение</th>
            <th class="px-4 py-3 font-medium">Возврат</th>
            <th class="px-4 py-3 font-medium" />
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="b in activeBookings"
            :key="b.id"
            class="border-b last:border-b-0 hover:bg-gray-50"
          >
            <td class="px-4 py-3 font-medium">
              {{ b.coworking?.name || "—" }}
              <span
                v-if="b.coworking"
                class="block text-xs text-gray-500"
              >
                комн. {{ b.coworking.number }}
              </span>
            </td>
            <td class="px-4 py-3">{{ studentName(b.student) }}</td>
            <td class="px-4 py-3">
              {{ b.student ? `${b.student.building}-${b.student.entrance}-${b.student.room}` : "—" }}
            </td>
            <td class="px-4 py-3">{{ formatDateTime(b.taken_from) }}</td>
            <td class="px-4 py-3">{{ formatDateTime(b.returned_back) }}</td>
            <td class="px-4 py-3">
              <button
                type="button"
                class="rounded border px-3 py-1 text-xs hover:bg-gray-100"
                @click="openDetail(b.id)"
              >
                Подробнее
              </button>
            </td>
          </tr>
          <tr v-if="activeBookings.length === 0 && !loading">
            <td
              colspan="6"
              class="px-4 py-6 text-center text-gray-500"
            >
              Нет активных бронирований
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
