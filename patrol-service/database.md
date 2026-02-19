# База данных patrol-service

СУБД: PostgreSQL 15+  
Схема: `public`  
Все первичные ключи: UUID v4  
Все временные метки: `TIMESTAMP WITH TIME ZONE`, UTC

## Таблицы

### `patrols`

Сеансы обхода.

| Столбец      | Тип                        | Ограничения                              | Описание                              |
|--------------|----------------------------|------------------------------------------|---------------------------------------|
| patrol_id    | UUID                       | PRIMARY KEY, DEFAULT gen_random_uuid()   | Идентификатор обхода                  |
| date         | DATE                       | NOT NULL                                 | Дата обхода                           |
| building     | VARCHAR(1)                 | NOT NULL, CHECK (building IN ('8','9'))  | Корпус                                |
| entrance     | SMALLINT                   | NOT NULL, CHECK (entrance BETWEEN 1 AND 4) | Подъезд                             |
| status       | VARCHAR(20)                | NOT NULL, DEFAULT 'in_progress', CHECK (status IN ('in_progress','completed')) | Статус обхода |
| started_at   | TIMESTAMP WITH TIME ZONE   | NOT NULL, DEFAULT NOW()                  | Время начала обхода                   |
| submitted_at | TIMESTAMP WITH TIME ZONE   | NULL                                     | Время сдачи (завершения) обхода       |
| created_at   | TIMESTAMP WITH TIME ZONE   | NOT NULL, DEFAULT NOW()                  | Дата создания записи                  |
| updated_at   | TIMESTAMP WITH TIME ZONE   | NOT NULL, DEFAULT NOW()                  | Дата последнего обновления            |

**Уникальное ограничение:**

```sql
UNIQUE (date, building, entrance)
```

**Индексы:**

```sql
CREATE INDEX idx_patrols_date ON patrols (date);
CREATE INDEX idx_patrols_building_entrance ON patrols (building, entrance);
CREATE INDEX idx_patrols_status ON patrols (status);
```

### `patrol_entries`

Записи проверки студентов в рамках обхода.

| Столбец         | Тип                        | Ограничения                                      | Описание                                                           |
|-----------------|----------------------------|--------------------------------------------------|--------------------------------------------------------------------|
| patrol_entry_id | UUID                       | PRIMARY KEY, DEFAULT gen_random_uuid()           | Идентификатор записи                                               |
| patrol_id       | UUID                       | NOT NULL, REFERENCES patrols(patrol_id) ON DELETE CASCADE | Ссылка на обход                                           |
| user_id         | UUID                       | NOT NULL                                         | UUID студента из auth-service (внешний, без FK)                    |
| room            | VARCHAR(10)                | NOT NULL                                         | Номер комнаты на момент обхода                                     |
| is_present      | BOOLEAN                    | NULL                                             | null — не проверен, true — присутствует, false — отсутствует       |
| absence_reason  | TEXT                       | NULL                                             | Причина отсутствия                                                 |
| checked_at      | TIMESTAMP WITH TIME ZONE   | NULL                                             | Время проверки                                                     |
| created_at      | TIMESTAMP WITH TIME ZONE   | NOT NULL, DEFAULT NOW()                          | Дата создания записи                                               |
| updated_at      | TIMESTAMP WITH TIME ZONE   | NOT NULL, DEFAULT NOW()                          | Дата последнего обновления                                         |

**Уникальное ограничение:**

```sql
UNIQUE (patrol_id, user_id)
```

**Индексы:**

```sql
CREATE INDEX idx_patrol_entries_patrol_id ON patrol_entries (patrol_id);
CREATE INDEX idx_patrol_entries_user_id ON patrol_entries (user_id);
```

## Соответствие 3НФ

**1НФ** — все атрибуты атомарны, нет повторяющихся групп.

**2НФ** — каждая таблица имеет единственный первичный ключ (UUID); все неключевые атрибуты полностью зависят от первичного ключа.

**3НФ** — нет транзитивных зависимостей:
- В `patrols`: все поля (`date`, `building`, `entrance`, `status`, `started_at`, `submitted_at`) зависят непосредственно от `patrol_id`.
- В `patrol_entries`: все поля (`user_id`, `room`, `is_present`, `absence_reason`, `checked_at`) зависят непосредственно от `patrol_entry_id`. `room` — денормализованное поле, зафиксированное на момент обхода, не зависит от `user_id` транзитивно через auth-service, поскольку студент мог сменить комнату.

**Обоснование отсутствия внешнего ключа на `user_id`:**  
`user_id` ссылается на сущность из auth-service, которая находится в отдельной базе данных. Ссылочная целостность обеспечивается на уровне бизнес-логики сервиса (данные запрашиваются по gRPC перед созданием записей).