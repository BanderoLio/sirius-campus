# ТЗ-1: Модели баз данных микросервисов

## Содержание

1. [Общие соглашения](#1-общие-соглашения)
2. [auth-service](#2-auth-service)
3. [patrol-service](#3-patrol-service)
4. [duty-service](#4-duty-service)
5. [coworking-service](#5-coworking-service)
6. [application-service](#6-application-service)

---

## 1. Общие соглашения

- Все первичные ключи — `UUID v4`.
- Все таблицы содержат поля `created_at` и `updated_at` (`TIMESTAMP WITH TIME ZONE`, UTC).
- Именование таблиц — `snake_case`, множественное число.
- Именование столбцов — `snake_case`.
- ORM — SQLAlchemy 2.0+ (Mapped, mapped_column), все модели наследуют `Base`, `UUIDPrimaryKeyMixin`, `TimestampMixin` из ТЗ-0.
- Каждый микросервис имеет **собственную** базу данных PostgreSQL.
- Межсервисные данные **не дублируются** — при необходимости запрашиваются через gRPC.

---

## 2. auth-service

База данных: `auth_db`

### 2.1 Таблица `users`

Основная таблица пользователей системы (студенты и воспитатели).

| Столбец        | Тип                        | Nullable | Описание                                      |
|----------------|----------------------------|----------|-----------------------------------------------|
| `id`           | `UUID`                     | NO       | PK. Идентификатор пользователя                |
| `email`        | `VARCHAR(255)`             | NO       | Электронная почта (уникальное)                |
| `phone`        | `VARCHAR(20)`              | YES      | Номер телефона                                |
| `password_hash`| `VARCHAR(255)`             | NO       | Хеш пароля                                    |
| `first_name`   | `VARCHAR(100)`             | NO       | Имя                                           |
| `last_name`    | `VARCHAR(100)`             | NO       | Фамилия                                       |
| `patronymic`   | `VARCHAR(100)`             | YES      | Отчество                                      |
| `building`     | `VARCHAR(5)`               | NO       | Корпус (`"8"` или `"9"`)                      |
| `entrance`     | `INTEGER`                  | NO       | Подъезд (1–4)                                 |
| `floor`        | `INTEGER`                  | NO       | Этаж (1–5)                                    |
| `room`         | `VARCHAR(10)`              | NO       | Номер комнаты                                 |
| `is_minor`     | `BOOLEAN`                  | NO       | Несовершеннолетний (`true` / `false`)         |
| `is_active`    | `BOOLEAN`                  | NO       | Активен ли аккаунт (по умолчанию `true`)      |
| `created_at`   | `TIMESTAMP WITH TIME ZONE` | NO       | Дата создания записи                          |
| `updated_at`   | `TIMESTAMP WITH TIME ZONE` | NO       | Дата последнего обновления                    |

### 2.2 Таблица `roles`

Справочник ролей в системе.

| Столбец      | Тип                        | Nullable | Описание                                      |
|--------------|----------------------------|----------|-----------------------------------------------|
| `id`         | `UUID`                     | NO       | PK. Идентификатор роли                        |
| `code`       | `VARCHAR(50)`              | NO       | Код роли (уникальное): `student`, `student_patrol`, `student_head`, `educator`, `educator_head`, `admin` |
| `name`       | `VARCHAR(100)`             | NO       | Название роли для отображения                 |
| `created_at` | `TIMESTAMP WITH TIME ZONE` | NO       | Дата создания записи                          |
| `updated_at` | `TIMESTAMP WITH TIME ZONE` | NO       | Дата последнего обновления                    |

### 2.3 Таблица `user_roles`

Связь пользователей и ролей (many-to-many). Один пользователь может иметь несколько ролей одновременно.

| Столбец      | Тип                        | Nullable | Описание                                      |
|--------------|----------------------------|----------|-----------------------------------------------|
| `id`         | `UUID`                     | NO       | PK. Идентификатор записи                      |
| `user_id`    | `UUID`                     | NO       | FK → `users.id`. Идентификатор пользователя   |
| `role_id`    | `UUID`                     | NO       | FK → `roles.id`. Идентификатор роли           |
| `created_at` | `TIMESTAMP WITH TIME ZONE` | NO       | Дата создания записи                          |
| `updated_at` | `TIMESTAMP WITH TIME ZONE` | NO       | Дата последнего обновления                    |

### 2.4 Таблица `refresh_tokens`

Хранение refresh-токенов для управления сессиями и инвалидации.

| Столбец      | Тип                        | Nullable | Описание                                      |
|--------------|----------------------------|----------|-----------------------------------------------|
| `id`         | `UUID`                     | NO       | PK. Идентификатор токена                      |
| `user_id`    | `UUID`                     | NO       | FK → `users.id`. Владелец токена              |
| `token`      | `VARCHAR(500)`             | NO       | Значение refresh-токена (уникальное)          |
| `expires_at` | `TIMESTAMP WITH TIME ZONE` | NO       | Время истечения токена                        |
| `is_revoked` | `BOOLEAN`                  | NO       | Отозван ли токен (по умолчанию `false`)       |
| `created_at` | `TIMESTAMP WITH TIME ZONE` | NO       | Дата создания записи                          |
| `updated_at` | `TIMESTAMP WITH TIME ZONE` | NO       | Дата последнего обновления                    |

---

## 3. patrol-service

База данных: `patrol_db`

### 3.1 Таблица `patrols`

Сеанс обхода — одна запись на один обход одного подъезда за вечер.

| Столбец        | Тип                        | Nullable | Описание                                      |
|----------------|----------------------------|----------|-----------------------------------------------|
| `id`           | `UUID`                     | NO       | PK. Идентификатор обхода                      |
| `date`         | `DATE`                     | NO       | Дата обхода                                   |
| `building`     | `VARCHAR(5)`               | NO       | Корпус (`"8"` или `"9"`)                      |
| `entrance`     | `INTEGER`                  | NO       | Подъезд (1–4)                                 |
| `patrol_by`    | `UUID`                     | NO       | UUID пользователя, выполняющего обход (студент-обходной или дежурный администратор) |
| `status`       | `VARCHAR(20)`              | NO       | Статус обхода: `in_progress`, `completed`     |
| `started_at`   | `TIMESTAMP WITH TIME ZONE` | NO       | Время начала обхода                           |
| `submitted_at` | `TIMESTAMP WITH TIME ZONE` | YES      | Время сдачи таблицы обхода                    |
| `created_at`   | `TIMESTAMP WITH TIME ZONE` | NO       | Дата создания записи                          |
| `updated_at`   | `TIMESTAMP WITH TIME ZONE` | NO       | Дата последнего обновления                    |

### 3.2 Таблица `patrol_entries`

Запись об одной комнате в рамках обхода.

| Столбец          | Тип                        | Nullable | Описание                                      |
|------------------|----------------------------|----------|-----------------------------------------------|
| `id`             | `UUID`                     | NO       | PK. Идентификатор записи                      |
| `patrol_id`      | `UUID`                     | NO       | FK → `patrols.id`. Идентификатор обхода       |
| `room`           | `VARCHAR(10)`              | NO       | Номер комнаты                                 |
| `user_id`        | `UUID`                     | NO       | UUID проверяемого студента                    |
| `is_present`     | `BOOLEAN`                  | YES      | Находится ли студент в комнате (`null` — ещё не проверен) |
| `absence_reason` | `TEXT`                     | YES      | Причина отсутствия (если известна)            |
| `checked_at`     | `TIMESTAMP WITH TIME ZONE` | YES      | Время проверки комнаты                        |
| `created_at`     | `TIMESTAMP WITH TIME ZONE` | NO       | Дата создания записи                          |
| `updated_at`     | `TIMESTAMP WITH TIME ZONE` | NO       | Дата последнего обновления                    |

---

## 4. duty-service

База данных: `duty_db`

### 4.1 Таблица `duty_schedules`

Расписание дежурств — привязка комнаты к дате дежурства.

| Столбец       | Тип                        | Nullable | Описание                                      |
|---------------|----------------------------|----------|-----------------------------------------------|
| `id`          | `UUID`                     | NO       | PK. Идентификатор записи расписания           |
| `building`    | `VARCHAR(5)`               | NO       | Корпус (`"8"` или `"9"`)                      |
| `entrance`    | `INTEGER`                  | NO       | Подъезд (1–4)                                 |
| `floor`       | `INTEGER`                  | NO       | Этаж (1–5)                                    |
| `room`        | `VARCHAR(10)`              | NO       | Номер комнаты                                 |
| `duty_date`   | `DATE`                     | NO       | Дата дежурства                                |
| `assigned_by` | `UUID`                     | NO       | UUID старосты или воспитателя, назначившего дежурство |
| `status`      | `VARCHAR(20)`              | NO       | Статус: `pending`, `report_submitted`, `accepted`, `overdue` |
| `created_at`  | `TIMESTAMP WITH TIME ZONE` | NO       | Дата создания записи                          |
| `updated_at`  | `TIMESTAMP WITH TIME ZONE` | NO       | Дата последнего обновления                    |

### 4.2 Таблица `duty_reports`

Отчёт о выполненном дежурстве (фото-отчёт по чек-листу).

| Столбец          | Тип                        | Nullable | Описание                                      |
|------------------|----------------------------|----------|-----------------------------------------------|
| `id`             | `UUID`                     | NO       | PK. Идентификатор отчёта                      |
| `schedule_id`    | `UUID`                     | NO       | FK → `duty_schedules.id`. Привязка к расписанию |
| `submitted_by`   | `UUID`                     | NO       | UUID студента, сдающего отчёт                 |
| `status`         | `VARCHAR(20)`              | NO       | Статус отчёта: `submitted`, `accepted`, `rejected` |
| `submitted_at`   | `TIMESTAMP WITH TIME ZONE` | NO       | Время подачи отчёта                           |
| `reviewed_by`    | `UUID`                     | YES      | UUID проверяющего (воспитатель/староста)       |
| `reviewed_at`    | `TIMESTAMP WITH TIME ZONE` | YES      | Время проверки отчёта                         |
| `reject_reason`  | `TEXT`                     | YES      | Причина отклонения (при `rejected`)           |
| `created_at`     | `TIMESTAMP WITH TIME ZONE` | NO       | Дата создания записи                          |
| `updated_at`     | `TIMESTAMP WITH TIME ZONE` | NO       | Дата последнего обновления                    |

### 4.3 Таблица `duty_report_photos`

Фотографии, приложенные к отчёту по чек-листу.

| Столбец      | Тип                        | Nullable | Описание                                      |
|--------------|----------------------------|----------|-----------------------------------------------|
| `id`         | `UUID`                     | NO       | PK. Идентификатор фото                        |
| `report_id`  | `UUID`                     | NO       | FK → `duty_reports.id`. Привязка к отчёту     |
| `category`   | `VARCHAR(50)`              | NO       | Категория чек-листа (см. перечень ниже)       |
| `photo_url`  | `VARCHAR(500)`             | NO       | URL фотографии в хранилище (MinIO)            |
| `created_at` | `TIMESTAMP WITH TIME ZONE` | NO       | Дата создания записи                          |
| `updated_at` | `TIMESTAMP WITH TIME ZONE` | NO       | Дата последнего обновления                    |

**Допустимые значения `category`:**

| Значение                    | Описание                                   |
|-----------------------------|--------------------------------------------|
| `kitchen_stove`             | Кухня — плита                              |
| `kitchen_countertop_1`      | Кухня — столешница 1                       |
| `kitchen_countertop_2`      | Кухня — столешница 2                       |
| `kitchen_sink`              | Кухня — раковина                           |
| `kitchen_appliances`        | Кухня — техника (микроволновки и т.д.)     |
| `kitchen_general`           | Кухня + столовая — общее фото              |
| `kitchen_tables_chairs`     | Столовая — чистые столы и стулья           |
| `laundry_cleanliness`       | Постирочная — отсутствие мусора и пыли     |
| `laundry_machines`          | Постирочная — чистота стиралок/сушилок     |
| `lights_off`                | Выключенный свет в общих зонах             |

### 4.4 Таблица `duty_sanctions`

Санкции при отсутствии отчёта — приглашение к воспитателям.

| Столбец        | Тип                        | Nullable | Описание                                      |
|----------------|----------------------------|----------|-----------------------------------------------|
| `id`           | `UUID`                     | NO       | PK. Идентификатор санкции                     |
| `schedule_id`  | `UUID`                     | NO       | FK → `duty_schedules.id`. Привязка к расписанию |
| `user_id`      | `UUID`                     | NO       | UUID студента, получившего санкцию            |
| `reason`       | `TEXT`                     | NO       | Причина санкции                               |
| `is_resolved`  | `BOOLEAN`                  | NO       | Снята ли санкция (по умолчанию `false`)       |
| `resolved_at`  | `TIMESTAMP WITH TIME ZONE` | YES      | Время снятия санкции                          |
| `resolved_by`  | `UUID`                     | YES      | UUID воспитателя, снявшего санкцию            |
| `created_at`   | `TIMESTAMP WITH TIME ZONE` | NO       | Дата создания записи                          |
| `updated_at`   | `TIMESTAMP WITH TIME ZONE` | NO       | Дата последнего обновления                    |

---

## 5. coworking-service

База данных: `coworking_db`

### 5.1 Таблица `coworkings`

Справочник доступных коворкингов.

| Столбец       | Тип                        | Nullable | Описание                                      |
|---------------|----------------------------|----------|-----------------------------------------------|
| `id`          | `UUID`                     | NO       | PK. Идентификатор коворкинга                  |
| `building`    | `VARCHAR(5)`               | NO       | Корпус (`"8"` или `"9"`)                      |
| `name`        | `VARCHAR(100)`             | NO       | Название коворкинга                           |
| `description` | `TEXT`                     | YES      | Описание коворкинга                           |
| `is_available`| `BOOLEAN`                  | NO       | Доступен ли для бронирования (по умолчанию `true`) |
| `created_at`  | `TIMESTAMP WITH TIME ZONE` | NO       | Дата создания записи                          |
| `updated_at`  | `TIMESTAMP WITH TIME ZONE` | NO       | Дата последнего обновления                    |

### 5.2 Таблица `coworking_bookings`

Заявки на бронирование и жизненный цикл использования коворкинга.

| Столбец              | Тип                        | Nullable | Описание                                      |
|----------------------|----------------------------|----------|-----------------------------------------------|
| `id`                 | `UUID`                     | NO       | PK. Идентификатор бронирования                |
| `coworking_id`       | `UUID`                     | NO       | FK → `coworkings.id`. Коворкинг               |
| `user_id`            | `UUID`                     | NO       | UUID студента-заявителя                       |
| `status`             | `VARCHAR(30)`              | NO       | Статус бронирования (см. перечень ниже)       |
| `booked_at`          | `TIMESTAMP WITH TIME ZONE` | NO       | Время подачи заявки                           |
| `approved_by`        | `UUID`                     | YES      | UUID воспитателя, одобрившего заявку          |
| `approved_at`        | `TIMESTAMP WITH TIME ZONE` | YES      | Время одобрения                               |
| `rejected_by`        | `UUID`                     | YES      | UUID воспитателя, отклонившего заявку         |
| `rejected_at`        | `TIMESTAMP WITH TIME ZONE` | YES      | Время отклонения                              |
| `reject_reason`      | `TEXT`                     | YES      | Причина отклонения                            |
| `key_taken_at`       | `TIMESTAMP WITH TIME ZONE` | YES      | Время получения ключа студентом               |
| `key_returned_at`    | `TIMESTAMP WITH TIME ZONE` | YES      | Время, когда студент отметил возврат ключа    |
| `return_confirmed_by`| `UUID`                     | YES      | UUID воспитателя, подтвердившего возврат ключа|
| `return_confirmed_at`| `TIMESTAMP WITH TIME ZONE` | YES      | Время подтверждения возврата                  |
| `created_at`         | `TIMESTAMP WITH TIME ZONE` | NO       | Дата создания записи                          |
| `updated_at`         | `TIMESTAMP WITH TIME ZONE` | NO       | Дата последнего обновления                    |

**Допустимые значения `status`:**

| Значение             | Описание                                                  |
|----------------------|-----------------------------------------------------------|
| `pending`            | Заявка подана, ожидает подтверждения воспитателем         |
| `approved`           | Заявка одобрена, студент может взять ключ                 |
| `rejected`           | Заявка отклонена воспитателем                             |
| `key_taken`          | Ключ выдан студенту, коворкинг в пользовании              |
| `key_return_requested` | Воспитатель/администратор запросил возврат ключа        |
| `key_returned`       | Студент отметил, что ключ сдан, ожидает подтверждения     |
| `completed`          | Возврат ключа подтверждён воспитателем, сеанс завершён    |
| `cancelled`          | Бронирование отменено студентом                           |

---

## 6. application-service

База данных: `application_db`

### 6.1 Таблица `applications`

Заявления на выход из кампуса.

| Столбец        | Тип                        | Nullable | Описание                                      |
|----------------|----------------------------|----------|-----------------------------------------------|
| `id`           | `UUID`                     | NO       | PK. Идентификатор заявления                   |
| `user_id`      | `UUID`                     | NO       | UUID студента-заявителя                       |
| `is_minor`     | `BOOLEAN`                  | NO       | Несовершеннолетний ли заявитель               |
| `leave_time`   | `TIMESTAMP WITH TIME ZONE` | NO       | Планируемое время выхода                      |
| `return_time`  | `TIMESTAMP WITH TIME ZONE` | NO       | Планируемое время возврата                    |
| `reason`       | `TEXT`                     | NO       | Причина отсутствия                            |
| `status`       | `VARCHAR(20)`              | NO       | Статус: `pending`, `approved`, `rejected`     |
| `decided_by`   | `UUID`                     | YES      | UUID воспитателя, принявшего решение          |
| `decided_at`   | `TIMESTAMP WITH TIME ZONE` | YES      | Время принятия решения                        |
| `reject_reason`| `TEXT`                     | YES      | Причина отклонения                            |
| `created_at`   | `TIMESTAMP WITH TIME ZONE` | NO       | Дата создания записи                          |
| `updated_at`   | `TIMESTAMP WITH TIME ZONE` | NO       | Дата последнего обновления                    |

### 6.2 Таблица `application_documents`

Документы, прикреплённые к заявлению (скан заявления, письмо родителя, голосовое сообщение).

| Столбец         | Тип                        | Nullable | Описание                                      |
|-----------------|----------------------------|----------|-----------------------------------------------|
| `id`            | `UUID`                     | NO       | PK. Идентификатор документа                   |
| `application_id`| `UUID`                     | NO       | FK → `applications.id`. Привязка к заявлению  |
| `document_type` | `VARCHAR(30)`              | NO       | Тип документа (см. перечень ниже)             |
| `file_url`      | `VARCHAR(500)`             | NO       | URL файла в хранилище (MinIO)                 |
| `uploaded_by`   | `UUID`                     | NO       | UUID пользователя, загрузившего документ       |
| `created_at`    | `TIMESTAMP WITH TIME ZONE` | NO       | Дата создания записи                          |
| `updated_at`    | `TIMESTAMP WITH TIME ZONE` | NO       | Дата последнего обновления                    |

**Допустимые значения `document_type`:**

| Значение            | Описание                                              |
|---------------------|-------------------------------------------------------|
| `signed_application`| Сканированное/сфотографированное подписанное заявление|
| `parent_letter`     | Заявление от родителя (для несовершеннолетних)        |
| `voice_message`     | Голосовое сообщение от родителя (для несовершеннолетних)|

---

> **Данный документ описывает структуру таблиц баз данных для всех микросервисов проекта «Кампус Сириус» в соответствии с бизнес-требованиями и стандартами ТЗ-0.**

