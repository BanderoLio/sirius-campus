<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { storeToRefs } from "pinia";
import { format, parseISO } from "date-fns";
import { ru } from "date-fns/locale";
import { useTheme } from "@/composables/useTheme";
import { usePatrolsStore } from "@/stores/patrols.store";
import Button from "@/components/ui/button/Button.vue";
import Card from "@/components/ui/card/Card.vue";
import CardContent from "@/components/ui/card/CardContent.vue";
import CardHeader from "@/components/ui/card/CardHeader.vue";
import CardTitle from "@/components/ui/card/CardTitle.vue";
import Badge from "@/components/ui/badge/Badge.vue";
import Alert from "@/components/ui/alert/Alert.vue";
import Input from "@/components/ui/input/Input.vue";
import Label from "@/components/ui/label/Label.vue";
import Textarea from "@/components/ui/textarea/Textarea.vue";
import {
  Calendar,
  Building,
  DoorOpen,
  ArrowLeft,
  CheckCircle,
  XCircle,
  Clock,
  User,
} from "lucide-vue-next";

const route = useRoute();
const router = useRouter();
const store = usePatrolsStore();
const { isDark } = useTheme();
const { currentDetail: patrol, loading, error } = storeToRefs(store);

const editingEntryId = ref<string | null>(null);
const entryIsPresent = ref<boolean | null>(null);
const entryAbsenceReason = ref("");

const patrolId = computed(() => route.params.id as string);

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

function formatDate(dateStr: string) {
  return format(parseISO(dateStr), "dd MMM yyyy", { locale: ru });
}

function formatDateTime(dateStr: string) {
  return format(parseISO(dateStr), "dd MMM yyyy, HH:mm", { locale: ru });
}

function formatTime(dateStr: string) {
  return format(parseISO(dateStr), "HH:mm");
}

function goBack() {
  router.push({ name: "patrols" });
}

async function completePatrol() {
  if (!patrol.value) return;
  try {
    await store.complete(patrol.value.patrol_id);
  } catch (e) {
    // Error handled by store
  }
}

async function deletePatrol() {
  if (!patrol.value) return;
  if (!confirm("Вы уверены, что хотите удалить этот обход?")) return;
  try {
    await store.remove(patrol.value.patrol_id);
    goBack();
  } catch (e) {
    // Error handled by store
  }
}

function startEditEntry(entryId: string, isPresent: boolean | null, reason: string | null) {
  editingEntryId.value = entryId;
  entryIsPresent.value = isPresent;
  entryAbsenceReason.value = reason ?? "";
}

function cancelEditEntry() {
  editingEntryId.value = null;
  entryIsPresent.value = null;
  entryAbsenceReason.value = "";
}

async function saveEntry(entryId: string) {
  if (!patrol.value) return;
  try {
    await store.updateEntry(patrol.value.patrol_id, entryId, {
      is_present: entryIsPresent.value,
      absence_reason: entryAbsenceReason.value || null,
    });
    cancelEditEntry();
  } catch (e) {
    // Error handled by store
  }
}

