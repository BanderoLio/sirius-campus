<script setup lang="ts">
import { cn } from "@/lib/utils";

interface Props {
  modelValue?: string;
  class?: string;
  disabled?: boolean;
}

const props = defineProps<Props>();

const emit = defineEmits<{ (e: "update:modelValue", value: string): void }>();

function onChange(e: Event) {
  emit("update:modelValue", (e.target as HTMLSelectElement).value);
}
</script>

<template>
  <select
    :value="modelValue"
    :class="cn(
      'flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50',
      props.class
    )"
    :disabled="disabled"
    @change="onChange"
  >
    <slot />
  </select>
</template>
