<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { format, parseISO } from "date-fns";
import { ru } from "date-fns/locale";
import { VueDatePicker } from "@vuepic/vue-datepicker";
import "@vuepic/vue-datepicker/dist/main.css";
import { useTheme } from "@/composables/useTheme";
import { usePatrolsStore } from "@/stores/patrols.store";
import Button from "@/components/ui/button/Button.vue";
import Card from "@/components/ui/card/Card.vue";
import CardContent from "@/components/ui/card/CardContent.vue";
import CardHeader from "@/components/ui/card/CardHeader.vue";
import CardTitle from "@/components/ui/card/CardTitle.vue";
import CardDescription from "@/components/ui/card/CardDescription.vue";
import Input from "@/components/ui/input/Input.vue";
import Label from "@/components/ui/label/Label.vue";
import Select from "@/components/ui/select/Select.vue";
import Alert from "@/components/ui/alert/Alert.vue";
import { ArrowLeft, Plus } from "lucide-vue-next";

const datePickerFormats = { input: "dd.MM.yyyy" };

const router = useRouter();
const store = usePatrolsStore();
const { isDark } = useTheme();

const date = ref<string>("");
const building = ref<string>("");
const entrance = ref<string>("");
const loading = ref(false);
const error = ref<string | null>(null);

function goBack() {
  router.push({ name: "patrols" });
}

async function createPatrol() {
  if (!date.value || !building.value || !entrance.value) {
    error.value = "Пожалуйста, заполните все поля";
    return;
  }

  loading.value = true;
  error.value = null;

  try {
    const created = await store.create({
      date: date.value,
      building: building.value,
      entrance: parseInt(entrance.value),
    });
    router.push({ name: "patrol-detail", params: { id: created.patrol_id } });
  } catch (e) {
    error.value = e instanceof Error ? e.message : "Ошибка создания обхода";
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  // Set default date to today
  date.value = format(new Date(), "yyyy-MM-dd");
});
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center gap-4">
      <Button variant="ghost" size="icon" @click="goBack">
        <ArrowLeft class="size-5" />
      </Button>
      <h2 class="text-xl font-semibold">Новый обход</h2>
    </div>

    <Alert v-if="error" variant="destructive">{{ error }}</Alert>

    <Card>
      <CardHeader>
        <CardTitle>Создать обход</CardTitle>
        <CardDescription>
          Заполните данные для начала нового сеанса обхода
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form class="space-y-4" @submit.prevent="createPatrol">
          <div class="space-y-2">
            <Label>Дата</Label>
            <VueDatePicker
              v-model="date"
              :formats="datePickerFormats"
              :locale="ru"
              :dark="isDark"
              :enable-time-picker="false"
              :action-row="{ cancelBtnLabel: 'Отмена', selectBtnLabel: 'Выбрать' }"
              @update:model-value="(v: Date | null) => { if (v) date = format(v, 'yyyy-MM-dd'); }"
            />
          </div>

          <div class="space-y-2">
            <Label>Корпус</Label>
            <Select
              v-model="building"
              :options="[
                { value: '8', label: 'Корпус 8' },
                { value: '9', label: 'Корпус 9' },
              ]"
              placeholder="Выберите корпус"
            />
          </div>

          <div class="space-y-2">
            <Label>Подъезд</Label>
            <Select
              v-model="entrance"
              :options="[
                { value: '1', label: '1' },
                { value: '2', label: '2' },
                { value: '3', label: '3' },
                { value: '4', label: '4' },
              ]"
              placeholder="Выберите подъезд"
            />
          </div>

          <div class="flex gap-2">
            <Button type="submit" :disabled="loading">
              <Plus v-if="!loading" class="mr-2 size-4" />
              {{ loading ? "Создание..." : "Создать обход" }}
            </Button>
            <Button type="button" variant="secondary" @click="goBack">Отмена</Button>
          </div>
        </form>
      </CardContent>
    </Card>
  </div>
</template>
