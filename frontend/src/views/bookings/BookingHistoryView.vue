<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { storeToRefs } from "pinia";
import { useCoworkingsStore } from "@/stores/coworkings.store";
import { formatDateTime } from "@/utils/date.utils";

const router = useRouter();
const store = useCoworkingsStore();
const { bookings, loading, error, total, limit, offset } =
  storeToRefs(store);

const coworkingName = ref("");
const dateFrom = ref("");
const dateTo = ref("");

const statusLabel: Record<string, string> = {
  created: "Создана",
  active: "Активна",
  completed: "Завершена",
  cancelled: "Отменена",
};

const statusClass: Record<string, string> = {
  created: "bg-yellow-100 text-yellow-800",
  active: "bg-blue-100 text-blue-800",
  completed: "bg-green-100 text-green-800",
  cancelled: "bg-gray-100 text-gray-600",
};

function studentName(
  s: { last_name: string; first_name: string; patronymic: string | null } | null,
): string {
  if (!s) return "—";
  return `${s.last_name} ${s.first_name} ${s.patronymic || ""}`.trim();
}

function applyFilters() {
  store.fetchBookingHistory({
    coworking_name: coworkingName.value || undefined,
    date_from: dateFrom.value ? `${dateFrom.value}T00:00:00Z` : undefined,
    date_to: dateTo.value ? `${dateTo.value}T23:59:59Z` : undefined,
    limit: 20,
    offset: 0,
  });
}

function goToPage(newOffset: number) {
  store.fetchBookingHistory({
    coworking_name: coworkingName.value || undefined,
    date_from: dateFrom.value ? `${dateFrom.value}T00:00:00Z` : undefined,
    date_to: dateTo.value ? `${dateTo.value}T23:59:59Z` : undefined,
    limit: limit.value,
    offset: newOffset,
  });
}

function openDetail(id: string) {
  router.push({ name: "booking-detail", params: { id } });
}

onMounted(() => {
  store.fetchBookingHistory();
});
</script>

<template>
  <div class="space-y-4">
    <h2 class="text-xl font-semibold">История использования коворкингов</h2>

    <div class="flex flex-wrap gap-4 rounded border bg-white p-4">
      <div>
        <label class="mb-1 block text-sm">Название коворкинга</label>
        <input
          v-model="coworkingName"
          type="text"
          placeholder="Например: Магнолия"
          class="rounded border px-3 py-2"
          @keyup.enter="applyFilters"
        />
      </div>
      <div>
        <label class="mb-1 block text-sm">Дата с</label>
        <input
          v-model="dateFrom"
          type="date"
          class="rounded border px-3 py-2"
          @change="applyFilters"
        />
      </div>
      <div>
        <label class="mb-1 block text-sm">Дата по</label>
        <input
          v-model="dateTo"
          type="date"
          class="rounded border px-3 py-2"
          @change="applyFilters"
        />
      </div>
      <div class="flex items-end">
        <button
          type="button"
          class="rounded border bg-gray-100 px-4 py-2 hover:bg-gray-200"
          @click="applyFilters"
        >
          Применить
        </button>
      </div>
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
            <th class="px-4 py-3 font-medium">Период</th>
            <th class="px-4 py-3 font-medium">Статус</th>
            <th class="px-4 py-3 font-medium" />
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="b in bookings"
            :key="b.id"
            class="border-b last:border-b-0 hover:bg-gray-50"
          >
            <td class="px-4 py-3">
              {{ b.coworking?.name || "—" }}
              <span
                v-if="b.coworking"
                class="block text-xs text-gray-500"
              >
                корп. {{ b.coworking.building }}, комн. {{ b.coworking.number }}
              </span>
            </td>
            <td class="px-4 py-3">
              {{ studentName(b.student) }}
              <span
                v-if="b.student"
                class="block text-xs text-gray-500"
              >
                комн. {{ b.student.room }}
              </span>
            </td>
            <td class="px-4 py-3 whitespace-nowrap">
              {{ formatDateTime(b.taken_from) }}
              <br />
              &mdash; {{ formatDateTime(b.returned_back) }}
            </td>
            <td class="px-4 py-3">
              <span
                class="rounded px-2 py-0.5 text-xs font-medium"
                :class="statusClass[b.status] || 'bg-gray-100'"
              >
                {{ statusLabel[b.status] || b.status }}
              </span>
            </td>
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
          <tr v-if="bookings.length === 0 && !loading">
            <td
              colspan="5"
              class="px-4 py-6 text-center text-gray-500"
            >
              История пуста
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div
      v-if="total > limit"
      class="flex justify-center gap-2"
    >
      <button
        class="rounded border px-3 py-1 disabled:opacity-50"
        :disabled="offset <= 0"
        @click="goToPage(offset - limit)"
      >
        Назад
      </button>
      <span class="py-1 text-sm text-gray-600">
        {{ offset + 1 }}&ndash;{{ Math.min(offset + limit, total) }} из
        {{ total }}
      </span>
      <button
        class="rounded border px-3 py-1 disabled:opacity-50"
        :disabled="offset + limit >= total"
        @click="goToPage(offset + limit)"
      >
        Вперёд
      </button>
    </div>
  </div>
</template>
