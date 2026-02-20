<script setup lang="ts">
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const alertVariants = cva(
  "relative w-full rounded-lg border p-4 [&>svg~*]:pl-7 [&>svg+div]:translate-y-[-3px] [&>svg]:absolute [&>svg]:left-4 [&>svg]:top-4 [&>svg]:text-foreground",
  {
    variants: {
      variant: {
        default: "bg-background text-foreground",
        destructive:
          "border-destructive/50 text-destructive dark:border-destructive [&>svg]:text-destructive",
        success: "border-green-500/50 bg-green-50 text-green-900 dark:bg-green-900/20 dark:text-green-400 [&>svg]:text-green-600",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

type AlertVariants = VariantProps<typeof alertVariants>;

interface Props extends /* @vue-ignore */ AlertVariants {
  class?: string;
}

const props = withDefaults(defineProps<Props>(), {
  variant: "default",
});
</script>

<template>
  <div :class="cn(alertVariants({ variant: props.variant }), props.class)" role="alert">
    <slot />
  </div>
</template>
