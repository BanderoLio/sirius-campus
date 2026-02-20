# Frontend Development Guidelines (Vue.js + TypeScript)

Данный документ описывает правила разработки фронтенд-части проекта «Кампус Сириус» на Vue.js 3 + TypeScript.

## Содержание

- [Технологический стек](#технологический-стек)
- [Структура проекта](#структура-проекта)
- [Архитектурные принципы](#архитектурные-принципы)
- [Стиль кода](#стиль-кода)
- [Управление состоянием](#управление-состоянием)
- [API-интеграция](#api-интеграция)
- [Обработка ошибок](#обработка-ошибок)
- [Маршрутизация](#маршрутизация)
- [Компоненты](#компоненты)
- [Формы и валидация](#формы-и-валидация)
- [Стилизация](#стилизация)
- [Тестирование](#тестирование)
- [Производительность](#производительность)

## Технологический стек

| Компонент             | Технология                  |
| --------------------- | --------------------------- |
| Фреймворк             | Vue.js 3 (Composition API)  |
| Язык                  | TypeScript 5+               |
| Сборка                | Vite                        |
| Управление состоянием | Pinia                       |
| Маршрутизация         | Vue Router 4                |
| HTTP-клиент           | Axios                       |
| Валидация форм        | VeeValidate + Zod           |
| UI-компоненты         | shadcn/ui (Vue port), см. [DESIGN-SYSTEM.md](frontend/DESIGN-SYSTEM.md) |
| Стилизация            | Tailwind CSS                |
| Иконки                | Lucide Vue                  |
| Форматирование        | Prettier                    |
| Линтинг               | ESLint + @typescript-eslint |
| Тестирование          | Vitest + Vue Test Utils     |
| E2E тесты             | Playwright                  |

## Структура проекта

```
frontend/
├── public/                     # Статические файлы
├── src/
│   ├── api/                    # API-клиенты
│   │   ├── client.ts           # Axios instance с трассировкой
│   │   ├── auth.api.ts
│   │   ├── duties.api.ts
│   │   └── ...
│   ├── assets/                 # Изображения, шрифты
│   ├── components/             # Переиспользуемые компоненты
│   │   ├── ui/                 # shadcn/ui компоненты
│   │   │   ├── button.vue
│   │   │   ├── input.vue
│   │   │   ├── card.vue
│   │   │   └── ...
│   │   └── features/           # Бизнес-компоненты
│   │       ├── DutyCard.vue
│   │       ├── PatrolTable.vue
│   │       └── ...
│   ├── composables/            # Composition API хуки
│   │   ├── useAuth.ts
│   │   ├── useApi.ts
│   │   ├── useTracing.ts       # Трассировка запросов
│   │   └── ...
│   ├── constants/              # Константы
│   │   ├── errorCodes.ts       # Коды ошибок (shared с backend)
│   │   ├── routes.ts
│   │   └── ...
│   ├── layouts/                # Layout-компоненты
│   │   ├── DefaultLayout.vue
│   │   ├── AuthLayout.vue
│   │   └── ...
│   ├── lib/                    # Утилиты библиотек
│   │   └── utils.ts            # cn() helper для Tailwind
│   ├── router/                 # Vue Router конфигурация
│   │   ├── index.ts
│   │   ├── guards.ts
│   │   └── routes.ts
│   ├── stores/                 # Pinia stores
│   │   ├── auth.store.ts
│   │   ├── duties.store.ts
│   │   └── ...
│   ├── types/                  # TypeScript типы
│   │   ├── api.types.ts
│   │   ├── models.types.ts
│   │   └── ...
│   ├── utils/                  # Утилиты
│   │   ├── date.utils.ts
│   │   ├── validation.utils.ts
│   │   └── ...
│   ├── views/                  # Страницы (route components)
│   │   ├── auth/
│   │   ├── duties/
│   │   └── ...
│   ├── App.vue
│   ├── main.ts
│   └── index.css               # Tailwind directives
├── tests/
├── components.json             # shadcn/ui конфигурация (см. DESIGN-SYSTEM.md)
├── tailwind.config.js
├── .env.example
├── tsconfig.json
├── vite.config.ts
└── package.json
```

## Архитектурные принципы

### Composition API

- **Обязательно** использовать Composition API (setup script)
- Избегать Options API
- Использовать `<script setup lang="ts">` синтаксис

```vue
<script setup lang="ts">
import { ref, computed } from 'vue';
import type { Duty } from '@/types/models.types';

const duties = ref<Duty[]>([]);
const activeDuties = computed(() =>
  duties.value.filter((d) => d.status === 'pending')
);
</script>
```

### Разделение ответственности

- **Views** — компоненты-страницы, привязаны к роутам
- **Components** — переиспользуемые UI-компоненты
- **Composables** — переиспользуемая логика (hooks)
- **Stores** — глобальное состояние приложения
- **API** — HTTP-запросы к backend

### Single Responsibility

Каждый компонент должен иметь одну ответственность:

```vue
<!-- ❌ Плохо: компонент делает слишком много -->
<template>
  <div>
    <form @submit="handleSubmit">...</form>
    <div v-for="duty in duties">...</div>
    <pagination />
  </div>
</template>

<!-- ✅ Хорошо: разделены на отдельные компоненты -->
<template>
  <div>
    <DutyForm @submit="handleSubmit" />
    <DutyList :duties="duties" />
    <AppPagination />
  </div>
</template>
```

## Стиль кода

### TypeScript Strict Mode

```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true
  }
}
```

### Именование

| Сущность        | Конвенция         | Пример                 |
| --------------- | ----------------- | ---------------------- |
| Компоненты      | PascalCase        | `DutyCard.vue`         |
| Composables     | camelCase + use   | `useAuth.ts`           |
| Stores          | camelCase + Store | `authStore.ts`         |
| Views           | PascalCase + View | `DutiesListView.vue`   |
| Типы/Интерфейсы | PascalCase        | `User`, `DutyResponse` |
| Константы       | UPPER_SNAKE_CASE  | `API_BASE_URL`         |
| Функции/методы  | camelCase         | `fetchDuties()`        |
| Props           | camelCase         | `userId`, `isActive`   |
| Events          | kebab-case        | `@update:modelValue`   |

### Props Typing

```vue
<script setup lang="ts">
interface Props {
  userId: string;
  isActive?: boolean;
  duties: Duty[];
}

const props = withDefaults(defineProps<Props>(), {
  isActive: true,
});
</script>
```

### Events Typing

```vue
<script setup lang="ts">
interface Emits {
  (e: 'submit', data: DutyCreateRequest): void;
  (e: 'cancel'): void;
}

const emit = defineEmits<Emits>();

const handleSubmit = (data: DutyCreateRequest) => {
  emit('submit', data);
};
</script>
```

### ESLint & Prettier

```bash
# Форматирование
npm run format

# Проверка lint
npm run lint
npm run lint:fix
```

## Управление состоянием

### Pinia Stores

Каждый store следует паттерну:

```typescript
// stores/duties.store.ts
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { Duty } from '@/types/models.types';
import { dutiesApi } from '@/api/duties.api';

export const useDutiesStore = defineStore('duties', () => {
  // State
  const duties = ref<Duty[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Getters
  const pendingDuties = computed(() =>
    duties.value.filter((d) => d.status === 'pending')
  );

  // Actions
  async function fetchDuties() {
    loading.value = true;
    error.value = null;

    try {
      const response = await dutiesApi.getAll();
      duties.value = response.data.items;
    } catch (err) {
      error.value = 'Не удалось загрузить дежурства';
      console.error(err);
    } finally {
      loading.value = false;
    }
  }

  async function createDuty(data: DutyCreateRequest): Promise<Duty> {
    loading.value = true;

    try {
      const response = await dutiesApi.create(data);
      duties.value.push(response.data);
      return response.data;
    } finally {
      loading.value = false;
    }
  }

  function $reset() {
    duties.value = [];
    loading.value = false;
    error.value = null;
  }

  return {
    // State
    duties,
    loading,
    error,
    // Getters
    pendingDuties,
    // Actions
    fetchDuties,
    createDuty,
    $reset,
  };
});
```

### Использование Store

```vue
<script setup lang="ts">
import { useDutiesStore } from '@/stores/duties.store';
import { storeToRefs } from 'pinia';

const dutiesStore = useDutiesStore();
const { duties, loading, pendingDuties } = storeToRefs(dutiesStore);
const { fetchDuties, createDuty } = dutiesStore;

onMounted(() => {
  fetchDuties();
});
</script>
```

## API-интеграция

### Axios Instance с трассировкой

```typescript
// filepath: src/api/client.ts
import axios from 'axios';
import { useAuthStore } from '@/stores/auth.store';
import router from '@/router';
import {
  generateTraceId,
  getTraceId,
  setTraceId,
  getCorrelationId,
} from '@/composables/useTracing';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - добавление токена и trace headers
apiClient.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore();
    const token = authStore.accessToken;

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Добавить trace_id и correlation_id
    let traceId = getTraceId();
    if (!traceId) {
      traceId = generateTraceId();
      setTraceId(traceId);
    }

    config.headers['X-Trace-ID'] = traceId;
    config.headers['X-Correlation-ID'] = getCorrelationId();

    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - обработка 401 и сохранение trace_id
apiClient.interceptors.response.use(
  (response) => {
    // Сохранить trace_id из ответа
    const traceId = response.headers['x-trace-id'];
    if (traceId) {
      setTraceId(traceId);
    }
    return response;
  },
  async (error) => {
    // Сохранить trace_id даже при ошибке
    const traceId = error.response?.headers['x-trace-id'];
    if (traceId) {
      setTraceId(traceId);
    }

    if (error.response?.status === 401) {
      const authStore = useAuthStore();

      // Попытка обновить токен
      const refreshed = await authStore.refreshToken();

      if (!refreshed) {
        authStore.logout();
        router.push('/login');
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;
```

### Composable для трассировки

```typescript
// filepath: src/composables/useTracing.ts
import { v4 as uuidv4 } from 'uuid';

let currentTraceId: string | null = null;
let currentCorrelationId: string | null = null;

export function generateTraceId(): string {
  return uuidv4();
}

export function generateCorrelationId(): string {
  return uuidv4();
}

export function getTraceId(): string {
  if (!currentTraceId) {
    currentTraceId = generateTraceId();
  }
  return currentTraceId;
}

export function setTraceId(traceId: string): void {
  currentTraceId = traceId;
}

export function getCorrelationId(): string {
  if (!currentCorrelationId) {
    currentCorrelationId = generateCorrelationId();
  }
  return currentCorrelationId;
}

export function setCorrelationId(correlationId: string): void {
  currentCorrelationId = correlationId;
}

export function resetTracing(): void {
  currentTraceId = null;
  currentCorrelationId = null;
}

export function useTracing() {
  return {
    generateTraceId,
    generateCorrelationId,
    getTraceId,
    setTraceId,
    getCorrelationId,
    setCorrelationId,
    resetTracing,
  };
}
```

### TypeScript Types (совместимые с Backend)

```typescript
// filepath: src/types/api.types.ts

// Базовые типы
export interface ErrorDetail {
  code: string;
  message: string;
  trace_id: string; // Обязательное поле
  details: unknown | null;
}

export interface ErrorResponse {
  error: ErrorDetail;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// Domain types
export interface Duty {
  id: string;
  building: string;
  entrance: number;
  floor: number;
  room: string;
  duty_date: string; // ISO 8601
  status: string;
  created_at: string;
  updated_at: string;
}

export interface DutyCreateRequest {
  building: string;
  entrance: number;
  floor: number;
  room: string;
  duty_date: string;
}
```

## Обработка ошибок

### Error Codes (shared с Backend)

```typescript
// constants/errorCodes.ts

// Auth Service
export const AUTH_USER_NOT_FOUND = 'AUTH_USER_NOT_FOUND' as const;
export const AUTH_INVALID_CREDENTIALS = 'AUTH_INVALID_CREDENTIALS' as const;
export const AUTH_INVALID_TOKEN = 'AUTH_INVALID_TOKEN' as const;

// Duty Service
export const DUTY_NOT_FOUND = 'DUTY_NOT_FOUND' as const;
export const DUTY_ALREADY_ASSIGNED = 'DUTY_ALREADY_ASSIGNED' as const;

export type AuthErrorCode =
  | typeof AUTH_USER_NOT_FOUND
  | typeof AUTH_INVALID_CREDENTIALS
  | typeof AUTH_INVALID_TOKEN;

export type DutyErrorCode =
  | typeof DUTY_NOT_FOUND
  | typeof DUTY_ALREADY_ASSIGNED;
```

### Интернационализация ошибок

```typescript
// utils/error.utils.ts
import type { ErrorResponse } from '@/types/api.types';
import { AUTH_USER_NOT_FOUND, DUTY_NOT_FOUND } from '@/constants/errorCodes';

const ERROR_MESSAGES: Record<string, string> = {
  [AUTH_USER_NOT_FOUND]: 'Пользователь не найден',
  [AUTH_INVALID_CREDENTIALS]: 'Неверный email или пароль',
  [DUTY_NOT_FOUND]: 'Дежурство не найдено',
  // ...
};

export function getErrorMessage(error: ErrorResponse): string {
  return ERROR_MESSAGES[error.error.code] || error.error.message;
}
```

### Composable для обработки ошибок с трассировкой

```typescript
// filepath: src/composables/useError.ts
import { ref } from 'vue';
import type { AxiosError } from 'axios';
import type { ErrorResponse } from '@/types/api.types';
import { getErrorMessage } from '@/utils/error.utils';
import { getTraceId } from '@/composables/useTracing';

export function useError() {
  const error = ref<string | null>(null);
  const traceId = ref<string | null>(null);

  function handleError(err: unknown) {
    // Сохранить trace_id для отчётов об ошибках
    traceId.value = getTraceId();

    if (axios.isAxiosError(err)) {
      const axiosError = err as AxiosError<ErrorResponse>;

      if (axiosError.response?.data?.error) {
        error.value = getErrorMessage(axiosError.response.data);
        traceId.value =
          axiosError.response.data.error.trace_id || traceId.value;
      } else {
        error.value = 'Произошла ошибка. Попробуйте позже.';
      }
    } else {
      error.value = 'Неизвестная ошибка';
    }

    // Логирование ошибки с trace_id для отладки
    console.error('[Error]', {
      message: error.value,
      trace_id: traceId.value,
      error: err,
    });
  }

  function clearError() {
    error.value = null;
    traceId.value = null;
  }

  return {
    error,
    traceId,
    handleError,
    clearError,
  };
}
```

### Toast компонент для отображения ошибок

```vue
<!-- filepath: src/components/features/ErrorToast.vue -->
<script setup lang="ts">
import {
  Toast,
  ToastAction,
  ToastClose,
  ToastDescription,
  ToastProvider,
  ToastTitle,
  ToastViewport,
} from '@/components/ui/toast';
import { useToast } from '@/components/ui/toast/use-toast';

const { toasts } = useToast();
</script>

<template>
  <ToastProvider>
    <Toast v-for="toast in toasts" :key="toast.id" v-bind="toast">
      <div class="grid gap-1">
        <ToastTitle v-if="toast.title">
          {{ toast.title }}
        </ToastTitle>
        <ToastDescription v-if="toast.description">
          {{ toast.description }}
        </ToastDescription>
        <ToastDescription
          v-if="toast.traceId"
          class="text-xs text-muted-foreground"
        >
          Trace ID: {{ toast.traceId }}
        </ToastDescription>
      </div>
      <ToastAction v-if="toast.action" v-bind="toast.action" />
      <ToastClose />
    </Toast>
    <ToastViewport />
  </ToastProvider>
</template>
```

## Формы и валидация

### VeeValidate + Zod

```vue
<!-- filepath: src/views/duties/CreateDutyView.vue -->
<script setup lang="ts">
import { toTypedSchema } from '@vee-validate/zod';
import { useForm } from 'vee-validate';
import * as z from 'zod';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

const dutySchema = z.object({
  building: z.enum(['8', '9'], {
    required_error: 'Выберите корпус',
  }),
  entrance: z.number().min(1).max(4, 'Подъезд должен быть от 1 до 4'),
  floor: z.number().min(1).max(5, 'Этаж должен быть от 1 до 5'),
  room: z.string().min(1, 'Введите номер комнаты'),
  duty_date: z.string().min(1, 'Выберите дату'),
});

const form = useForm({
  validationSchema: toTypedSchema(dutySchema),
});

const onSubmit = form.handleSubmit(async (values) => {
  // Submit logic
});
</script>

<template>
  <Card class="max-w-2xl mx-auto">
    <CardHeader>
      <CardTitle>Создать дежурство</CardTitle>
      <CardDescription
        >Заполните форму для создания нового дежурства</CardDescription
      >
    </CardHeader>
    <form @submit="onSubmit">
      <CardContent class="space-y-4">
        <FormField v-slot="{ componentField }" name="building">
          <FormItem>
            <FormLabel>Корпус</FormLabel>
            <Select v-bind="componentField">
              <FormControl>
                <SelectTrigger>
                  <SelectValue placeholder="Выберите корпус" />
                </SelectTrigger>
              </FormControl>
              <SelectContent>
                <SelectItem value="8">Корпус 8</SelectItem>
                <SelectItem value="9">Корпус 9</SelectItem>
              </SelectContent>
            </Select>
            <FormMessage />
          </FormItem>
        </FormField>

        <FormField v-slot="{ componentField }" name="room">
          <FormItem>
            <FormLabel>Номер комнаты</FormLabel>
            <FormControl>
              <Input type="text" placeholder="304" v-bind="componentField" />
            </FormControl>
            <FormDescription>Введите номер комнаты</FormDescription>
            <FormMessage />
          </FormItem>
        </FormField>

        <!-- ...other fields... -->
      </CardContent>
      <CardFooter class="flex justify-between">
        <Button type="button" variant="outline" @click="$router.back()">
          Отмена
        </Button>
        <Button type="submit"> Создать </Button>
      </CardFooter>
    </form>
  </Card>
</template>
```

## Стилизация

### Tailwind Utility Classes

Используйте Tailwind utility classes напрямую:

```vue
<template>
  <div class="flex items-center justify-between p-4 bg-card rounded-lg border">
    <h2 class="text-xl font-semibold">Дежурства</h2>
    <Button class="ml-auto">Создать</Button>
  </div>
</template>
```

### Кастомные стили (только при необходимости)

```vue
<style scoped>
/* Используйте @apply только для сложных, повторяющихся паттернов */
.custom-card {
  @apply rounded-lg border bg-card text-card-foreground shadow-sm;
}
</style>
```

### Responsive Design

```vue
<template>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <DutyCard v-for="duty in duties" :key="duty.id" :duty="duty" />
  </div>
</template>
```

## Тестирование

### Unit Tests (Vitest)

```typescript
// tests/unit/components/DutyCard.spec.ts
import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import DutyCard from '@/components/DutyCard.vue';

describe('DutyCard', () => {
  it('renders duty information', () => {
    const wrapper = mount(DutyCard, {
      props: {
        duty: {
          id: '123',
          building: '8',
          room: '304',
          duty_date: '2025-12-01',
          status: 'pending',
        },
      },
    });

    expect(wrapper.text()).toContain('Корпус 8');
    expect(wrapper.text()).toContain('Комната 304');
  });

  it('emits click event', async () => {
    const wrapper = mount(DutyCard, {
      props: { duty: mockDuty },
    });

    await wrapper.trigger('click');
    expect(wrapper.emitted('click')).toBeTruthy();
  });
});
```

### Composable Tests

```typescript
// tests/unit/composables/useAuth.spec.ts
import { describe, it, expect, beforeEach } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useAuth } from '@/composables/useAuth';

describe('useAuth', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it('should login successfully', async () => {
    const { login, isAuthenticated } = useAuth();

    await login('test@example.com', 'password');

    expect(isAuthenticated.value).toBe(true);
  });
});
```

## Производительность

### Lazy Loading

```typescript
// Lazy load routes
const routes: RouteRecordRaw[] = [
  {
    path: '/duties',
    component: () => import('@/views/duties/DutiesListView.vue'),
  },
];

// Lazy load components
const HeavyComponent = defineAsyncComponent(
  () => import('@/components/HeavyComponent.vue')
);
```

### Virtual Scrolling

Для больших списков используйте virtual scrolling (vue-virtual-scroller):

```vue
<template>
  <RecycleScroller :items="duties" :item-size="80" key-field="id">
    <template #default="{ item }">
      <DutyCard :duty="item" />
    </template>
  </RecycleScroller>
</template>
```

### Debounce для поиска с трассировкой

```typescript
import { useDebounceFn } from '@vueuse/core';
import {
  generateCorrelationId,
  setCorrelationId,
} from '@/composables/useTracing';

const searchQuery = ref('');

const debouncedSearch = useDebounceFn((query: string) => {
  // Новый correlation_id для группы запросов поиска
  setCorrelationId(generateCorrelationId());
  fetchDuties({ search: query });
}, 300);

watch(searchQuery, (newQuery) => {
  debouncedSearch(newQuery);
});
```

### Memo для тяжёлых вычислений

```typescript
import { computed } from 'vue';

const expensiveComputation = computed(() => {
  // Тяжёлые вычисления
  return duties.value
    .filter((d) => d.status === 'pending')
    .map((d) => ({ ...d, formatted: formatDuty(d) }))
    .sort((a, b) => a.duty_date.localeCompare(b.duty_date));
});
```

## Утилиты

### Форматирование даты

```typescript
// utils/date.utils.ts
import { format, parseISO } from 'date-fns';
import { ru } from 'date-fns/locale';

export function formatDate(isoDate: string): string {
  return format(parseISO(isoDate), 'dd.MM.yyyy', { locale: ru });
}

export function formatDateTime(isoDate: string): string {
  return format(parseISO(isoDate), 'dd.MM.yyyy HH:mm', { locale: ru });
}

export function formatTime(isoDate: string): string {
  return format(parseISO(isoDate), 'HH:mm', { locale: ru });
}
```

### Local Storage Composable

```typescript
// composables/useLocalStorage.ts
import { ref, watch } from 'vue';

export function useLocalStorage<T>(key: string, defaultValue: T) {
  const storedValue = localStorage.getItem(key);
  const data = ref<T>(storedValue ? JSON.parse(storedValue) : defaultValue);

  watch(
    data,
    (newValue) => {
      localStorage.setItem(key, JSON.stringify(newValue));
    },
    { deep: true }
  );

  return data;
}
```

---

> **Данный документ является обязательным к соблюдению всеми frontend-разработчиками проекта «Кампус Сириус».**
