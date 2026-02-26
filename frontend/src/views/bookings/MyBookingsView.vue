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
const statusFilter = ref<string>("");

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

function applyFilters() {
  store.fetchMyBookings({
    status: statusFilter.value || undefined,
    limit: 20,
    offset: 0,
  });
}

function goToPage(newOffset: number) {
  store.fetchMyBookings({
    status: statusFilter.value || undefined,
    limit: limit.value,
    offset: newOffset,
  });
}

function openDetail(id: string) {
  router.push({ name: "booking-detail", params: { id } });
}

onMounted(() => {
  store.fetchMyBookings();
});
</script>

<template>
  <div class="space-y-4">
    <h2 class="text-xl font-semibold">Мои бронирования</h2>

    <div class="flex flex-wrap gap-4 rounded border bg-white p-4">
      <div>
        <label class="mb-1 block text-sm">Статус</label>
        <select
          v-model="statusFilter"
          class="rounded border px-3 py-2"
          @change="applyFilters"
        >
          <option value="">Все</option>
          <option value="created">Создана</option>
          <option value="active">Активна</option>
          <option value="completed">Завершена</option>
          <option value="cancelled">Отменена</option>
        </select>
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
      class="space-y-2"
    >
      <div
        v-for="b in bookings"
        :key="b.id"
        class="cursor-pointer rounded border bg-white p-4 shadow-sm transition hover:shadow"
        @click="openDetail(b.id)"
      >
        <div class="flex items-center justify-between">
          <div>
            <span class="font-medium">{{ b.coworking?.name || "Коворкинг" }}</span>
            <span
              v-if="b.coworking"
              class="ml-2 text-sm text-gray-500"
            >
              комн. {{ b.coworking.number }}
            </span>
          </div>
          <span
            class="rounded px-2 py-0.5 text-xs font-medium"
            :class="statusClass[b.status] || 'bg-gray-100'"
          >
            {{ statusLabel[b.status] || b.status }}
          </span>
        </div>
        <p class="mt-1 text-sm text-gray-600">
          {{ formatDateTime(b.taken_from) }} &mdash;
          {{ formatDateTime(b.returned_back) }}
        </p>
      </div>
    </div>

    <p
      v-if="!loading && bookings.length === 0"
      class="text-center text-gray-500"
    >
      Бронирований нет
    </p>

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
