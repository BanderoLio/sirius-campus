# Логи в Grafana Loki

При запуске стека через `docker-compose up` поднимаются:

- **Loki** — хранилище логов (порт 3100)
- **Grafana** — UI для просмотра (порт 3000)

## Просмотр логов

1. Откройте Grafana: http://localhost:3000  
   Логин: `admin`, пароль: `admin`.

2. Перейдите в **Explore** (иконка компаса слева) и выберите источник **Loki**.

3. В запросе можно указать:
   - `{service="application-service"}` — логи application-service
   - `{service="gateway"}` — логи gateway
   - или оставить пустой запрос и нажать **Run query**, чтобы увидеть все логи.

Сервисы **gateway** и **application-service** при заданной переменной `LOKI_URL` отправляют логи в Loki автоматически.
