<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useCoworkingsStore } from "@/stores/coworkings.store";
import { storeToRefs } from "pinia";
import DateInput from "@/components/DateInput.vue";
import TimeInput from "@/components/TimeInput.vue";

const router = useRouter();
const route = useRoute();
const store = useCoworkingsStore();
const { coworkings, loading } = storeToRefs(store);

const selectedCoworkingId = ref((route.params.coworkingId as string) || "");
const takenFromDate = ref("");
const takenFromTime = ref("10:00");
const returnedBackDate = ref("");
const returnedBackTime = ref("14:00");
const submitting = ref(false);
const formError = ref("");

const selectedCoworking = computed(() =>
  coworkings.value.find((c) => c.id === selectedCoworkingId.value),
);

function ddmmyyyyToIsoDate(s: string): string {
  const [dd, mm, yyyy] = s.split(".");
  if (!dd || !mm || !yyyy || yyyy.length < 4) return "";
  return `${yyyy}-${mm.padStart(2, "0")}-${dd.padStart(2, "0")}`;
}

function buildIso(dateDDMMYYYY: string, time: string): string {
  const isoDate = ddmmyyyyToIsoDate(dateDDMMYYYY);
  if (!isoDate) return "";
  const [h, m] = (time || "00:00").split(":");
  return `${isoDate}T${h || "00"}:${m || "00"}:00.000Z`;
}

async function submit() {
  formError.value = "";
  if (
    !selectedCoworkingId.value ||
    !takenFromDate.value ||
    !returnedBackDate.value
  ) {
    formError.value = "Заполните все обязательные поля.";
    return;
  }

  submitting.value = true;
  try {
    const booking = await store.createBooking({
      coworking_id: selectedCoworkingId.value,
      taken_from: buildIso(takenFromDate.value, takenFromTime.value),
      returned_back: buildIso(returnedBackDate.value, returnedBackTime.value),
    });
    router.push({ name: "booking-detail", params: { id: booking.id } });
  } catch {
    formError.value = store.error || "Не удалось создать бронирование.";
  } finally {
    submitting.value = false;
  }
}

onMounted(() => {
  store.fetchCoworkings({ available: true });
});
</script>

<template>
  <div class="mx-auto max-w-lg space-y-6">
    <div class="flex items-center gap-4">
      <button
        type="button"
        class="text-blue-600 hover:underline"
        @click="router.push({ name: 'coworkings' })"
      >
        &larr; К коворкингам
      </button>
      <h2 class="text-xl font-semibold">Новое бронирование</h2>
    </div>

    <form
      class="space-y-4 rounded border bg-white p-6 shadow"
      @submit.prevent="submit"
    >
      <div>
        <label class="mb-1 block font-medium">Коворкинг</label>
        <select
          v-model="selectedCoworkingId"
          class="w-full rounded border px-3 py-2"
          required
          :disabled="loading"
        >
          <option
            value=""
            disabled
          >
            Выберите коворкинг
          </option>
          <option
            v-for="cw in coworkings"
            :key="cw.id"
            :value="cw.id"
          >
            {{ cw.name }} (корп. {{ cw.building }}, подъезд {{ cw.entrance }},
            комн. {{ cw.number }})
          </option>
        </select>
        <p
          v-if="selectedCoworking"
          class="mt-1 text-sm text-gray-500"
        >
          {{ selectedCoworking.name }} — Корпус {{ selectedCoworking.building }},
          подъезд {{ selectedCoworking.entrance }}
        </p>
      </div>

      <div>
        <label class="mb-1 block font-medium">Дата и время получения</label>
        <div class="flex items-start gap-2">
          <DateInput v-model="takenFromDate" required class="flex-1" />
          <TimeInput v-model="takenFromTime" />
        </div>
      </div>

      <div>
        <label class="mb-1 block font-medium">Дата и время возврата</label>
        <div class="flex items-start gap-2">
          <DateInput v-model="returnedBackDate" required class="flex-1" />
          <TimeInput v-model="returnedBackTime" />
        </div>
      </div>

      <p
        v-if="formError"
        class="text-red-600"
      >
        {{ formError }}
      </p>

      <div class="flex gap-2">
        <button
          type="submit"
          class="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
          :disabled="submitting"
        >
          {{ submitting ? "Бронирование..." : "Забронировать" }}
        </button>
        <RouterLink
          to="/coworkings"
          class="rounded border px-4 py-2 hover:bg-gray-100"
        >
          Отмена
        </RouterLink>
      </div>
    </form>
  </div>
</template>
