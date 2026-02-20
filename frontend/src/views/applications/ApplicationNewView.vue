<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { format, parseISO } from "date-fns";
import { ru } from "date-fns/locale";
import { VueDatePicker } from "@vuepic/vue-datepicker";
import "@vuepic/vue-datepicker/dist/main.css";
import { useTheme } from "@/composables/useTheme";
import { useApplicationsStore } from "@/stores/applications.store";
import Button from "@/components/ui/button/Button.vue";
import Card from "@/components/ui/card/Card.vue";
import CardContent from "@/components/ui/card/CardContent.vue";
import CardHeader from "@/components/ui/card/CardHeader.vue";
import CardTitle from "@/components/ui/card/CardTitle.vue";
import CardFooter from "@/components/ui/card/CardFooter.vue";
import Input from "@/components/ui/input/Input.vue";
import Label from "@/components/ui/label/Label.vue";
import Textarea from "@/components/ui/textarea/Textarea.vue";
import Alert from "@/components/ui/alert/Alert.vue";
import { Calendar, Send } from "lucide-vue-next";

const datePickerFormats = { input: "dd.MM.yyyy" };

const router = useRouter();
const store = useApplicationsStore();
const { isDark } = useTheme();
const leaveDate = ref("");
const leaveTime = ref("12:00");
const returnDate = ref("");
const returnTime = ref("18:00");
const reason = ref("");
const contactPhone = ref("");
const submitting = ref(false);
const error = ref("");
const fieldErrors = ref<Record<string, string>>({});

const MIN_YEAR = 2000;
const MAX_YEAR = 2100;
const PHONE_DIGITS_REGEX = /^[78]?\d{10}$/;

function buildIso(date: string, time: string): string {
  if (!date) return "";
  const [h, m] = (time || "00:00").split(":");
  return `${date}T${h || "00"}:${m || "00"}:00.000Z`;
}

function yearFromDateStr(dateStr: string): number | null {
  if (!dateStr) return null;
  const y = new Date(dateStr + "T00:00:00Z").getUTCFullYear();
  return Number.isNaN(y) ? null : y;
}

function validatePhone(phone: string): boolean {
  const digits = phone.replace(/\D/g, "");
  return PHONE_DIGITS_REGEX.test(digits);
}

function validate(): boolean {
  fieldErrors.value = {};
  error.value = "";

  if (!leaveDate.value?.trim()) {
    fieldErrors.value.leave = "Укажите дату выхода.";
  }
  if (!returnDate.value?.trim()) {
    fieldErrors.value.return = "Укажите дату возвращения.";
  }
  if (!reason.value.trim()) {
    fieldErrors.value.reason = "Укажите цель выхода.";
  }
  if (!contactPhone.value.trim()) {
    fieldErrors.value.contact_phone = "Укажите контактный телефон.";
  } else if (!validatePhone(contactPhone.value)) {
    fieldErrors.value.contact_phone = "Введите корректный номер телефона.";
  }

  const leaveYear = yearFromDateStr(leaveDate.value);
  const returnYear = yearFromDateStr(returnDate.value);
  if (leaveYear != null && (leaveYear < MIN_YEAR || leaveYear > MAX_YEAR)) {
    fieldErrors.value.leave = fieldErrors.value.leave || "Укажите дату в диапазоне 2000–2100.";
  }
  if (returnYear != null && (returnYear < MIN_YEAR || returnYear > MAX_YEAR)) {
    fieldErrors.value.return = fieldErrors.value.return || "Укажите дату в диапазоне 2000–2100.";
  }

  if (leaveDate.value && returnDate.value) {
    const leaveIso = buildIso(leaveDate.value, leaveTime.value);
    const returnIso = buildIso(returnDate.value, returnTime.value);
    if (new Date(returnIso) < new Date(leaveIso)) {
      fieldErrors.value.return = fieldErrors.value.return || "Дата возвращения не может быть раньше даты выхода.";
    }
  }

  return Object.keys(fieldErrors.value).length === 0;
}

async function submit() {
  if (!validate()) return;

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
    <Card>
      <form novalidate @submit.prevent="submit">
        <CardHeader>
          <CardTitle>Данные заявления</CardTitle>
        </CardHeader>
        <CardContent class="space-y-4">
          <div class="space-y-2">
            <Label class="flex items-center gap-2">
              <Calendar class="size-4" />
              Дата и время выхода
            </Label>
            <div class="flex flex-col gap-2 sm:flex-row">
              <VueDatePicker
                :model-value="leaveDate ? parseISO(leaveDate + 'T12:00:00') : null"
                :formats="datePickerFormats"
                :locale="ru"
                :dark="isDark"
                :action-row="{ cancelBtnLabel: 'Отмена', selectBtnLabel: 'Выбрать' }"
                class="min-w-0 flex-1"
                @update:model-value="(v: Date | null) => leaveDate = v ? format(v, 'yyyy-MM-dd') : ''"
              />
              <Input v-model="leaveTime" type="time" class="w-full sm:w-28" />
            </div>
            <p v-if="fieldErrors.leave" class="text-sm text-destructive">{{ fieldErrors.leave }}</p>
          </div>
          <div class="space-y-2">
            <Label class="flex items-center gap-2">
              <Calendar class="size-4" />
              Дата и время возвращения
            </Label>
            <div class="flex flex-col gap-2 sm:flex-row">
              <VueDatePicker
                :model-value="returnDate ? parseISO(returnDate + 'T12:00:00') : null"
                :formats="datePickerFormats"
                :locale="ru"
                :dark="isDark"
                :action-row="{ cancelBtnLabel: 'Отмена', selectBtnLabel: 'Выбрать' }"
                class="min-w-0 flex-1"
                @update:model-value="(v: Date | null) => returnDate = v ? format(v, 'yyyy-MM-dd') : ''"
              />
              <Input v-model="returnTime" type="time" class="w-full sm:w-28" />
            </div>
            <p v-if="fieldErrors.return" class="text-sm text-destructive">{{ fieldErrors.return }}</p>
          </div>
          <div class="space-y-2">
            <Label>Цель выхода</Label>
            <Textarea v-model="reason" :rows="3" />
            <p v-if="fieldErrors.reason" class="text-sm text-destructive">{{ fieldErrors.reason }}</p>
          </div>
          <div class="space-y-2">
            <Label>Контактный телефон</Label>
            <Input v-model="contactPhone" type="tel" />
            <p v-if="fieldErrors.contact_phone" class="text-sm text-destructive">{{ fieldErrors.contact_phone }}</p>
          </div>
          <Alert variant="success">
            Для несовершеннолетних необходимо прикрепить голосовое сообщение от родителя с подтверждением согласия на выход (после создания заявления — в разделе «Документы»).
          </Alert>
          <Alert v-if="error" variant="destructive">{{ error }}</Alert>
        </CardContent>
        <CardFooter class="flex gap-2">
          <Button type="submit" :disabled="submitting">
            <Send class="mr-2 size-4" />
            {{ submitting ? "Сохранение..." : "Подать заявление" }}
          </Button>
          <Button type="button" variant="outline" @click="router.push({ name: 'applications' })">
            Отмена
          </Button>
        </CardFooter>
      </form>
    </Card>
  </div>
</template>
