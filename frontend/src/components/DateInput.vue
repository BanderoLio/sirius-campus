<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount } from "vue";
import {
  startOfMonth,
  endOfMonth,
  startOfWeek,
  endOfWeek,
  addMonths,
  subMonths,
  eachDayOfInterval,
  format,
  isSameMonth,
  isSameDay,
  isToday,
} from "date-fns";
import { ru } from "date-fns/locale";

const props = defineProps<{
  modelValue: string;
  placeholder?: string;
  required?: boolean;
}>();

const emit = defineEmits<{
  "update:modelValue": [value: string];
  change: [];
}>();

const display = ref(props.modelValue);
const open = ref(false);
const wrapperRef = ref<HTMLElement | null>(null);

const viewDate = ref(new Date());

watch(
  () => props.modelValue,
  (v) => {
    display.value = v;
  },
);

const selectedDate = computed(() => {
  const [dd, mm, yyyy] = display.value.split(".");
  if (!dd || !mm || !yyyy || yyyy.length < 4) return null;
  const d = new Date(+yyyy, +mm - 1, +dd);
  return isNaN(d.getTime()) ? null : d;
});

const monthLabel = computed(() =>
  format(viewDate.value, "LLLL yyyy", { locale: ru }).replace(/^./, (c) =>
    c.toUpperCase(),
  ),
);

const weekDays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"];

const calendarDays = computed(() => {
  const monthStart = startOfMonth(viewDate.value);
  const monthEnd = endOfMonth(viewDate.value);
  const rangeStart = startOfWeek(monthStart, { weekStartsOn: 1 });
  const rangeEnd = endOfWeek(monthEnd, { weekStartsOn: 1 });
  return eachDayOfInterval({ start: rangeStart, end: rangeEnd });
});

function prevMonth() {
  viewDate.value = subMonths(viewDate.value, 1);
}

function nextMonth() {
  viewDate.value = addMonths(viewDate.value, 1);
}

function pickDay(day: Date) {
  const val = format(day, "dd.MM.yyyy");
  display.value = val;
  emit("update:modelValue", val);
  emit("change");
  open.value = false;
}

function onInput(e: Event) {
  const input = e.target as HTMLInputElement;
  const raw = input.value.replace(/\D/g, "").slice(0, 8);
  let masked = raw;
  if (raw.length > 4)
    masked = raw.slice(0, 2) + "." + raw.slice(2, 4) + "." + raw.slice(4);
  else if (raw.length > 2) masked = raw.slice(0, 2) + "." + raw.slice(2);
  display.value = masked;
  input.value = masked;
  emit("update:modelValue", masked);
}

function onBlur() {
  emit("change");
}

function toggleCalendar() {
  if (!open.value && selectedDate.value) {
    viewDate.value = new Date(
      selectedDate.value.getFullYear(),
      selectedDate.value.getMonth(),
      1,
    );
  } else if (!open.value) {
    viewDate.value = new Date();
  }
  open.value = !open.value;
}

function onClickOutside(e: MouseEvent) {
  if (wrapperRef.value && !wrapperRef.value.contains(e.target as Node)) {
    open.value = false;
  }
}

onMounted(() => document.addEventListener("mousedown", onClickOutside));
onBeforeUnmount(() =>
  document.removeEventListener("mousedown", onClickOutside),
);
</script>

