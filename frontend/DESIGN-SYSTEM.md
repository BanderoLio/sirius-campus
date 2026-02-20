# UI Kit / Design System

Фронтенд использует **shadcn-style** компоненты (Vue 3 + Tailwind) для единообразного интерфейса.

## Расположение

- **Примитивы UI:** `frontend/src/components/ui/` — кнопки, карточки, поля ввода, бейджи, алерты и т.д.
- **Утилиты:** `frontend/src/lib/utils.ts` — функция `cn()` для объединения классов Tailwind.

## Компоненты

| Компонент | Путь | Назначение |
|-----------|------|------------|
| Button | `components/ui/button/Button.vue` | Кнопки (variant: default, destructive, outline, secondary, ghost, link; size: default, sm, lg, icon) |
| Card | `components/ui/card/Card.vue` | Карточки; подкомпоненты CardHeader, CardTitle, CardDescription, CardContent, CardFooter |
| Input | `components/ui/input/Input.vue` | Текстовое поле (v-model) |
| Label | `components/ui/label/Label.vue` | Подпись к полю |
| Select | `components/ui/select/Select.vue` | Выпадающий список (native select, v-model) |
| Textarea | `components/ui/textarea/Textarea.vue` | Многострочное поле (v-model) |
| Badge | `components/ui/badge/Badge.vue` | Бейдж (variant: default, secondary, destructive, outline, success, warning) |
| Alert | `components/ui/alert/Alert.vue` | Блок сообщения (variant: default, destructive, success) |

## Дизайн-токены

В `src/index.css` заданы CSS-переменные для темы (`:root` и `.dark`):

- **Цвета:** `--background`, `--foreground`, `--primary`, `--secondary`, `--muted`, `--accent`, `--destructive`, `--border`, `--input`, `--ring`
- **Скругления:** `--radius` (используется в `tailwind.config.js` как `lg`, `md`, `sm`)

В коде используйте классы Tailwind: `bg-primary`, `text-muted-foreground`, `border-border`, `rounded-lg` и т.д.

## Добавление новых компонентов

1. Создайте компонент в `src/components/ui/<name>/` с использованием `cn()` из `@/lib/utils`.
2. Используйте варианты через `class-variance-authority` (cva) при необходимости.
3. Подключите дизайн-токены (цвета, радиус) из темы.

## Примеры

**Кнопка:**
```vue
<Button>Отправить</Button>
<Button variant="outline" size="sm">Отмена</Button>
```

**Карточка:**
```vue
<Card>
  <CardHeader>
    <CardTitle>Заголовок</CardTitle>
    <CardDescription>Описание</CardDescription>
  </CardHeader>
  <CardContent>Контент</CardContent>
  <CardFooter>Действия</CardFooter>
</Card>
```

**Форма:**
```vue
<div class="space-y-2">
  <Label for="email">Email</Label>
  <Input id="email" v-model="email" type="email" placeholder="email@example.com" />
</div>
```

**Бейдж статуса:**
```vue
<Badge variant="success">Одобрено</Badge>
<Badge variant="destructive">Отклонено</Badge>
<Badge variant="secondary">Ожидает</Badge>
```

## Ссылки

- [shadcn-vue](https://www.shadcn-vue.com/) — порт shadcn/ui для Vue 3
- [Tailwind CSS](https://tailwindcss.com/)
- [Radix Vue](https://www.radix-vue.com/) — примитивы (при расширении набора компонентов)
