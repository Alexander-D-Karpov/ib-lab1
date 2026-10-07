# ib-lab1 — Secure Crystal Shop API

Защищённое REST API для покупки кристаллов разных цветов.
Flask + SQLAlchemy (SQLite) + JWT (PyJWT) + bcrypt, с CI/CD на GitHub Actions
(Bandit — SAST, pip-audit — SCA).

## Run

    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements-dev.txt
    python run.py

Сервер: http://127.0.0.1:5000
Сид-пользователь: `admin` / `CorrectHorse42!`

## Endpoints

| Метод | Путь            | Auth | Описание                          |
|-------|-----------------|------|-----------------------------------|
| POST  | /auth/register  | нет  | Регистрация пользователя          |
| POST  | /auth/login     | нет  | Логин, возвращает JWT             |
| GET   | /api/data       | да   | Баланс + список кристаллов        |
| POST  | /api/buy        | да   | Покупка кристаллов                |

### Примеры

    curl -s -X POST localhost:5000/auth/login \
      -H 'Content-Type: application/json' \
      -d '{"username":"admin","password":"CorrectHorse42!"}'

    TOKEN=<token from login>

    curl -s localhost:5000/api/data -H "Authorization: Bearer $TOKEN"

    curl -s -X POST localhost:5000/api/buy \
      -H "Authorization: Bearer $TOKEN" \
      -H 'Content-Type: application/json' \
      -d '{"crystal_id":1,"quantity":2}'

## Security

- **SQL Injection:** все запросы к БД идут через SQLAlchemy ORM
  (`User.query.filter_by(...)`, `db.session.get(...)`). Строки SQL руками не
  собираются, пользовательский ввод — всегда параметр, не часть запроса.
- **XSS:** все строковые поля из пользовательского ввода (`username`, `color`)
  экранируются `markupsafe.escape` перед возвратом в JSON.
- **Broken Authentication:** пароли хранятся только как bcrypt-хэш
  (`bcrypt.hashpw` + случайная соль). При логине выдаётся подписанный JWT
  (HS256) с `exp`. Защищённые эндпоинты закрыты декоратором `token_required`,
  который проверяет подпись и срок действия токена.

## CI/CD

`.github/workflows/ci.yml` запускается на каждый push и pull request:
Bandit (SAST) → pip-audit (SCA) → pytest. Отчёты — во вкладке Actions.
