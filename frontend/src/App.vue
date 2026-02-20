<script setup lang="ts">
import { RouterView } from "vue-router";
import { useTheme } from "@/composables/useTheme";
import Button from "@/components/ui/button/Button.vue";
import { Sun, Moon } from "lucide-vue-next";

const { isDark, toggleTheme } = useTheme();
</script>

<template>
  <div class="min-h-screen bg-background text-foreground">
    <header class="border-b border-border bg-card px-4 py-3 shadow-sm">
      <div class="mx-auto flex max-w-4xl flex-wrap items-center justify-between gap-4">
        <router-link to="/" class="text-xl font-semibold hover:opacity-90">Кампус Сириус</router-link>
        <div class="flex flex-wrap items-center gap-4">
          <nav class="flex gap-4">
            <router-link
              to="/applications"
              class="text-muted-foreground hover:text-foreground"
              active-class="font-medium text-foreground"
              >Заявления</router-link
            >
          </nav>
          <Button
            variant="ghost"
            size="icon"
            class="bg-transparent text-primary hover:bg-accent/50 hover:text-primary"
            :aria-label="isDark ? 'Включить светлую тему' : 'Включить тёмную тему'"
            @click="toggleTheme"
          >
            <Sun v-if="isDark" class="size-5 shrink-0" />
            <Moon v-else class="size-5 shrink-0" />
          </Button>
        </div>
      </div>
    </header>
    <main class="mx-auto max-w-4xl px-4 py-6">
      <RouterView />
    </main>
  </div>
</template>
