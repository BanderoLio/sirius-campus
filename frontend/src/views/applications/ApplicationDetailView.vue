<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { storeToRefs } from "pinia";
import { useApplicationsStore } from "@/stores/applications.store";
import { formatDateTime } from "@/utils/date.utils";
import { getDocumentDownloadUrl } from "@/api/applications.api";
import Button from "@/components/ui/button/Button.vue";
import Card from "@/components/ui/card/Card.vue";
import CardContent from "@/components/ui/card/CardContent.vue";
import CardHeader from "@/components/ui/card/CardHeader.vue";
import CardTitle from "@/components/ui/card/CardTitle.vue";
import Label from "@/components/ui/label/Label.vue";
import Select from "@/components/ui/select/Select.vue";
import Textarea from "@/components/ui/textarea/Textarea.vue";
import Badge from "@/components/ui/badge/Badge.vue";
import Alert from "@/components/ui/alert/Alert.vue";

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
const downloadingDocId = ref<string | null>(null);

const id = computed(() => route.params.id as string);
const isPending = computed(() => currentDetail.value?.status === "pending");
const canDecide = computed(() => currentDetail.value?.can_decide === true);

const statusVariant = computed(() => {
  const s = currentDetail.value?.status;
  if (s === "approved") return "success";
  if (s === "rejected") return "destructive";
  return "secondary";
});

const statusLabel = (s: string) => {
  if (s === "pending") return "Ожидает";
  if (s === "approved") return "Одобрено";
  if (s === "rejected") return "Отклонено";
  return s;
};

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

async function downloadDoc(documentId: string) {
  downloadingDocId.value = documentId;
  try {
    const { url } = await getDocumentDownloadUrl(id.value, documentId);
    const downloadUrl = url.replace(/\bminio\b/g, "localhost");
    window.open(downloadUrl, "_blank", "noopener,noreferrer");
  } finally {
    downloadingDocId.value = null;
  }
}
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center gap-4">
      <Button variant="ghost" size="sm" @click="router.push({ name: 'applications' })">
        ← К списку
      </Button>
      <h2 class="text-xl font-semibold">Заявление</h2>
    </div>

    <Alert v-if="error" variant="destructive">{{ error }}</Alert>
    <p v-if="loading && !currentDetail" class="text-muted-foreground">Загрузка...</p>

    <template v-else-if="currentDetail">
      <Card>
        <CardContent class="p-6">
          <div class="grid gap-4 sm:grid-cols-2">
            <div v-if="currentDetail.user_name" class="sm:col-span-2">
              <span class="text-muted-foreground">ФИО:</span>
              {{ currentDetail.user_name }}
            </div>
            <div v-if="currentDetail.room != null && currentDetail.room !== ''">
              <span class="text-muted-foreground">Комната:</span>
              {{ currentDetail.room }}
            </div>
            <div v-if="currentDetail.entrance != null">
              <span class="text-muted-foreground">Подъезд:</span>
              {{ currentDetail.entrance }}
            </div>
            <div>
              <span class="text-muted-foreground">Выход:</span>
              {{ formatDateTime(currentDetail.leave_time) }}
            </div>
            <div>
              <span class="text-muted-foreground">Возвращение:</span>
              {{ formatDateTime(currentDetail.return_time) }}
            </div>
            <div class="sm:col-span-2">
              <span class="text-muted-foreground">Цель:</span>
              {{ currentDetail.reason }}
            </div>
            <div>
              <span class="text-muted-foreground">Телефон:</span>
              {{ currentDetail.contact_phone }}
            </div>
            <div>
              <span class="text-muted-foreground">Статус:</span>
              <Badge :variant="statusVariant">{{ statusLabel(currentDetail.status) }}</Badge>
            </div>
            <div v-if="currentDetail.reject_reason" class="sm:col-span-2">
              <span class="text-muted-foreground">Причина отклонения:</span>
              {{ currentDetail.reject_reason }}
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Документы</CardTitle>
        </CardHeader>
        <CardContent>
          <Alert v-if="currentDetail.is_minor" variant="success" class="mb-4">
            Для несовершеннолетних необходимо прикрепить голосовое сообщение от родителя с подтверждением согласия на выход.
          </Alert>
          <div class="mb-4 flex flex-wrap items-center gap-2">
            <Select v-model="docType" class="w-48">
              <option value="signed_application">Скан заявления</option>
              <option value="parent_letter">Письмо родителя</option>
              <option value="voice_message">Голосовое сообщение</option>
            </Select>
            <input
              ref="fileInput"
              type="file"
              class="hidden"
              accept=".pdf,.jpg,.jpeg,.png,.mp3,.m4a,.wav"
              @change="onFileChange"
            />
            <Button
              v-if="isPending"
              variant="secondary"
              :disabled="uploading"
              @click="triggerUpload"
            >
              {{ uploading ? "Загрузка..." : "Прикрепить файл" }}
            </Button>
          </div>
          <ul v-if="currentDetail.documents?.length" class="list-disc space-y-1 pl-5">
            <li
              v-for="doc in currentDetail.documents"
              :key="doc.id"
              class="flex items-center justify-between gap-3"
            >
              <span>
                {{ documentTypeLabel(doc.document_type) }} ({{ doc.id.slice(0, 8) }})
              </span>
              <Button
                variant="outline"
                size="sm"
                :disabled="downloadingDocId === doc.id"
                @click="downloadDoc(doc.id)"
              >
                {{ downloadingDocId === doc.id ? "..." : "Скачать" }}
              </Button>
            </li>
          </ul>
          <p v-else class="text-muted-foreground">Нет прикреплённых документов.</p>
        </CardContent>
      </Card>

      <Card v-if="isPending && canDecide">
        <CardHeader>
          <CardTitle>Решение (воспитатель)</CardTitle>
        </CardHeader>
        <CardContent class="space-y-4">
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
          <div v-if="decideStatus === 'rejected'" class="space-y-2">
            <Label>Причина отклонения</Label>
            <Textarea v-model="rejectReason" :rows="2" />
          </div>
          <Button :disabled="deciding" @click="decide">
            {{ deciding ? "Сохранение..." : "Сохранить решение" }}
          </Button>
        </CardContent>
      </Card>
    </template>
  </div>
</template>
