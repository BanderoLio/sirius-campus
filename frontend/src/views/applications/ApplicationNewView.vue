<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
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
    <Card>
      <form @submit.prevent="submit">
        <CardHeader>
          <CardTitle>Данные заявления</CardTitle>
        </CardHeader>
        <CardContent class="space-y-4">
          <div class="space-y-2">
            <Label>Дата и время выхода</Label>
            <div class="flex gap-2">
              <Input v-model="leaveDate" type="date" class="flex-1" required />
              <Input v-model="leaveTime" type="time" class="w-28" />
            </div>
          </div>
          <div class="space-y-2">
            <Label>Дата и время возвращения</Label>
            <div class="flex gap-2">
              <Input v-model="returnDate" type="date" class="flex-1" required />
              <Input v-model="returnTime" type="time" class="w-28" />
            </div>
          </div>
          <div class="space-y-2">
            <Label>Цель выхода</Label>
            <Textarea v-model="reason" :rows="3" required />
          </div>
          <div class="space-y-2">
            <Label>Контактный телефон</Label>
            <Input v-model="contactPhone" type="tel" required />
          </div>
          <Alert variant="success">
            Для несовершеннолетних необходимо прикрепить голосовое сообщение от родителя с подтверждением согласия на выход (после создания заявления — в разделе «Документы»).
          </Alert>
          <Alert v-if="error" variant="destructive">{{ error }}</Alert>
        </CardContent>
        <CardFooter class="flex gap-2">
          <Button type="submit" :disabled="submitting">
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