<template>
  <div ref="wrapperRef" class="date-input-root">
    <div class="date-input-wrapper">
      <input
        :value="display"
        type="text"
        inputmode="numeric"
        :placeholder="placeholder ?? 'дд.мм.гггг'"
        maxlength="10"
        autocomplete="off"
        class="date-input"
        :required="required"
        @input="onInput"
        @blur="onBlur"
      />
      <button type="button" tabindex="-1" class="date-input-btn" @click="toggleCalendar">
        <svg viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M5.75 2a.75.75 0 0 1 .75.75V4h7V2.75a.75.75 0 0 1 1.5 0V4H16a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h1.25V2.75A.75.75 0 0 1 5.75 2ZM4 7.5h12v8.5H4V7.5Z" clip-rule="evenodd" />
        </svg>
      </button>
    </div>

    <Transition name="dp-fade">
      <div v-if="open" class="dp-dropdown">
        <div class="dp-header">
          <button type="button" class="dp-nav" @click="prevMonth">
            <svg viewBox="0 0 16 16" fill="currentColor"><path d="M10.354 3.354a.5.5 0 0 0-.708-.708l-5 5a.5.5 0 0 0 0 .708l5 5a.5.5 0 0 0 .708-.708L5.707 8l4.647-4.646Z"/></svg>
          </button>
          <span class="dp-month-label">{{ monthLabel }}</span>
          <button type="button" class="dp-nav" @click="nextMonth">
            <svg viewBox="0 0 16 16" fill="currentColor"><path d="M5.646 3.354a.5.5 0 0 1 .708-.708l5 5a.5.5 0 0 1 0 .708l-5 5a.5.5 0 0 1-.708-.708L10.293 8 5.646 3.354Z"/></svg>
          </button>
        </div>

        <div class="dp-weekdays">
          <span v-for="wd in weekDays" :key="wd" class="dp-wd">{{ wd }}</span>
        </div>

        <div class="dp-days">
          <button
            v-for="(day, idx) in calendarDays"
            :key="idx"
            type="button"
            class="dp-day"
            :class="{
              'dp-day--other': !isSameMonth(day, viewDate),
              'dp-day--today': isToday(day),
              'dp-day--selected': selectedDate && isSameDay(day, selectedDate),
            }"
            @click="pickDay(day)"
          >
            {{ day.getDate() }}
          </button>
        </div>

        <div class="dp-footer">
          <button type="button" class="dp-today-btn" @click="pickDay(new Date())">
            Сегодня
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.date-input-root {
  position: relative;
  display: inline-block;
}

.date-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.date-input {
  width: 100%;
  padding: 0.5rem 2.25rem 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  line-height: 1.25rem;
  font-variant-numeric: tabular-nums;
  letter-spacing: 0.025em;
  color: #111827;
  background: white;
}

.date-input::placeholder { color: #9ca3af; }

.date-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

.date-input-btn {
  position: absolute;
  right: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.25rem;
  height: 1.25rem;
  color: #6b7280;
  cursor: pointer;
  background: none;
  border: none;
  padding: 0;
  transition: color 0.15s;
}
.date-input-btn:hover { color: #3b82f6; }
.date-input-btn svg { width: 1rem; height: 1rem; }

/* dropdown */
.dp-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  z-index: 50;
  width: 17rem;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  box-shadow: 0 10px 15px -3px rgba(0,0,0,.1), 0 4px 6px -4px rgba(0,0,0,.1);
  padding: 0.75rem;
  user-select: none;
}

.dp-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.dp-month-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #111827;
}

.dp-nav {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.75rem;
  height: 1.75rem;
  border-radius: 0.375rem;
  border: none;
  background: none;
  color: #6b7280;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}
.dp-nav:hover { background: #f3f4f6; color: #111827; }
.dp-nav svg { width: 1rem; height: 1rem; }

.dp-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  margin-bottom: 0.25rem;
}

.dp-wd {
  text-align: center;
  font-size: 0.6875rem;
  font-weight: 500;
  color: #9ca3af;
  padding: 0.125rem 0;
}

.dp-days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
}

.dp-day {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  margin: auto;
  font-size: 0.8125rem;
  border-radius: 0.375rem;
  border: none;
  background: none;
  color: #111827;
  cursor: pointer;
  transition: background 0.1s, color 0.1s;
}
.dp-day:hover { background: #eff6ff; }

.dp-day--other {
  color: #d1d5db;
}
.dp-day--other:hover { color: #9ca3af; }

.dp-day--today {
  font-weight: 600;
  box-shadow: inset 0 0 0 1px #3b82f6;
}

.dp-day--selected {
  background: #3b82f6 !important;
  color: white !important;
  font-weight: 600;
}

.dp-footer {
  display: flex;
  justify-content: center;
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid #f3f4f6;
}

.dp-today-btn {
  font-size: 0.75rem;
  color: #3b82f6;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  transition: background 0.15s;
}
.dp-today-btn:hover { background: #eff6ff; }

/* transition */
.dp-fade-enter-active { transition: opacity 0.15s ease, transform 0.15s ease; }
.dp-fade-leave-active { transition: opacity 0.1s ease, transform 0.1s ease; }
.dp-fade-enter-from { opacity: 0; transform: translateY(-4px); }
.dp-fade-leave-to { opacity: 0; transform: translateY(-4px); }
</style>
