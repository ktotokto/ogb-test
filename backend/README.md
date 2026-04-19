# OGB Game Server — Backend

Flask + Flask-SocketIO backend для онлайн-игры OGB.

## Установка

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
```

## Запуск

```bash
python app.py
```

Сервер запустится на `http://localhost:5000`

## API Endpoints

### Авторизация

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/api/auth/register` | Регистрация |
| POST | `/api/auth/login` | Вход |
| GET | `/api/auth/me` | Получить текущего пользователя (JWT) |
| GET | `/api/auth/users?q=...` | Поиск пользователей |

### Игровые сессии

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/api/game/sessions` | Создать сессию |
| GET | `/api/game/sessions` | Список сессий |
| GET | `/api/game/sessions/:id` | Получить сессию |
| POST | `/api/game/sessions/:id/join` | Войти в сессию |
| POST | `/api/game/sessions/:id/leave` | Покинуть сессию |
| PUT | `/api/game/sessions/:id/state` | Сохранить состояние |
| GET | `/api/game/sessions/:id/players` | Игроки сессии |

### Колоды карт

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/api/game/sessions/:id/decks` | Получить колоды |
| POST | `/api/game/sessions/:id/decks` | Создать колоду |
| PUT | `/api/game/decks/:id` | Обновить колоду |

## WebSocket (Socket.IO)

Подключение:
```js
import { io } from 'socket.io-client'
const socket = io('http://localhost:5000', {
  query: { token: 'YOUR_JWT_TOKEN' }
})
```

### События от клиента → сервер

| Событие | Данные | Описание |
|---------|--------|----------|
| `join-session` | `{ sessionId }` | Войти в игровую комнату |
| `leave-session` | `{ sessionId }` | Покинуть комнату |
| `object-move` | `{ sessionId, objectId, position }` | Перемещение объекта |
| `object-select` | `{ sessionId, objectId }` | Выделение объекта |
| `object-flip` | `{ sessionId, objectId, faceUp }` | Переворот карты |
| `object-rotate` | `{ sessionId, objectId, rotation }` | Поворот объекта |
| `object-delete` | `{ sessionId, objectId }` | Удаление объекта |
| `object-add` | `{ sessionId, object }` | Добавление объекта |
| `stack-add` | `{ sessionId, targetId, sourceId }` | Добавить в стопку |
| `stack-remove` | `{ sessionId, objectId }` | Убрать из стопки |
| `draw-update` | `{ sessionId, drawings }` | Обновление рисунков |
| `draw-clear` | `{ sessionId }` | Очистить рисунки |
| `save-state` | `{ sessionId, state }` | Сохранить состояние в БД |
| `chat-message` | `{ sessionId, message }` | Сообщение в чат |

### События от сервера → клиент

| Событие | Данные | Описание |
|---------|--------|----------|
| `connected` | `{ userId }` | Подключено |
| `error` | `{ message }` | Ошибка |
| `session-state` | `{ sessionId, state, players }` | Текущее состояние |
| `player-online` | `{ user }` | Игрок подключился |
| `player-offline` | `{ userId }` | Игрок отключился |
| `object-move` | `{ ...data }` | Объект перемещён |
| `object-select` | `{ ...data }` | Объект выделен |
| `object-flip` | `{ ...data }` | Карта перевёрнута |
| `object-rotate` | `{ ...data }` | Объект повёрнут |
| `object-delete` | `{ ...data }` | Объект удалён |
| `object-add` | `{ ...data }` | Объект добавлен |
| `stack-add` | `{ ...data }` | Стопка создана |
| `stack-remove` | `{ ...data }` | Карта убрана из стопки |
| `draw-update` | `{ ...data }` | Рисунки обновлены |
| `draw-clear` | `{ ...data }` | Рисунки очищены |
| `chat-message` | `{ userId, username, message, timestamp }` | Сообщение в чат |
| `state-saved` | `{ sessionId }` | Состояние сохранено |

## Пример запроса — регистрация

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "player1", "email": "p1@test.com", "password": "123456"}'
```

## Пример запроса — вход

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "player1", "password": "123456"}'
```

## Структура проекта

```
backend/
├── app.py          # Точка входа
├── config.py       # Конфигурация
├── models.py       # Модели БД
├── auth.py         # Авторизация (register, login)
├── game.py         # Игровые сессии (CRUD)
├── events.py       # SocketIO события
├── requirements.txt
└── .env.example
```
