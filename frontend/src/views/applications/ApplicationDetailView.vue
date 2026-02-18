<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { storeToRefs } from "pinia";
import { useApplicationsStore } from "@/stores/applications.store";
import { formatDateTime } from "@/utils/date.utils";

const route = useRoute();
const router = useRouter();
const store = useApplicationsStore();
const { currentDetail, loading, error } = storeToRefs(store);
const decideStatus = ref<"approved" | "rejected">("approved");
const rejectReason = ref("");
const deciding = ref(false);
const uploading = ref(false);
const docType = ref("signed_application");
const fileInput = ref<HTMLInputElement | null>(null);

const id = computed(() => route.params.id as string);
const isPending = computed(() => currentDetail.value?.status === "pending");

onMounted(() => {
  store.fetchOne(id.value).catch(() => router.push({ name: "applications" }));
});

async function decide() {
  deciding.value = true;
  try {
    await store.decide(id.value, {
      status: decideStatus.value,
      reject_reason: rejectReason.value || undefined,
    });
  } finally {
    deciding.value = false;
  }
}

function triggerUpload() {
  fileInput.value?.click();
}

async function onFileChange(e: Event) {
  const target = e.target as HTMLInputElement;
  const file = target.files?.[0];
  if (!file) return;
  uploading.value = true;
  try {
    await store.uploadDoc(id.value, docType.value, file);
    if (fileInput.value) fileInput.value.value = "";
  } finally {
    uploading.value = false;
  }
}

function documentTypeLabel(t: string) {
  const map: Record<string, string> = {
    signed_application: "Скан заявления",
    parent_letter: "Письмо родителя",
    voice_message: "Голосовое сообщение",
  };
  return map[t] ?? t;
}
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center gap-4">
      <button
        type="button"
        class="text-blue-600 hover:underline"
        @click="router.push({ name: 'applications' })"
      >
        ← К списку
      </button>
      <h2 class="text-xl font-semibold">Заявление</h2>
    </div>

    <p v-if="error" class="text-red-600">{{ error }}</p>
    <p v-if="loading && !currentDetail" class="text-gray-600">Загрузка...</p>

    <template v-else-if="currentDetail">
      <div class="rounded border bg-white p-6 shadow">
        <div class="grid gap-4 sm:grid-cols-2">
          <div>
            <span class="text-gray-600">Выход:</span>
            {{ formatDateTime(currentDetail.leave_time) }}
          </div>
          <div>
            <span class="text-gray-600">Возвращение:</span>
            {{ formatDateTime(currentDetail.return_time) }}
          </div>
          <div class="sm:col-span-2">
            <span class="text-gray-600">Цель:</span>
            {{ currentDetail.reason }}
          </div>
          <div>
            <span class="text-gray-600">Телефон:</span>
            {{ currentDetail.contact_phone }}
          </div>
          <div>
            <span class="text-gray-600">Статус:</span>
            <span
              class="rounded px-2 py-0.5 text-sm"
              :class="{
                'bg-yellow-100': currentDetail.status === 'pending',
                'bg-green-100': currentDetail.status === 'approved',
                'bg-red-100': currentDetail.status === 'rejected',
              }"
            >
              {{ currentDetail.status === 'pending' ? 'Ожидает' : currentDetail.status === 'approved' ? 'Одобрено' : 'Отклонено' }}
            </span>
          </div>
          <div v-if="currentDetail.reject_reason" class="sm:col-span-2">
            <span class="text-gray-600">Причина отклонения:</span>
            {{ currentDetail.reject_reason }}
          </div>
        </div>
      </div>

      <div class="rounded border bg-white p-6 shadow">
        <h3 class="mb-4 font-medium">Документы</h3>
        <div class="mb-4 flex flex-wrap gap-2">
          <select v-model="docType" class="rounded border px-3 py-2">
            <option value="signed_application">Скан заявления</option>
            <option value="parent_letter">Письмо родителя</option>
            <option value="voice_message">Голосовое сообщение</option>
          </select>
          <input
            ref="fileInput"
            type="file"
            class="hidden"
            accept=".pdf,.jpg,.jpeg,.png,.mp3,.m4a,.wav"
            @change="onFileChange"
          />
          <button
            v-if="isPending"
            type="button"
            class="rounded bg-gray-200 px-4 py-2 hover:bg-gray-300 disabled:opacity-50"
            :disabled="uploading"
            @click="triggerUpload"
          >
            {{ uploading ? "Загрузка..." : "Прикрепить файл" }}
          </button>
        </div>
        <ul v-if="currentDetail.documents?.length" class="list-disc space-y-1 pl-5">
          <li
            v-for="doc in currentDetail.documents"
            :key="doc.id"
          >
            {{ documentTypeLabel(doc.document_type) }} ({{ doc.id.slice(0, 8) }})
          </li>
        </ul>
        <p v-else class="text-gray-500">Нет прикреплённых документов.</p>
      </div>

      <div
        v-if="isPending"
        class="rounded border bg-white p-6 shadow"
      >
        <h3 class="mb-4 font-medium">Решение (воспитатель)</h3>
        <div class="flex flex-wrap gap-4">
          <label class="flex items-center gap-2">
            <input v-model="decideStatus" type="radio" value="approved" />
            Одобрить
          </label>
          <label class="flex items-center gap-2">
            <input v-model="decideStatus" type="radio" value="rejected" />
            Отклонить
          </label>
        </div>
        <div v-if="decideStatus === 'rejected'" class="mt-4">
          <label class="mb-1 block text-sm">Причина отклонения</label>
          <textarea
            v-model="rejectReason"
            rows="2"
            class="w-full rounded border px-3 py-2"
          />
        </div>
        <button
          type="button"
          class="mt-4 rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
          :disabled="deciding"
          @click="decide"
        >
          {{ deciding ? "Сохранение..." : "Сохранить решение" }}
        </button>
      </div>
    </template>
  </div>
</template>
