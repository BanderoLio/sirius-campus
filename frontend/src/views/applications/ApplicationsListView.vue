<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { storeToRefs } from "pinia";
import { format, parseISO } from "date-fns";
import { ru } from "date-fns/locale";
import { VueDatePicker } from "@vuepic/vue-datepicker";
import "@vuepic/vue-datepicker/dist/main.css";
import { useTheme } from "@/composables/useTheme";
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
import { CalendarClock, User, Plus } from "lucide-vue-next";

const datePickerFormats = { input: "dd.MM.yyyy" };

const router = useRouter();
const store = useApplicationsStore();
const { isDark } = useTheme();
const { items, loading, error, page, pages } = storeToRefs(store);
const statusFilter = ref<string>("all");
const dateFrom = ref("");
const dateTo = ref("");
const entranceFilter = ref<string>("all");
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
    status: statusFilter.value && statusFilter.value !== "all" ? statusFilter.value : undefined,
    date_from: dateFrom.value || undefined,
    date_to: dateTo.value || undefined,
    entrance: entranceFilter.value && entranceFilter.value !== "all" ? Number(entranceFilter.value) : undefined,
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
        <Button>
          <Plus class="mr-2 size-4" />
          Новое заявление
        </Button>
      </router-link>
    </div>

    <Card>
      <CardContent class="p-4 sm:p-6">
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <div class="space-y-2">
            <Label>Статус</Label>
            <Select
              v-model="statusFilter"
              :options="[
                { value: 'all', label: 'Все' },
                { value: 'pending', label: 'Ожидает' },
                { value: 'approved', label: 'Одобрено' },
                { value: 'rejected', label: 'Отклонено' },
              ]"
              placeholder="Все"
              @update:model-value="applyFilters"
            />
          </div>
          <div class="space-y-2">
            <Label>Дата с</Label>
            <VueDatePicker
              :model-value="dateFrom ? parseISO(dateFrom + 'T12:00:00') : null"
              :formats="datePickerFormats"
              :locale="ru"
              :dark="isDark"
              :action-row="{ cancelBtnLabel: 'Отмена', selectBtnLabel: 'Выбрать' }"
              @update:model-value="(v: Date | null) => { dateFrom = v ? format(v, 'yyyy-MM-dd') : ''; applyFilters(); }"
            />
          </div>
          <div class="space-y-2">
            <Label>Дата по</Label>
            <VueDatePicker
              :model-value="dateTo ? parseISO(dateTo + 'T12:00:00') : null"
              :formats="datePickerFormats"
              :locale="ru"
              :dark="isDark"
              :action-row="{ cancelBtnLabel: 'Отмена', selectBtnLabel: 'Выбрать' }"
              @update:model-value="(v: Date | null) => { dateTo = v ? format(v, 'yyyy-MM-dd') : ''; applyFilters(); }"
            />
          </div>
          <div class="space-y-2">
            <Label>Подъезд</Label>
            <Select
              v-model="entranceFilter"
              :options="[
                { value: 'all', label: 'Все' },
                { value: '1', label: '1' },
                { value: '2', label: '2' },
                { value: '3', label: '3' },
                { value: '4', label: '4' },
              ]"
              placeholder="Все"
              @update:model-value="applyFilters"
            />
          </div>
          <div class="space-y-2">
            <Label>Комната</Label>
            <Input
              v-model="roomFilter"
              type="text"
              placeholder="Напр. 301"
            />
          </div>
          <div class="flex items-end sm:col-span-2 lg:col-span-1">
            <Button variant="secondary" class="w-full sm:w-auto" @click="applyFilters">Применить</Button>
          </div>
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
          <div class="flex flex-col gap-2 sm:flex-row sm:flex-wrap sm:items-center sm:justify-between">
            <span class="flex items-center gap-1.5 font-medium">
              <CalendarClock class="size-4 shrink-0 text-muted-foreground" />
              {{ formatDateTime(app.leave_time) }} — {{ formatDateTime(app.return_time) }}
            </span>
            <span v-if="app.user_name || app.room" class="flex items-center gap-1.5 text-sm text-muted-foreground">
              <User class="size-4 shrink-0" />
              {{ [app.user_name, app.room ? `комн. ${app.room}` : null, app.entrance != null ? `подъезд ${app.entrance}` : null].filter(Boolean).join(", ") }}
            </span>
            <Badge :variant="statusVariant(app.status)" class="min-w-[7rem] justify-center">{{ statusLabel(app.status) }}</Badge>
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
