<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { storeToRefs } from "pinia";
import { useCoworkingsStore } from "@/stores/coworkings.store";

const router = useRouter();
const store = useCoworkingsStore();
const { coworkings, loading, error } = storeToRefs(store);
const buildingFilter = ref<string>("");
const entranceFilter = ref<string>("");
const availableFilter = ref<string>("");

const isStudent = computed(() => {
  const token = localStorage.getItem("access_token") ?? "";
  const prefix = token.split(":")[0];
  return !["educator", "admin"].includes(prefix);
});

function applyFilters() {
  store.fetchCoworkings({
    building: buildingFilter.value ? Number(buildingFilter.value) : undefined,
    entrance: entranceFilter.value ? Number(entranceFilter.value) : undefined,
    available:
      availableFilter.value === ""
        ? undefined
        : availableFilter.value === "true",
  });
}

function bookCoworking(coworkingId: string) {
  router.push({ name: "booking-new", params: { coworkingId } });
}

onMounted(() => {
  store.fetchCoworkings();
});
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h2 class="text-xl font-semibold">Коворкинги</h2>
    </div>

    <div class="flex flex-wrap gap-4 rounded border bg-white p-4">
      <div>
        <label class="mb-1 block text-sm">Корпус</label>
        <select
          v-model="buildingFilter"
          class="rounded border px-3 py-2"
          @change="applyFilters"
        >
          <option value="">Все</option>
          <option value="8">Корпус 8</option>
          <option value="9">Корпус 9</option>
        </select>
      </div>
      <div>
        <label class="mb-1 block text-sm">Подъезд</label>
        <select
          v-model="entranceFilter"
          class="rounded border px-3 py-2"
          @change="applyFilters"
        >
          <option value="">Все</option>
          <option value="1">1</option>
          <option value="2">2</option>
          <option value="3">3</option>
          <option value="4">4</option>
        </select>
      </div>
      <div>
        <label class="mb-1 block text-sm">Доступность</label>
        <select
          v-model="availableFilter"
          class="rounded border px-3 py-2"
          @change="applyFilters"
        >
          <option value="">Все</option>
          <option value="true">Доступен</option>
          <option value="false">Занят</option>
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
      class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3"
    >
      <div
        v-for="cw in coworkings"
        :key="cw.id"
        class="rounded-lg border bg-white p-5 shadow-sm transition hover:shadow"
      >
        <div class="mb-2 flex items-center justify-between">
          <h3 class="text-lg font-semibold">{{ cw.name }}</h3>
          <span
            class="rounded-full px-2.5 py-0.5 text-xs font-medium"
            :class="cw.available ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
          >
            {{ cw.available ? "Доступен" : "Занят" }}
          </span>
        </div>
        <div class="space-y-1 text-sm text-gray-600">
          <p>Корпус {{ cw.building }}, подъезд {{ cw.entrance }}</p>
          <p>Комната {{ cw.number }}</p>
        </div>
        <button
          v-if="cw.available && isStudent"
          type="button"
          class="mt-4 w-full rounded bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700"
          @click="bookCoworking(cw.id)"
        >
          Забронировать
        </button>
        <div
          v-else-if="!cw.available"
          class="mt-4 w-full rounded bg-gray-100 px-4 py-2 text-center text-sm text-gray-500"
        >
          Недоступен
        </div>
      </div>
    </div>

    <p
      v-if="!loading && coworkings.length === 0"
      class="text-center text-gray-500"
    >
      Коворкинги не найдены
    </p>
  </div>
</template>
