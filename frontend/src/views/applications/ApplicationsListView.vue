<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { storeToRefs } from "pinia";
import { useApplicationsStore } from "@/stores/applications.store";
import { formatDateTime } from "@/utils/date.utils";
import Button from "@/components/ui/button/Button.vue";
import Card from "@/components/ui/card/Card.vue";
import CardContent from "@/components/ui/card/CardContent.vue";
import Input from "@/components/ui/input/Input.vue";
import Label from "@/components/ui/label/Label.vue";
import Select from "@/components/ui/select/Select.vue";
import Badge from "@/components/ui/badge/Badge.vue";
import Alert from "@/components/ui/alert/Alert.vue";

const router = useRouter();
const store = useApplicationsStore();
const { items, loading, error, page, pages } = storeToRefs(store);
const statusFilter = ref<string>("");
const dateFrom = ref("");
const dateTo = ref("");
const entranceFilter = ref<string>("");
const roomFilter = ref("");

const statusLabel = (s: string) => {
  const map: Record<string, string> = {
    pending: "Ожидает",
    approved: "Одобрено",
    rejected: "Отклонено",
  };
  return map[s] ?? s;
};

const statusVariant = (s: string) => {
  if (s === "approved") return "success";
  if (s === "rejected") return "destructive";
  return "secondary";
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
    entrance: entranceFilter.value === "" ? undefined : Number(entranceFilter.value),
    room: roomFilter.value || undefined,
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
      <router-link to="/applications/new">
        <Button>Новое заявление</Button>
      </router-link>
    </div>

    <Card>
      <CardContent class="flex flex-wrap gap-4 p-6">
        <div class="space-y-2">
          <Label>Статус</Label>
          <Select v-model="statusFilter" @update:model-value="applyFilters">
            <option value="">Все</option>
            <option value="pending">Ожидает</option>
            <option value="approved">Одобрено</option>
            <option value="rejected">Отклонено</option>
          </Select>
        </div>
        <div class="space-y-2">
          <Label>Дата с</Label>
          <Input v-model="dateFrom" type="date" @update:model-value="applyFilters" />
        </div>
        <div class="space-y-2">
          <Label>Дата по</Label>
          <Input v-model="dateTo" type="date" @update:model-value="applyFilters" />
        </div>
        <div class="space-y-2">
          <Label>Подъезд</Label>
          <Select v-model="entranceFilter" @update:model-value="applyFilters">
            <option value="">Все</option>
            <option :value="1">1</option>
            <option :value="2">2</option>
            <option :value="3">3</option>
            <option :value="4">4</option>
          </Select>
        </div>
        <div class="space-y-2">
          <Label>Комната</Label>
          <Input
            v-model="roomFilter"
            type="text"
            placeholder="Напр. 301"
          />
        </div>
        <div class="flex items-end">
          <Button variant="secondary" @click="applyFilters">Применить</Button>
        </div>
      </CardContent>
    </Card>

    <Alert v-if="error" variant="destructive">{{ error }}</Alert>
    <p v-if="loading" class="text-muted-foreground">Загрузка...</p>

    <div v-else class="space-y-2">
      <Card
        v-for="app in items"
        :key="app.id"
        class="cursor-pointer transition hover:shadow-md"
        @click="openDetail(app.id)"
      >
        <CardContent class="p-4">
          <div class="flex flex-wrap items-center justify-between gap-2">
            <span class="font-medium">
              {{ formatDateTime(app.leave_time) }} — {{ formatDateTime(app.return_time) }}
            </span>
            <span v-if="app.user_name || app.room" class="text-sm text-muted-foreground">
              {{ [app.user_name, app.room ? `комн. ${app.room}` : null, app.entrance != null ? `подъезд ${app.entrance}` : null].filter(Boolean).join(", ") }}
            </span>
            <Badge :variant="statusVariant(app.status)">{{ statusLabel(app.status) }}</Badge>
          </div>
          <p class="mt-1 text-sm text-muted-foreground">{{ app.reason }}</p>
        </CardContent>
      </Card>
    </div>

    <div v-if="pages > 1" class="flex items-center justify-center gap-2">
      <Button
        variant="outline"
        size="sm"
        :disabled="page <= 1"
        @click="store.fetchList({ page: page - 1 })"
      >
        Назад
      </Button>
      <span class="text-sm text-muted-foreground">Стр. {{ page }} из {{ pages }}</span>
      <Button
        variant="outline"
        size="sm"
        :disabled="page >= pages"
        @click="store.fetchList({ page: page + 1 })"
      >
        Вперёд
      </Button>
    </div>
  </div>
</template>
