<script setup lang="ts">
import {
  SelectContent,
  SelectItem,
  SelectItemIndicator,
  SelectItemText,
  SelectPortal,
  SelectRoot,
  SelectTrigger,
  SelectValue,
  SelectViewport,
} from "radix-vue";
import { cn } from "@/lib/utils";
import { Check, ChevronDown } from "lucide-vue-next";

interface SelectOption {
  value: string;
  label: string;
}

interface Props {
  modelValue?: string;
  options: SelectOption[];
  class?: string;
  disabled?: boolean;
  placeholder?: string;
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: "Выберите...",
});

const emit = defineEmits<{ (e: "update:modelValue", value: string): void }>();
</script>

<template>
  <SelectRoot
    :model-value="modelValue"
    @update:model-value="(v: string | undefined) => emit('update:modelValue', v ?? '')"
  >
    <SelectTrigger
      :class="
        cn(
          'flex h-9 w-full items-center justify-between gap-2 rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 [&>span]:line-clamp-1',
          props.class
        )
      "
      :disabled="disabled"
    >
      <SelectValue :placeholder="placeholder" />
      <ChevronDown class="size-4 shrink-0 opacity-50" />
    </SelectTrigger>
    <SelectPortal>
      <SelectContent
        position="popper"
        :side-offset="4"
        :class="
          cn(
            'relative z-[100] max-h-96 min-w-[8rem] overflow-hidden rounded-md border border-border bg-popover text-popover-foreground shadow-md data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2'
          )
        "
      >
        <SelectViewport class="p-1">
          <SelectItem
            v-for="opt in options"
            :key="opt.value"
            :value="opt.value"
            :class="cn(
              'relative flex cursor-default select-none items-center rounded-sm py-1.5 pl-8 pr-2 text-sm outline-none focus:bg-accent focus:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50',
              'data-[highlighted]:bg-accent data-[highlighted]:text-accent-foreground'
            )"
          >
            <SelectItemIndicator class="absolute left-2 flex w-4 items-center justify-center">
              <Check class="size-4" />
            </SelectItemIndicator>
            <SelectItemText>{{ opt.label }}</SelectItemText>
          </SelectItem>
        </SelectViewport>
      </SelectContent>
    </SelectPortal>
  </SelectRoot>
</template>
