<script setup lang="ts">
import { cn } from "@/lib/utils";

interface Props {
  type?: string;
  modelValue?: string | number;
  class?: string;
  placeholder?: string;
  disabled?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  type: "text",
});

const emit = defineEmits<{ (e: "update:modelValue", value: string): void }>();

function onInput(e: Event) {
  const t = (e.target as HTMLInputElement);
  emit("update:modelValue", t.value);
}
</script>

<template>
  <input
    :type="type"
    :value="modelValue"
    :class="cn(
      'flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50',
      props.class
    )"
    :placeholder="placeholder"
    :disabled="disabled"
    @input="onInput"
  />
</template>
