<script setup lang="ts">
import { ref, watch, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { storeToRefs } from "pinia";
import { useCoworkingsStore } from "@/stores/coworkings.store";
import { formatDateTime } from "@/utils/date.utils";
import DateInput from "@/components/DateInput.vue";
const router = useRouter();
const route = useRoute();
const store = useCoworkingsStore();
const { bookings, loading, error, total, limit, offset } = storeToRefs(store);

const isHistory = ref(route.path.includes("history"));
const statusFilter = ref("");
const coworkingName = ref("");
const dateFrom = ref("");
const dateTo = ref("");

const STATUS_LABEL: Record<string, string> = {
  created: "Ожидает выдачи",
  active: "Активна",
  pending_close: "Ожидает приемки",
  completed: "Завершена",
  cancelled: "Отменена",
};

const STATUS_CLASS: Record<string, string> = {
  created: "bg-yellow-100 text-yellow-800",
  active: "bg-blue-100 text-blue-800",
  pending_close: "bg-orange-100 text-orange-800",
  completed: "bg-green-100 text-green-800",
  cancelled: "bg-gray-100 text-gray-600",
};

function studentName(
  student: { last_name: string; first_name: string; patronymic: string | null } | null,
): string {
  if (!student) return "—";
  return `${student.last_name} ${student.first_name} ${student.patronymic ?? ""}`.trim();
}

function dateToIso(ddmmyyyy: string, suffix: string): string | undefined {
  const [dd, mm, yyyy] = ddmmyyyy.split(".");
  if (!dd || !mm || !yyyy || yyyy.length < 4) return undefined;
  const iso = `${yyyy}-${mm.padStart(2, "0")}-${dd.padStart(2, "0")}`;
  return `${iso}${suffix}`;
}

function load() {
  if (isHistory.value) {
    store.fetchBookingHistory({
      coworking_name: coworkingName.value || undefined,
      date_from: dateToIso(dateFrom.value, "T00:00:00Z"),
      date_to: dateToIso(dateTo.value, "T23:59:59Z"),
      limit: 20,
      offset: 0,
    });
  } else {
    store.fetchBookings({
      status: statusFilter.value || undefined,
      coworking_name: coworkingName.value || undefined,
      limit: 20,
      offset: 0,
    });
  }
}

function goToPage(newOffset: number) {
  if (isHistory.value) {
    store.fetchBookingHistory({
      coworking_name: coworkingName.value || undefined,
      date_from: dateToIso(dateFrom.value, "T00:00:00Z"),
      date_to: dateToIso(dateTo.value, "T23:59:59Z"),
      limit: limit.value,
      offset: newOffset,
    });
  } else {
    store.fetchBookings({
      status: statusFilter.value || undefined,
      coworking_name: coworkingName.value || undefined,
      limit: limit.value,
      offset: newOffset,
    });
  }
}

function openDetail(id: string) {
  router.push({ name: "booking-detail", params: { id } });
}

function setTabHistory(value: boolean) {
  isHistory.value = value;
  const path = value ? "/bookings/history" : "/bookings/requests";
  if (route.path !== path) router.replace(path);
  load();
}

watch(
  () => route.path,
  (path) => {
    const history = path.includes("history");
    if (isHistory.value !== history) {
      isHistory.value = history;
      load();
    }
  },
);

onMounted(() => {
  load();
});
</script>

<template>
  <div class="space-y-4">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <h2 class="text-xl font-semibold">
        {{ isHistory ? "История использования" : "Заявки на выдачу и возврат" }}
      </h2>
      <div class="flex rounded-lg border border-gray-200 bg-gray-50 p-0.5">
        <button
          type="button"
          class="rounded-md px-3 py-1.5 text-sm font-medium transition"
          :class="
            !isHistory
              ? 'bg-white text-gray-900 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          "
          @click="setTabHistory(false)"
        >
          Заявки
        </button>
        <button
          type="button"
          class="rounded-md px-3 py-1.5 text-sm font-medium transition"
          :class="
            isHistory
              ? 'bg-white text-gray-900 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          "
          @click="setTabHistory(true)"
        >
          История
        </button>
      </div>
    </div>

    <p class="text-sm text-gray-600">
      {{
        isHistory
          ? "Просмотр завершённых бронирований за период. Заявки в работе — во вкладке «Заявки»."
          : "Обработка заявок на выдачу ключа и приёмку коворкинга (в т.ч. заявки на возврат)."
      }}
    </p>

    <!-- Фильтры: разные для Заявки / История -->
    <div class="flex flex-wrap items-end gap-4 rounded-lg border bg-white p-4 shadow-sm">
      <div v-if="!isHistory">
        <label class="mb-1 block text-sm font-medium text-gray-700">Статус</label>
        <select
          v-model="statusFilter"
          class="rounded-lg border border-gray-300 px-3 py-2 text-sm"
          @change="load"
        >
          <option value="">Все</option>
          <option value="created">Ожидает выдачи</option>
          <option value="pending_close">Ожидает приемки</option>
          <option value="active">Активна</option>
          <option value="completed">Завершена</option>
          <option value="cancelled">Отменена</option>
        </select>
      </div>
      <div>
        <label class="mb-1 block text-sm font-medium text-gray-700">
          {{ isHistory ? "Коворкинг" : "Коворкинг" }}
        </label>
        <input
          v-model="coworkingName"
          type="text"
          class="rounded-lg border border-gray-300 px-3 py-2 text-sm"
          placeholder="Название"
          @keyup.enter="load"
        />
      </div>
      <template v-if="isHistory">
        <div>
          <label class="mb-1 block text-sm font-medium text-gray-700">Дата с</label>
          <DateInput v-model="dateFrom" @change="load" />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium text-gray-700">Дата по</label>
          <DateInput v-model="dateTo" @change="load" />
        </div>
      </template>
      <button
        type="button"
        class="rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
        @click="load"
      >
        Применить
      </button>
    </div>

    <p v-if="error" class="text-red-600">{{ error }}</p>
    <p v-if="loading" class="text-gray-600">Загрузка...</p>

    <div v-else class="overflow-x-auto rounded-lg border bg-white shadow-sm">
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
              <span v-if="b.coworking" class="block text-xs text-gray-500">
                корп. {{ b.coworking.building }}, комн. {{ b.coworking.number }}
              </span>
            </td>
            <td class="px-4 py-3">
              {{ studentName(b.student) }}
              <span v-if="b.student" class="block text-xs text-gray-500">
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
                :class="STATUS_CLASS[b.status] || 'bg-gray-100'"
              >
                {{ STATUS_LABEL[b.status] || b.status }}
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
            <td colspan="5" class="px-4 py-6 text-center text-gray-500">
              {{ isHistory ? "За выбранный период записей нет" : "Подходящих заявок нет" }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="total > limit" class="flex justify-center gap-2">
      <button
        class="rounded border px-3 py-1 disabled:opacity-50"
        :disabled="offset <= 0"
        @click="goToPage(offset - limit)"
      >
        Назад
      </button>
      <span class="py-1 text-sm text-gray-600">
        {{ offset + 1 }}–{{ Math.min(offset + limit, total) }} из {{ total }}
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
