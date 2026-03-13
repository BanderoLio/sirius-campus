<script setup lang="ts">
import { onMounted, computed, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { storeToRefs } from "pinia";
import { useCoworkingsStore } from "@/stores/coworkings.store";
import { formatDateTime } from "@/utils/date.utils";
import DateInput from "@/components/DateInput.vue";
import TimeInput from "@/components/TimeInput.vue";
import { format } from "date-fns";

const route = useRoute();
const router = useRouter();
const store = useCoworkingsStore();
const { currentBooking, loading, error } = storeToRefs(store);

const id = computed(() => route.params.id as string);
const actionLoading = ref(false);
const showReturnForm = ref(false);

const returnDate = ref(format(new Date(), "dd.MM.yyyy"));
const returnTime = ref(format(new Date(), "HH:mm"));

const rolePrefix = computed(() => {
  const token = localStorage.getItem("access_token") ?? "";
  return token.split(":")[0];
});
const isEducator = computed(() => ["educator", "admin"].includes(rolePrefix.value));
const isStudent = computed(() => !isEducator.value);

function buildReturnedBackISO(): string {
  const [dd, mm, yyyy] = returnDate.value.split(".");
  const [hh, mi] = returnTime.value.split(":");
  const d = new Date(+yyyy, +mm - 1, +dd, +hh || 0, +mi || 0);
  return d.toISOString();
}

const statusLabel: Record<string, string> = {
  created: "Создана",
  active: "Активна",
  pending_close: "Ожидает приемки",
  completed: "Завершена",
  cancelled: "Отменена",
};

const statusClass: Record<string, string> = {
  created: "bg-yellow-100 text-yellow-800",
  active: "bg-blue-100 text-blue-800",
  pending_close: "bg-orange-100 text-orange-800",
  completed: "bg-green-100 text-green-800",
  cancelled: "bg-gray-100 text-gray-600",
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

async function doAction(action: "confirm" | "close" | "cancel") {
  actionLoading.value = true;
  try {
    if (action === "confirm") await store.confirmBooking(id.value);
    else if (action === "close") await store.closeBooking(id.value);
    else await store.cancelBooking(id.value);
    await store.fetchBooking(id.value);
  } finally {
    actionLoading.value = false;
  }
}

async function submitReturnRequest() {
  actionLoading.value = true;
  try {
    await store.requestCloseBooking(id.value, buildReturnedBackISO());
    showReturnForm.value = false;
    await store.fetchBooking(id.value);
  } finally {
    actionLoading.value = false;
  }
}

onMounted(() => {
  store
    .fetchBooking(id.value)
    .catch(() =>
      router.push({ name: isEducator.value ? "booking-requests" : "my-bookings" }),
    );
});
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center gap-4">
      <button
        type="button"
        class="text-blue-600 hover:underline"
        @click="router.back()"
      >
        &larr; Назад
      </button>
      <h2 class="text-xl font-semibold">Бронирование</h2>
    </div>

    <p v-if="error" class="text-red-600">
      {{ error }}
    </p>
    <p v-if="loading && !currentBooking" class="text-gray-600">Загрузка...</p>

    <template v-if="currentBooking">
      <div class="rounded border bg-white p-6 shadow">
        <div class="grid gap-4 sm:grid-cols-2">
          <div>
            <span class="text-sm text-gray-500">Коворкинг</span>
            <p class="font-medium">
              {{ currentBooking.coworking?.name || "—" }}
            </p>
            <p v-if="currentBooking.coworking" class="text-sm text-gray-500">
              Корпус {{ currentBooking.coworking.building }}, подъезд
              {{ currentBooking.coworking.entrance }}, комн.
              {{ currentBooking.coworking.number }}
            </p>
          </div>
          <div>
            <span class="text-sm text-gray-500">Статус</span>
            <p>
              <span
                class="rounded px-2.5 py-0.5 text-sm font-medium"
                :class="statusClass[currentBooking.status] || 'bg-gray-100'"
              >
                {{
                  statusLabel[currentBooking.status] || currentBooking.status
                }}
              </span>
            </p>
          </div>
          <div>
            <span class="text-sm text-gray-500">Получение</span>
            <p>{{ formatDateTime(currentBooking.taken_from) }}</p>
          </div>
          <div>
            <span class="text-sm text-gray-500">Возврат</span>
            <p>{{ formatDateTime(currentBooking.returned_back) }}</p>
          </div>
          <div>
            <span class="text-sm text-gray-500">Студент</span>
            <p>{{ studentName(currentBooking.student) }}</p>
            <p v-if="currentBooking.student" class="text-sm text-gray-500">
              Корпус {{ currentBooking.student.building }}, подъезд
              {{ currentBooking.student.entrance }}, комн.
              {{ currentBooking.student.room }}
            </p>
          </div>
        </div>
      </div>

      <div class="flex flex-wrap gap-3">
        <button
          v-if="currentBooking.status === 'created' && isEducator"
          type="button"
          class="rounded bg-green-600 px-4 py-2 text-white hover:bg-green-700 disabled:opacity-50"
          :disabled="actionLoading"
          @click="doAction('confirm')"
        >
          Подтвердить (выдать ключ)
        </button>
        <button
          v-if="
            (currentBooking.status === 'active' ||
              currentBooking.status === 'pending_close') &&
            isEducator
          "
          type="button"
          class="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
          :disabled="actionLoading"
          @click="doAction('close')"
        >
          Закрыть (принять ключ)
        </button>
        <div
          v-if="currentBooking.status === 'active' && isStudent"
          class="w-full rounded-lg border border-orange-200 bg-orange-50 p-4"
        >
          <h3 class="text-sm font-semibold text-orange-900">
            Заявка на сдачу коворкинга
          </h3>
          <p class="mt-1 text-sm text-orange-800">
            Укажите дату и время, когда сдаёте ключ воспитателю.
          </p>
          <button
            v-if="!showReturnForm"
            type="button"
            class="mt-3 rounded bg-orange-600 px-4 py-2 text-sm text-white hover:bg-orange-700 disabled:opacity-50"
            :disabled="actionLoading"
            @click="showReturnForm = true"
          >
            Указать время сдачи
          </button>
          <form
            v-else
            class="mt-4 space-y-3"
            @submit.prevent="submitReturnRequest"
          >
            <div class="flex flex-wrap items-end gap-3">
              <div>
                <label class="mb-1 block text-xs font-medium text-gray-700">
                  Дата сдачи
                </label>
                <DateInput v-model="returnDate" class="min-w-[120px]" />
              </div>
              <div>
                <label class="mb-1 block text-xs font-medium text-gray-700">
                  Время сдачи
                </label>
                <TimeInput v-model="returnTime" :step="15" />
              </div>
            </div>
            <div class="flex gap-2">
              <button
                type="submit"
                class="rounded bg-orange-600 px-4 py-2 text-sm text-white hover:bg-orange-700 disabled:opacity-50"
                :disabled="actionLoading"
              >
                Отправить заявку на возврат
              </button>
              <button
                type="button"
                class="rounded border border-gray-300 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                @click="showReturnForm = false"
              >
                Отмена
              </button>
            </div>
          </form>
        </div>
        <button
          v-if="currentBooking.status === 'created'"
          type="button"
          class="rounded border border-red-300 px-4 py-2 text-red-600 hover:bg-red-50 disabled:opacity-50"
          :disabled="actionLoading"
          @click="doAction('cancel')"
        >
          Отменить
        </button>
      </div>
    </template>
  </div>
</template>
