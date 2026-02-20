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

**REST API заявлений предоставляется единой точкой входа — Gateway BFF** (порт 8080). Документация: `http://gateway:8080/docs`. application-service **не отдаёт HTTP по заявлениям** — только gRPC. Контракт REST (пути, методы, форматы JSON) описан в документации Gateway и совпадает с прежним контрактом по путям `/api/v1/applications`, query-параметрам и кодам ошибок.

---

### 2.2 gRPC (для Gateway BFF и patrol-service)

Сервис предоставляет метод для получения одобренных заявлений на выход на дату (для обходов).

**Пакет:** `campus.application`, сервис `ApplicationService`. Контекст пользователя передаётся в метаданных gRPC: `x-user-id`, `x-user-roles` (задаёт Gateway BFF).

| RPC | Описание |
|-----|----------|
| `GetApprovedLeaves` | Список одобренных заявлений на выход за дату (building, entrance). Для patrol-service. |
| `ListApplications` | Список заявлений с пагинацией и фильтрами (page, size, status, entrance, room, date_from, date_to). |
| `CreateApplication` | Создание заявления (leave_time, return_time, reason, contact_phone). user_id из метаданных. |
| `GetApplication` | Заявка по ID с документами и can_decide. |
| `DecideApplication` | Одобрение/отклонение (application_id, status, reject_reason). decided_by из метаданных. |
| `UploadDocument` | Загрузка документа (application_id, document_type, file_content, content_type, filename). |
| `GetDocumentDownloadUrl` | Presigned URL для скачивания документа. |

**Расположение proto:** `application-service/proto/application.proto`. Порт gRPC: **50055**. Вызовы идут от Gateway BFF и при необходимости от patrol-service.
