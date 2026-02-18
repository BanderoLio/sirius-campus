# Контракты application-service

Документ описывает контракты, которые application-service **потребляет** от других сервисов и **предоставляет** внешним потребителям.

---

## 1. Контракты, которые сервис потребляет

### 1.1 auth-service (gRPC)

application-service зависит от auth-service для валидации JWT и получения данных о пользователе. Используются следующие RPC:

| RPC | Назначение |
|-----|------------|
| `ValidateToken(ValidateTokenRequest) returns (ValidateTokenResponse)` | Валидация JWT access token; получение user_id, roles, building, entrance, floor, room для авторизации запросов |
| `GetUserInfo(GetUserInfoRequest) returns (UserInfoResponse)` | Получение ФИО, комнаты, подъезда, корпуса, is_minor, phone, email по user_id (при создании заявления, при обогащении списка и для gRPC GetApprovedLeaves) |

**Расположение proto:** общий репозиторий `proto/` в корне проекта или копия в `application-service/proto/`. Пакет: `campus.auth`, сервис `AuthService`.

**Адрес:** задаётся переменной окружения `AUTH_GRPC_URL` (например `auth-service:50051`).

**Примечание:** при разработке MVP без развёрнутого auth-service допускается использование заглушки gRPC (мок), возвращающей валидный `ValidateTokenResponse` и `UserInfoResponse`.

---

## 2. Контракты, которые сервис предоставляет

### 2.1 REST API

Базовый путь: **`/api/v1/applications`**.

Общие правила: см. ТЗ-0 (формат URL, HTTP-методы, статусы, пагинация, формат ошибок с `trace_id`, заголовки `X-Trace-ID`, `X-Correlation-ID`, `Authorization: Bearer <token>`).

| Метод | Путь | Описание | Права |
|-------|------|----------|--------|
| GET | `/api/v1/applications` | Список заявлений с пагинацией и фильтрами (status, entrance, room, date_from, date_to). Для студента — только свои (user_id из JWT), для воспитателя — все/по фильтрам | student, educator* |
| POST | `/api/v1/applications` | Создание заявления (JSON: leave_time, return_time, reason, contact_phone). is_minor берётся из auth GetUserInfo | student |
| GET | `/api/v1/applications/{id}` | Получение заявления по ID (с проверкой: свой заявка или роль воспитателя) | student, educator* |
| PATCH | `/api/v1/applications/{id}` | Одобрение/отклонение (body: status=approved|rejected, reject_reason?). decided_by, decided_at проставляются сервисом | educator* |
| POST | `/api/v1/applications/{id}/documents` | Загрузка документа (multipart: file, document_type). Типы: signed_application, parent_letter, voice_message | student |

\* educator: роли educator, educator_head, admin.

**Query-параметры для GET списка:**

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| page | int | 1 | Номер страницы |
| size | int | 20 | Размер страницы (≤100) |
| status | string | — | Фильтр: pending, approved, rejected |
| entrance | int | — | Подъезд (1–4). Для воспитателя; список обогащается данными из auth (фильтр по user_id по GetUsers или по снимку, если введён) |
| room | string | — | Номер комнаты |
| date_from | string (ISO 8601 date) | — | Начало периода по leave_time |
| date_to | string (ISO 8601 date) | — | Конец периода по leave_time |

**Формат ответа списка:** по ТЗ-0 (items, total, page, size, pages).

**Коды ошибок (префикс APP_):** APP_APPLICATION_NOT_FOUND, APP_DOCUMENT_NOT_FOUND, APP_INVALID_DOCUMENT_TYPE, APP_MINOR_VOICE_REQUIRED, APP_FORBIDDEN, и общие (UNAUTHORIZED, FORBIDDEN, VALIDATION_ERROR, NOT_FOUND, INTERNAL_ERROR).

---

### 2.2 gRPC (для patrol-service)

Сервис предоставляет метод для получения одобренных заявлений на выход на дату (для обходов).

**Пакет:** `campus.application`, сервис `ApplicationService`.

| RPC | Описание |
|-----|----------|
| `GetApprovedLeaves(GetApprovedLeavesRequest) returns (GetApprovedLeavesResponse)` | Возвращает список одобренных заявлений на выход за указанную дату (и опционально building, entrance). Поля LeaveRecord: user_id, user_name, room, leave_time, return_time, reason. user_name и room при необходимости обогащаются из auth GetUserInfo |

**Proto (как в ТЗ-0):**

```protobuf
syntax = "proto3";

package campus.application;

service ApplicationService {
  rpc GetApprovedLeaves(GetApprovedLeavesRequest) returns (GetApprovedLeavesResponse);
}

message GetApprovedLeavesRequest {
  string date = 1;       // ISO 8601 дата (YYYY-MM-DD)
  string building = 2;
  int32 entrance = 3;     // 0 = все
}

message GetApprovedLeavesResponse {
  repeated LeaveRecord records = 1;
}

message LeaveRecord {
  string user_id = 1;
  string user_name = 2;
  string room = 3;
  string leave_time = 4;
  string return_time = 5;
  string reason = 6;
}
```

**Расположение:** `application-service/proto/` или общий `proto/` в корне репозитория. Порт gRPC: **50055**.
