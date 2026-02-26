<script setup lang="ts">
import { ref, watch, onMounted, onBeforeUnmount, nextTick } from "vue";

const props = defineProps<{
  modelValue: string;
  step?: number;
}>();

const emit = defineEmits<{
  "update:modelValue": [value: string];
}>();

const display = ref(formatHHMM(props.modelValue));
const open = ref(false);
const wrapperRef = ref<HTMLElement | null>(null);
const listRef = ref<HTMLElement | null>(null);

const stepMinutes = props.step ?? 30;

const slots: string[] = [];
for (let m = 0; m < 24 * 60; m += stepMinutes) {
  const hh = String(Math.floor(m / 60)).padStart(2, "0");
  const mm = String(m % 60).padStart(2, "0");
  slots.push(`${hh}:${mm}`);
}

watch(
  () => props.modelValue,
  (v) => {
    display.value = formatHHMM(v);
  },
);

function formatHHMM(v: string): string {
  const [h, m] = (v || "00:00").split(":");
  const hh = Math.min(23, Math.max(0, parseInt(h, 10) || 0));
  const mm = Math.min(59, Math.max(0, parseInt(m, 10) || 0));
  return `${String(hh).padStart(2, "0")}:${String(mm).padStart(2, "0")}`;
}

function onInput(e: Event) {
  const input = e.target as HTMLInputElement;
  let raw = input.value.replace(/[^\d:]/g, "");

  const digits = raw.replace(/:/g, "");
  if (digits.length <= 2) {
    raw = digits;
  } else {
    raw = digits.slice(0, 2) + ":" + digits.slice(2, 4);
  }

  input.value = raw;
  display.value = raw;

  if (/^\d{2}:\d{2}$/.test(raw)) {
    emit("update:modelValue", formatHHMM(raw));
  }
}

function onBlur() {
  display.value = formatHHMM(display.value);
  emit("update:modelValue", display.value);
}

function pick(slot: string) {
  display.value = slot;
  emit("update:modelValue", slot);
  open.value = false;
}

async function toggle() {
  open.value = !open.value;
  if (open.value) {
    await nextTick();
    scrollToActive();
  }
}

function scrollToActive() {
  if (!listRef.value) return;
  const active = listRef.value.querySelector(".tp-slot--active") as HTMLElement;
  if (active) {
    active.scrollIntoView({ block: "center" });
  }
}

function onClickOutside(e: MouseEvent) {
  if (wrapperRef.value && !wrapperRef.value.contains(e.target as Node)) {
    open.value = false;
  }
}

function onWheel(e: WheelEvent) {
  e.preventDefault();
  const [h, m] = display.value.split(":").map(Number);
  let total = h * 60 + m;
  total += e.deltaY > 0 ? stepMinutes : -stepMinutes;
  total = ((total % (24 * 60)) + 24 * 60) % (24 * 60);
  const val = `${String(Math.floor(total / 60)).padStart(2, "0")}:${String(total % 60).padStart(2, "0")}`;
  display.value = val;
  emit("update:modelValue", val);
}

onMounted(() => document.addEventListener("mousedown", onClickOutside));
onBeforeUnmount(() => document.removeEventListener("mousedown", onClickOutside));
</script>

<template>
  <div ref="wrapperRef" class="tp-root">
    <div class="tp-field" @wheel="onWheel">
      <input
        :value="display"
        type="text"
        inputmode="numeric"
        placeholder="ЧЧ:ММ"
        maxlength="5"
        autocomplete="off"
        class="tp-input"
        @input="onInput"
        @blur="onBlur"
        @focus="($event.target as HTMLInputElement).select()"
      />
      <button type="button" tabindex="-1" class="tp-btn" @click="toggle">
        <svg viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 18a8 8 0 1 0 0-16 8 8 0 0 0 0 16Zm.75-13a.75.75 0 0 0-1.5 0v5c0 .414.336.75.75.75h4a.75.75 0 0 0 0-1.5h-3.25V5Z" clip-rule="evenodd" />
        </svg>
      </button>
    </div>

    <Transition name="tp-fade">
      <div v-if="open" ref="listRef" class="tp-dropdown">
        <button
          v-for="slot in slots"
          :key="slot"
          type="button"
          class="tp-slot"
          :class="{ 'tp-slot--active': slot === display }"
          @click="pick(slot)"
        >
          {{ slot }}
        </button>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.tp-root {
  position: relative;
  display: inline-block;
}

.tp-field {
  position: relative;
  display: flex;
  align-items: center;
}

.tp-input {
  width: 6.5rem;
  padding: 0.5rem 2.25rem 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-variant-numeric: tabular-nums;
  letter-spacing: 0.05em;
  color: #111827;
  background: white;
  text-align: center;
}
.tp-input::placeholder { color: #9ca3af; }
.tp-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

.tp-btn {
  position: absolute;
  right: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.25rem;
  height: 1.25rem;
  color: #6b7280;
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
  transition: color 0.15s;
}
.tp-btn:hover { color: #3b82f6; }
.tp-btn svg { width: 1rem; height: 1rem; }

.tp-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  z-index: 50;
  width: 6.5rem;
  max-height: 14rem;
  overflow-y: auto;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  box-shadow: 0 10px 15px -3px rgba(0,0,0,.1), 0 4px 6px -4px rgba(0,0,0,.1);
  padding: 0.25rem;
  scrollbar-width: thin;
  scrollbar-color: #d1d5db transparent;
}

.tp-slot {
  display: block;
  width: 100%;
  padding: 0.375rem 0;
  text-align: center;
  font-size: 0.8125rem;
  font-variant-numeric: tabular-nums;
  color: #374151;
  border: none;
  background: none;
  border-radius: 0.25rem;
  cursor: pointer;
  transition: background 0.1s, color 0.1s;
}
.tp-slot:hover { background: #eff6ff; color: #1d4ed8; }

.tp-slot--active {
  background: #3b82f6 !important;
  color: white !important;
  font-weight: 600;
}

.tp-fade-enter-active { transition: opacity 0.15s ease, transform 0.15s ease; }
.tp-fade-leave-active { transition: opacity 0.1s ease, transform 0.1s ease; }
.tp-fade-enter-from { opacity: 0; transform: translateY(-4px); }
.tp-fade-leave-to { opacity: 0; transform: translateY(-4px); }
</style>
