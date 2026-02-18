<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { storeToRefs } from "pinia";
import { useApplicationsStore } from "@/stores/applications.store";
import { formatDateTime } from "@/utils/date.utils";

const router = useRouter();
const store = useApplicationsStore();
const { items, loading, error, page, pages } = storeToRefs(store);
const statusFilter = ref<string>("");
const dateFrom = ref("");
const dateTo = ref("");

const statusLabel = (s: string) => {
  const map: Record<string, string> = {
    pending: "Ожидает",
    approved: "Одобрено",
    rejected: "Отклонено",
  };
  return map[s] ?? s;
};

function openDetail(id: string) {
  router.push({ name: "application-detail", params: { id } });
}

function applyFilters() {
  store.fetchList({
    page: 1,
    size: 20,
    status: statusFilter.value || undefined,
    date_from: dateFrom.value || undefined,
    date_to: dateTo.value || undefined,
  });
}

onMounted(() => {
  store.fetchList();
});
</script>

<template>
  <div class="space-y-4">
    <div class="flex flex-wrap items-center justify-between gap-4">
      <h2 class="text-xl font-semibold">Заявления на выход</h2>
      <router-link
        to="/applications/new"
        class="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
      >
        Новое заявление
      </router-link>
    </div>

    <div class="flex flex-wrap gap-4 rounded border bg-white p-4">
      <div>
        <label class="mb-1 block text-sm">Статус</label>
        <select
          v-model="statusFilter"
          class="rounded border px-3 py-2"
          @change="applyFilters"
        >
          <option value="">Все</option>
          <option value="pending">Ожидает</option>
          <option value="approved">Одобрено</option>
          <option value="rejected">Отклонено</option>
        </select>
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

    <p v-if="error" class="text-red-600">{{ error }}</p>
    <p v-if="loading" class="text-gray-600">Загрузка...</p>

    <div v-else class="space-y-2">
      <div
        v-for="app in items"
        :key="app.id"
        class="cursor-pointer rounded border bg-white p-4 shadow-sm transition hover:shadow"
        @click="openDetail(app.id)"
      >
        <div class="flex justify-between">
          <span class="font-medium">{{ formatDateTime(app.leave_time) }} — {{ formatDateTime(app.return_time) }}</span>
          <span
            class="rounded px-2 py-0.5 text-sm"
            :class="{
              'bg-yellow-100 text-yellow-800': app.status === 'pending',
              'bg-green-100 text-green-800': app.status === 'approved',
              'bg-red-100 text-red-800': app.status === 'rejected',
            }"
          >
            {{ statusLabel(app.status) }}
          </span>
        </div>
        <p class="mt-1 text-sm text-gray-600">{{ app.reason }}</p>
      </div>
    </div>

    <div v-if="pages > 1" class="flex justify-center gap-2">
      <button
        class="rounded border px-3 py-1 disabled:opacity-50"
        :disabled="page <= 1"
        @click="store.fetchList({ page: page - 1 })"
      >
        Назад
      </button>
      <span class="py-1">Стр. {{ page }} из {{ pages }}</span>
      <button
        class="rounded border px-3 py-1 disabled:opacity-50"
        :disabled="page >= pages"
        @click="store.fetchList({ page: page + 1 })"
      >
        Вперёд
      </button>
    </div>
  </div>
</template>
