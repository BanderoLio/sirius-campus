<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { storeToRefs } from "pinia";
import { format, parseISO } from "date-fns";
import { ru } from "date-fns/locale";
import { VueDatePicker } from "@vuepic/vue-datepicker";
import "@vuepic/vue-datepicker/dist/main.css";
import { useTheme } from "@/composables/useTheme";
import { usePatrolsStore } from "@/stores/patrols.store";
import Button from "@/components/ui/button/Button.vue";
import Card from "@/components/ui/card/Card.vue";
import CardContent from "@/components/ui/card/CardContent.vue";
import Input from "@/components/ui/input/Input.vue";
import Label from "@/components/ui/label/Label.vue";
import Select from "@/components/ui/select/Select.vue";
import Badge from "@/components/ui/badge/Badge.vue";
import Alert from "@/components/ui/alert/Alert.vue";
import { Calendar, Building, DoorOpen, Plus, CheckCircle, Clock } from "lucide-vue-next";

const datePickerFormats = { input: "dd.MM.yyyy" };

const router = useRouter();
const store = usePatrolsStore();
const { isDark } = useTheme();
const { items, loading, error, page, pages } = storeToRefs(store);

const dateFilter = ref("");
const buildingFilter = ref<string>("all");
const entranceFilter = ref<string>("all");
const statusFilter = ref<string>("all");

const statusLabel = (s: string) => {
  const map: Record<string, string> = {
    in_progress: "В процессе",
    completed: "Завершён",
  };
  return map[s] ?? s;
};

const statusVariant = (s: string) => {
  if (s === "completed") return "success";
  return "secondary";
};

const buildingLabel = (b: string) => {
  return b === "8" ? "Корпус 8" : b === "9" ? "Корпус 9" : b;
};

function openDetail(id: string) {
  router.push({ name: "patrol-detail", params: { id } });
}

function openNew() {
  router.push({ name: "patrol-new" });
}

function applyFilters() {
  store.fetchList({
    page: 1,
    size: 20,
    date: dateFilter.value || undefined,
    building: buildingFilter.value && buildingFilter.value !== "all" ? buildingFilter.value : undefined,
    entrance: entranceFilter.value && entranceFilter.value !== "all" ? Number(entranceFilter.value) : undefined,
    status: statusFilter.value && statusFilter.value !== "all" ? statusFilter.value : undefined,
  });
}

function formatDate(dateStr: string) {
  return format(parseISO(dateStr), "dd MMM yyyy", { locale: ru });
}

function formatTime(dateStr: string) {
  return format(parseISO(dateStr), "HH:mm");
}

onMounted(() => {
  store.fetchList();
});
</script>

<template>
  <div class="space-y-4">
    <div class="flex flex-wrap items-center justify-between gap-4">
      <h2 class="text-xl font-semibold">Обходы</h2>
      <Button @click="openNew">
        <Plus class="mr-2 size-4" />
        Новый обход
      </Button>
    </div>

    <Card>
      <CardContent class="p-4 sm:p-6">
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div class="space-y-2">
            <Label>Дата</Label>
            <VueDatePicker
              :model-value="dateFilter ? parseISO(dateFilter + 'T12:00:00') : null"
              :formats="datePickerFormats"
              :locale="ru"
              :dark="isDark"
              :action-row="{ cancelBtnLabel: 'Отмена', selectBtnLabel: 'Выбрать' }"
              @update:model-value="(v: Date | null) => { dateFilter = v ? format(v, 'yyyy-MM-dd') : ''; applyFilters(); }"
            />
          </div>
          <div class="space-y-2">
            <Label>Корпус</Label>
            <Select
              v-model="buildingFilter"
              :options="[
                { value: 'all', label: 'Все' },
                { value: '8', label: 'Корпус 8' },
                { value: '9', label: 'Корпус 9' },
              ]"
              placeholder="Все"
              @update:model-value="applyFilters"
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
            <Label>Статус</Label>
            <Select
              v-model="statusFilter"
              :options="[
                { value: 'all', label: 'Все' },
                { value: 'in_progress', label: 'В процессе' },
                { value: 'completed', label: 'Завершён' },
              ]"
              placeholder="Все"
              @update:model-value="applyFilters"
            />
          </div>
        </div>
      </CardContent>
    </Card>

    <Alert v-if="error" variant="destructive">{{ error }}</Alert>
    <p v-if="loading" class="text-muted-foreground">Загрузка...</p>

    <div v-else class="space-y-2">
      <Card
        v-for="patrol in items"
        :key="patrol.patrol_id"
        class="cursor-pointer transition hover:shadow-md"
        @click="openDetail(patrol.patrol_id)"
      >
        <CardContent class="p-4">
          <div class="flex flex-col gap-2 sm:flex-row sm:flex-wrap sm:items-center sm:justify-between">
            <span class="flex items-center gap-1.5 font-medium">
              <Calendar class="size-4 shrink-0 text-muted-foreground" />
              {{ formatDate(patrol.date) }}
            </span>
            <span class="flex items-center gap-1.5 text-sm text-muted-foreground">
              <Building class="size-4 shrink-0" />
              {{ buildingLabel(patrol.building) }}
            </span>
            <span class="flex items-center gap-1.5 text-sm text-muted-foreground">
              <DoorOpen class="size-4 shrink-0" />
              Подъезд {{ patrol.entrance }}
            </span>
            <span class="flex items-center gap-1.5 text-sm text-muted-foreground">
              <Clock v-if="patrol.status === 'in_progress'" class="size-4 shrink-0" />
              <CheckCircle v-else class="size-4 shrink-0" />
              {{ statusLabel(patrol.status) }}
            </span>
            <Badge :variant="statusVariant(patrol.status)" class="min-w-[7rem] justify-center">
              {{ statusLabel(patrol.status) }}
            </Badge>
          </div>
          <p class="mt-1 text-sm text-muted-foreground">
            Начало: {{ formatTime(patrol.started_at) }}
            <span v-if="patrol.submitted_at"> | Завершение: {{ formatTime(patrol.submitted_at) }}</span>
          </p>
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
