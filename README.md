# OGB — Онлайн настольная игра

Vue 3 + Vite фронтенд + Flask + Socket.IO бэкенд для онлайн-настольных игр.

## Стек

**Фронтенд:** Vue 3, Vite, Pinia, Vue Router, TailwindCSS, socket.io-client
**Бэкенд:** Python, Flask, Flask-SocketIO, Flask-JWT-Extended, SQLAlchemy

## Быстрый старт

### 1. Фронтенд

```bash
npm install
npm run dev
```

Откройте http://localhost:5173

### 2. Бэкенд

**Windows:**
```bash
run-backend.bat
```

**Вручную:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python app.py
```

Бэкенд запустится на http://localhost:5000

## Функционал

### Авторизация
- Регистрация и вход через `/auth`
- JWT токены сохраняются в localStorage
- Автоматическое подключение WebSocket при входе

### Игровое поле
- **Рисование** — плавные линии (quadraticCurveTo)
- **Карты** — добавление, редактирование, переворот (face up/down)
- **Стопки карт** — кнопка "Layers" на карте → клик на другую карту
- **Панорамирование** — Alt + drag или средняя кнопка мыши
- **Зум** — Ctrl + колесо мыши или кнопки +/-
- **Выделение** — Ctrl+Click (множественное), Shift+Click (диапазон), Ctrl+A (все)

### Онлайн (WebSocket)
Все действия синхронизируются между игроками в реальном времени:
- Перемещение объектов
- Переворот/поворот карт
- Создание/удаление объектов
- Рисование
- Чат

## Структура

```
├── backend/
│   ├── app.py          # Flask приложение
│   ├── config.py       # Конфигурация
│   ├── models.py       # Модели БД (User, GameSession)
│   ├── auth.py         # API авторизации
│   ├── game.py         # API игровых сессий
│   ├── events.py       # SocketIO обработчики
│   └── requirements.txt
├── src/
│   ├── composables/
│   │   ├── useSocket.js        # WebSocket composable
│   │   └── useGameBoardPan.js  # Панорамирование
│   ├── stores/
│   │   ├── user.js             # Авторизация
│   │   └── game.js             # Игровое состояние
│   ├── views/
│   │   ├── AuthView.vue        # Страница входа
│   │   └── GameView.vue        # Игровая страница
│   └── components/
│       └── gamePage/
│           └── gameMain/
│               ├── GameBoard.vue   # Игровое поле
│               ├── GameObject.vue  # Объект на поле
│               └── CardEditor.vue  # Редактор карт
└── run-backend.bat     # Запуск бэкенда (Windows)
```

## API Endpoints

### Авторизация
| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/api/auth/register` | Регистрация |
| POST | `/api/auth/login` | Вход |
| GET | `/api/auth/me` | Текущий пользователь |

### Игровые сессии
| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/api/game/sessions` | Создать сессию |
| GET | `/api/game/sessions` | Список сессий |
| POST | `/api/game/sessions/:id/join` | Войти в сессию |
| PUT | `/api/game/sessions/:id/state` | Сохранить состояние |

См. [backend/README.md](backend/README.md) для полного описания API и WebSocket.
