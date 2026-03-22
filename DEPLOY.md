# 🎮 KOLIZEI — Инструкция по деплою

## Структура проекта
```
kolizei/
├── main.py          # FastAPI сервер (API + отдаёт сайт)
├── bot.py           # Telegram бот
├── database.py      # SQLite база данных
├── requirements.txt # Зависимости Python
├── railway.toml     # Конфиг Railway
└── index.html       # Фронтенд (перенести в static/)
```

---

## ШАГ 1 — Создать Telegram бота

1. Открой Telegram → найди **@BotFather**
2. Напиши `/newbot`
3. Введи имя: `KOLIZEI Reviews`
4. Введи username: `kolizei_reviews_bot` (или любой свободный)
5. **Скопируй токен** — выглядит так: `7412345678:AAFxxx...`

6. Узнай свой **Chat ID**:
   - Напиши боту @userinfobot любое сообщение
   - Он ответит твоим ID, например: `123456789`

---

## ШАГ 2 — Подготовить файлы

1. Создай папку `static/` внутри проекта
2. Переименуй `index.html` → `static/index.html`

Итоговая структура:
```
kolizei/
├── static/
│   └── index.html
├── main.py
├── bot.py
├── database.py
├── requirements.txt
└── railway.toml
```

---

## ШАГ 3 — Залить на GitHub

1. Зайди на https://github.com → **New repository**
2. Назови `kolizei-feedback`, создай публичный
3. Загрузи все файлы (можно через веб-интерфейс drag & drop)

---

## ШАГ 4 — Задеплоить на Railway

1. Зайди на https://railway.app
2. **New Project** → **Deploy from GitHub repo**
3. Выбери репозиторий `kolizei-feedback`
4. Railway сам определит Python проект

### Добавить переменные окружения:
В Railway → твой проект → вкладка **Variables** → добавь:

| Переменная  | Значение                        |
|-------------|----------------------------------|
| `BOT_TOKEN` | токен от BotFather               |
| `CHAT_ID`   | твой Telegram ID (числовой)      |

5. Нажми **Deploy** — Railway соберёт и запустит

### Получить URL сайта:
- Railway → Settings → Networking → **Generate Domain**
- Получишь адрес вида: `kolizei-feedback.up.railway.app`

---

## ШАГ 5 — Проверить

1. Открой сайт по Railway URL
2. Заполни тестовый отзыв и отправь
3. В Telegram боте должно прийти уведомление 🔔
4. Напиши боту `/stats` — увидишь статистику
5. Напиши `/reviews` — последние отзывы
6. Напиши `/export` — получишь CSV файл

---

## Команды бота

| Команда    | Описание                          |
|------------|-----------------------------------|
| `/start`   | Главное меню                      |
| `/stats`   | Статистика: кол-во, средние оценки|
| `/reviews` | Последние 5 отзывов               |
| `/export`  | Скачать все отзывы (CSV файл)     |

---

## Частые вопросы

**Q: Где хранится база данных?**
SQLite файл `kolizei.db` создаётся автоматически в папке проекта на Railway.

**Q: Бесплатно ли это?**
Да. Railway даёт $5 кредитов в месяц — этого хватит на небольшой проект.

**Q: Как посмотреть логи?**
Railway → проект → вкладка **Deployments** → кликни на деплой → **View Logs**

**Q: Бот не отвечает?**
Убедись что `BOT_TOKEN` и `CHAT_ID` правильно заданы в Variables.
CHAT_ID должен быть числом без кавычек.
