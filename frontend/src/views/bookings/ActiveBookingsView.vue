<script setup lang="ts">
import { onMounted } from "vue";
import { useRouter } from "vue-router";
import { storeToRefs } from "pinia";
import { useCoworkingsStore } from "@/stores/coworkings.store";
import { formatDateTime } from "@/utils/date.utils";

const router = useRouter();
const store = useCoworkingsStore();
const { activeBookings, loading, error } = storeToRefs(store);

const statusLabel: Record<string, string> = {
  active: "Активна",
  pending_close: "Ожидает приемки",
};

const statusClass: Record<string, string> = {
  active: "bg-blue-100 text-blue-800",
  pending_close: "bg-orange-100 text-orange-800",
};

function studentName(
  s: {
    last_name: string;
    first_name: string;
    patronymic: string | null;
  } | null,
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
      <div class="flex items-center gap-2">
        <RouterLink
          to="/bookings/requests"
          class="rounded border px-3 py-1.5 text-sm hover:bg-gray-100"
        >
          К заявкам
        </RouterLink>
        <button
          type="button"
          class="rounded border px-3 py-1.5 text-sm hover:bg-gray-100"
          @click="store.fetchActiveBookings()"
        >
          Обновить
        </button>
      </div>
    </div>

    <p v-if="error" class="text-red-600">
      {{ error }}
    </p>
    <p v-if="loading" class="text-gray-600">Загрузка...</p>

    <div v-else class="overflow-x-auto rounded border bg-white shadow-sm">
      <table class="w-full text-left text-sm">
        <thead class="border-b bg-gray-50">
          <tr>
            <th class="px-4 py-3 font-medium">Коворкинг</th>
            <th class="px-4 py-3 font-medium">Студент</th>
            <th class="px-4 py-3 font-medium">Комната</th>
            <th class="px-4 py-3 font-medium">Статус</th>
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
              <span v-if="b.coworking" class="block text-xs text-gray-500">
                комн. {{ b.coworking.number }}
              </span>
            </td>
            <td class="px-4 py-3">{{ studentName(b.student) }}</td>
            <td class="px-4 py-3">
              {{
                b.student
                  ? `${b.student.building}-${b.student.entrance}-${b.student.room}`
                  : "—"
              }}
            </td>
            <td class="px-4 py-3">
              <span
                class="rounded px-2 py-0.5 text-xs font-medium"
                :class="statusClass[b.status] || 'bg-gray-100'"
              >
                {{ statusLabel[b.status] || b.status }}
              </span>
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
            <td colspan="7" class="px-4 py-6 text-center text-gray-500">
              Нет активных бронирований
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