onMounted(() => {
  store.fetchOne(patrolId.value);
});
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center gap-4">
      <Button variant="ghost" size="icon" @click="goBack">
        <ArrowLeft class="size-5" />
      </Button>
      <h2 class="text-xl font-semibold">Обход</h2>
    </div>

    <Alert v-if="error" variant="destructive">{{ error }}</Alert>
    <p v-if="loading && !patrol" class="text-muted-foreground">Загрузка...</p>

    <template v-else-if="patrol">
      <Card>
        <CardHeader>
          <CardTitle class="flex items-center justify-between">
            <span>{{ formatDate(patrol.date) }}</span>
            <Badge :variant="statusVariant(patrol.status)">
              {{ statusLabel(patrol.status) }}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div class="grid grid-cols-2 gap-4 sm:grid-cols-4">
            <div class="flex items-center gap-2">
              <Building class="size-4 text-muted-foreground" />
              <span>{{ buildingLabel(patrol.building) }}</span>
            </div>
            <div class="flex items-center gap-2">
              <DoorOpen class="size-4 text-muted-foreground" />
              <span>Подъезд {{ patrol.entrance }}</span>
            </div>
            <div class="flex items-center gap-2">
              <Clock class="size-4 text-muted-foreground" />
              <span>Начало: {{ formatTime(patrol.started_at) }}</span>
            </div>
            <div v-if="patrol.submitted_at" class="flex items-center gap-2">
              <CheckCircle class="size-4 text-muted-foreground" />
              <span>Завершён: {{ formatTime(patrol.submitted_at) }}</span>
            </div>
          </div>

          <div v-if="patrol.status === 'in_progress'" class="mt-6 flex gap-2">
            <Button @click="completePatrol">
              <CheckCircle class="mr-2 size-4" />
              Завершить обход
            </Button>
            <Button variant="destructive" @click="deletePatrol">
              <XCircle class="mr-2 size-4" />
              Удалить
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Проверенные студенты</CardTitle>
        </CardHeader>
        <CardContent>
          <div v-if="patrol.entries.length === 0" class="text-muted-foreground">
            Нет проверенных студентов
          </div>
          <div v-else class="space-y-2">
            <div
              v-for="entry in patrol.entries"
              :key="entry.patrol_entry_id"
              class="flex flex-col gap-2 rounded-lg border p-4 sm:flex-row sm:items-center sm:justify-between"
            >
              <div class="flex items-center gap-3">
                <User class="size-5 text-muted-foreground" />
                <div>
                  <p class="font-medium">Комната {{ entry.room }}</p>
                  <p v-if="entry.checked_at" class="text-sm text-muted-foreground">
                    Проверено: {{ formatDateTime(entry.checked_at) }}
                  </p>
                </div>
              </div>

              <div v-if="editingEntryId === entry.patrol_entry_id" class="flex flex-col gap-2 sm:flex-row">
                <div class="flex gap-2">
                  <Button
                    size="sm"
                    :variant="entryIsPresent === true ? 'default' : 'outline'"
                    @click="entryIsPresent = true"
                  >
                    Присутствует
                  </Button>
                  <Button
                    size="sm"
                    :variant="entryIsPresent === false ? 'destructive' : 'outline'"
                    @click="entryIsPresent = false"
                  >
                    Отсутствует
                  </Button>
                </div>
                <div v-if="entryIsPresent === false" class="flex gap-2">
                  <Input
                    v-model="entryAbsenceReason"
                    placeholder="Причина отсутствия"
                    class="w-48"
                  />
                </div>
                <div class="flex gap-2">
                  <Button size="sm" variant="secondary" @click="cancelEditEntry">Отмена</Button>
                  <Button size="sm" @click="saveEntry(entry.patrol_entry_id)">Сохранить</Button>
                </div>
              </div>

              <div v-else class="flex items-center gap-2">
                <Badge v-if="entry.is_present === true" variant="success">
                  <CheckCircle class="mr-1 size-3" />
                  Присутствует
                </Badge>
                <Badge v-else-if="entry.is_present === false" variant="destructive">
                  <XCircle class="mr-1 size-3" />
                  Отсутствует
                </Badge>
                <Badge v-else variant="secondary">
                  <Clock class="mr-1 size-3" />
                  Не проверено
                </Badge>
                <Button
                  v-if="patrol.status === 'in_progress'"
                  size="sm"
                  variant="outline"
                  @click="startEditEntry(entry.patrol_entry_id, entry.is_present, entry.absence_reason)"
                >
                  Изменить
                </Button>
              </div>

              <p v-if="entry.absence_reason && entry.is_present === false" class="text-sm text-muted-foreground">
                Причина: {{ entry.absence_reason }}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </template>
  </div>
</template>
