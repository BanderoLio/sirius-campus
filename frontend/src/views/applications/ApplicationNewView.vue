<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useApplicationsStore } from "@/stores/applications.store";

const router = useRouter();
const store = useApplicationsStore();
const leaveDate = ref("");
const leaveTime = ref("12:00");
const returnDate = ref("");
const returnTime = ref("18:00");
const reason = ref("");
const contactPhone = ref("");
const submitting = ref(false);
const error = ref("");

function buildIso(date: string, time: string): string {
  if (!date) return "";
  const [h, m] = (time || "00:00").split(":");
  return `${date}T${h || "00"}:${m || "00"}:00.000Z`;
}

async function submit() {
  error.value = "";
  if (!leaveDate.value || !returnDate.value || !reason.value.trim() || !contactPhone.value.trim()) {
    error.value = "Заполните все поля.";
    return;
  }
  submitting.value = true;
  try {
    const created = await store.create({
      leave_time: buildIso(leaveDate.value, leaveTime.value),
      return_time: buildIso(returnDate.value, returnTime.value),
      reason: reason.value.trim(),
      contact_phone: contactPhone.value.trim(),
    });
    router.push({ name: "application-detail", params: { id: created.id } });
  } catch {
    error.value = store.error || "Не удалось создать заявление.";
  } finally {
    submitting.value = false;
  }
}
</script>

<template>
  <div class="mx-auto max-w-lg space-y-6">
    <h2 class="text-xl font-semibold">Новое заявление на выход</h2>
    <form @submit.prevent="submit" class="space-y-4 rounded border bg-white p-6 shadow">
      <div>
        <label class="mb-1 block font-medium">Дата и время выхода</label>
        <div class="flex gap-2">
          <input v-model="leaveDate" type="date" class="flex-1 rounded border px-3 py-2" required />
          <input v-model="leaveTime" type="time" class="w-28 rounded border px-3 py-2" />
        </div>
      </div>
      <div>
        <label class="mb-1 block font-medium">Дата и время возвращения</label>
        <div class="flex gap-2">
          <input v-model="returnDate" type="date" class="flex-1 rounded border px-3 py-2" required />
          <input v-model="returnTime" type="time" class="w-28 rounded border px-3 py-2" />
        </div>
      </div>
      <div>
        <label class="mb-1 block font-medium">Цель выхода</label>
        <textarea
          v-model="reason"
          rows="3"
          class="w-full rounded border px-3 py-2"
          required
        />
      </div>
      <div>
        <label class="mb-1 block font-medium">Контактный телефон</label>
        <input
          v-model="contactPhone"
          type="tel"
          class="w-full rounded border px-3 py-2"
          required
        />
      </div>
      <p v-if="error" class="text-red-600">{{ error }}</p>
      <div class="flex gap-2">
        <button
          type="submit"
          class="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
          :disabled="submitting"
        >
          {{ submitting ? "Сохранение..." : "Подать заявление" }}
        </button>
        <router-link
          to="/applications"
          class="rounded border px-4 py-2 hover:bg-gray-100"
        >
          Отмена
        </router-link>
      </div>
    </form>
  </div>
</template>
