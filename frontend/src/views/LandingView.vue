<script setup lang="ts">
import Button from "@/components/ui/button/Button.vue";
import {
  FileText,
  LogIn,
  ArrowRight,
  Calendar,
  ShieldCheck,
  Users,
  ClipboardList,
  BookOpen,
} from "lucide-vue-next";
</script>

<template>
  <div class="relative overflow-hidden">
    <!-- Subtle gradient background -->
    <div
      class="pointer-events-none absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-primary/10 dark:from-primary/10 dark:to-primary/5"
      aria-hidden="true"
    />

    <!-- Hero -->
    <section class="relative mx-auto max-w-4xl px-4 py-16 sm:py-24 md:py-32">
      <div class="mx-auto max-w-2xl text-center">
        <h2 class="text-balance text-3xl font-bold tracking-tight sm:text-4xl md:text-5xl">
          Заявления на выход
          <span class="block text-primary">в одном месте</span>
        </h2>
        <p class="mt-4 text-lg text-muted-foreground sm:text-xl">
          Подавайте заявки на выход из кампуса, указывайте даты и цель, прикладывайте документы. Воспитатели рассматривают заявки — вы видите статус в реальном времени.
        </p>
        <div class="mt-10 flex flex-wrap items-center justify-center gap-4">
          <router-link to="/applications">
            <Button size="lg" class="gap-2 shadow-sm">
              Перейти к заявлениям
              <ArrowRight class="size-4" />
            </Button>
          </router-link>
          <router-link to="/login">
            <Button variant="outline" size="lg" class="gap-2">
              <LogIn class="size-4" />
              Войти
            </Button>
          </router-link>
        </div>
      </div>
    </section>

    <!-- О продукте -->
    <section class="relative mx-auto max-w-4xl px-4 py-12 sm:py-16">
      <h3 class="text-center text-2xl font-semibold sm:text-3xl">О продукте</h3>
      <p class="mx-auto mt-4 max-w-2xl text-center text-muted-foreground">
        <strong>Кампус Сириус</strong> — цифровая система для жизни в кампусе. Модуль заявлений на выход позволяет
        жителям подавать заявки на выезд с указанием времени выхода и возвращения, цели и контактов.
        Воспитатели одобряют или отклоняют заявки; для несовершеннолетних можно приложить скан заявления
        от родителя или голосовое сообщение. Всё хранится в одном месте, без бумажной волокиты.
      </p>
    </section>

    <!-- Для кого -->
    <section class="relative mx-auto max-w-4xl px-4 py-12 sm:py-16">
      <h3 class="text-center text-2xl font-semibold sm:text-3xl">Для кого</h3>
      <div class="mt-8 grid gap-6 sm:grid-cols-2">
        <article
          class="rounded-xl border border-border bg-card/50 p-6 shadow-sm backdrop-blur-sm dark:bg-card/30"
        >
          <div class="flex size-12 items-center justify-center rounded-lg bg-primary/10 text-primary">
            <Users class="size-6" />
          </div>
          <h4 class="mt-4 text-lg font-semibold">Жители кампуса</h4>
          <p class="mt-2 text-sm text-muted-foreground">
            Подавайте заявки на выход, указывайте даты и время, цель и контактный телефон. При необходимости прикрепляйте документы. Отслеживайте статус: ожидает, одобрено или отклонено.
          </p>
        </article>
        <article
          class="rounded-xl border border-border bg-card/50 p-6 shadow-sm backdrop-blur-sm dark:bg-card/30"
        >
          <div class="flex size-12 items-center justify-center rounded-lg bg-primary/10 text-primary">
            <ShieldCheck class="size-6" />
          </div>
          <h4 class="mt-4 text-lg font-semibold">Воспитатели</h4>
          <p class="mt-2 text-sm text-muted-foreground">
            Рассматривайте заявки жителей, одобряйте или отклоняйте с указанием причины. Видите полную информацию по заявителю, датам и приложенным документам.
          </p>
        </article>
      </div>
    </section>

    <!-- Как это работает -->
    <section class="relative mx-auto max-w-4xl px-4 py-12 sm:py-16">
      <h3 class="text-center text-2xl font-semibold sm:text-3xl">Как это работает</h3>
      <ul class="mx-auto mt-8 max-w-xl space-y-4 text-muted-foreground">
        <li class="flex gap-3">
          <span class="flex size-8 shrink-0 items-center justify-center rounded-full bg-primary/10 text-sm font-medium text-primary">1</span>
          <span><strong class="text-foreground">Войдите</strong> в систему под своей учётной записью.</span>
        </li>
        <li class="flex gap-3">
          <span class="flex size-8 shrink-0 items-center justify-center rounded-full bg-primary/10 text-sm font-medium text-primary">2</span>
          <span><strong class="text-foreground">Создайте заявление</strong> — укажите дату и время выхода и возвращения, цель выхода и контактный телефон.</span>
        </li>
        <li class="flex gap-3">
          <span class="flex size-8 shrink-0 items-center justify-center rounded-full bg-primary/10 text-sm font-medium text-primary">3</span>
          <span><strong class="text-foreground">При необходимости приложите документы</strong> — скан заявления, письмо от родителя (для несовершеннолетних) или голосовое сообщение.</span>
        </li>
        <li class="flex gap-3">
          <span class="flex size-8 shrink-0 items-center justify-center rounded-full bg-primary/10 text-sm font-medium text-primary">4</span>
          <span><strong class="text-foreground">Дождитесь решения</strong> — воспитатель одобрит или отклонит заявку. Статус можно смотреть в списке заявлений.</span>
        </li>
      </ul>
    </section>

    <!-- Возможности + CTA cards -->
    <section class="relative mx-auto max-w-4xl px-4 py-12 sm:py-16">
      <h3 class="text-center text-2xl font-semibold sm:text-3xl">Возможности</h3>
      <div class="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <article
          class="rounded-xl border border-border bg-card/50 p-6 shadow-sm backdrop-blur-sm transition-shadow hover:shadow-md dark:bg-card/30"
        >
          <div class="flex size-12 items-center justify-center rounded-lg bg-primary/10 text-primary">
            <FileText class="size-6" />
          </div>
          <h4 class="mt-4 text-lg font-semibold">Заявления</h4>
          <p class="mt-2 text-sm text-muted-foreground">
            Создавайте заявки на выход, указывайте даты и цель. Статусы «Ожидает», «Одобрено» или «Отклонено» — всё в одном списке.
          </p>
          <router-link
            to="/applications"
            class="mt-4 inline-flex items-center gap-1 text-sm font-medium text-primary hover:underline"
          >
            К заявлениям
            <ArrowRight class="size-4" />
          </router-link>
        </article>
        <article
          class="rounded-xl border border-border bg-card/50 p-6 shadow-sm backdrop-blur-sm transition-shadow hover:shadow-md dark:bg-card/30"
        >
          <div class="flex size-12 items-center justify-center rounded-lg bg-primary/10 text-primary">
            <Calendar class="size-6" />
          </div>
          <h4 class="mt-4 text-lg font-semibold">Фильтры</h4>
          <p class="mt-2 text-sm text-muted-foreground">
            Фильтруйте заявления по статусу, датам, подъезду и комнате — удобно искать свои или обрабатывать списки.
          </p>
        </article>
        <article
          class="rounded-xl border border-border bg-card/50 p-6 shadow-sm backdrop-blur-sm transition-shadow hover:shadow-md dark:bg-card/30"
        >
          <div class="flex size-12 items-center justify-center rounded-lg bg-primary/10 text-primary">
            <ClipboardList class="size-6" />
          </div>
          <h4 class="mt-4 text-lg font-semibold">Документы</h4>
          <p class="mt-2 text-sm text-muted-foreground">
            Прикрепляйте к заявлению подписанное заявление, письмо от родителя или голосовое сообщение — всё хранится в системе.
          </p>
        </article>
      </div>
      <div class="mt-12 flex flex-wrap justify-center gap-4">
        <router-link to="/applications">
          <Button size="lg" class="gap-2">
            Перейти к заявлениям
            <ArrowRight class="size-4" />
          </Button>
        </router-link>
        <router-link to="/login">
          <Button variant="outline" size="lg" class="gap-2">
            <LogIn class="size-4" />
            Войти
          </Button>
        </router-link>
      </div>
    </section>

    <!-- Footer -->
    <footer class="relative border-t border-border bg-card/30 px-4 py-8 dark:bg-card/20">
      <div class="mx-auto flex max-w-4xl flex-wrap items-center justify-between gap-4">
        <p class="text-sm text-muted-foreground">
          Кампус Сириус — заявления на выход и жизнь в кампусе.
        </p>
        <p class="text-sm text-muted-foreground">
          <BookOpen class="mr-1 inline size-4" aria-hidden="true" />
          Ядерные Бобры
        </p>
      </div>
    </footer>
  </div>
</template>
