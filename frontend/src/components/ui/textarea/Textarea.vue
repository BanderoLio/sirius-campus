<script setup lang="ts">
import { cn } from "@/lib/utils";

interface Props {
  modelValue?: string;
  class?: string;
  placeholder?: string;
  disabled?: boolean;
  rows?: number;
}

const props = withDefaults(defineProps<Props>(), {
  rows: 3,
});

const emit = defineEmits<{ (e: "update:modelValue", value: string): void }>();

function onInput(e: Event) {
  emit("update:modelValue", (e.target as HTMLTextAreaElement).value);
}
</script>

<template>
  <textarea
    :value="modelValue"
    :class="cn(
      'flex min-h-[60px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50',
      props.class
    )"
    :placeholder="placeholder"
    :disabled="disabled"
    :rows="rows"
    @input="onInput"
  />
</template>
