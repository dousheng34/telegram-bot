# 🎬 Telegram Bot — Қазақша Одағайлар

Қазақша фильмдердегі одағайларды (эмоциялық сөздерді) үйрететін интерактивті Telegram боты.

## 🚀 Ерекшеліктері

- 📹 **Видео үзіндісі** — Фильмдегі сахналар
- ❓ **Интерактивті тестілер** — Одағайдың мағынасын анықтау
- 🎯 **Қазақша интерфейс** — Толық қазақша
- ⚡ **Жылдам жауап** — Telegram API арқылы
- 🔄 **Автоматты ping** — Koyeb-те ұйықтамау

## 📋 Орнату

### 1. Telegram Bot Token алу

1. [@BotFather](https://t.me/BotFather) арқылы жаңа бот құрыңыз
2. Token-ді көшіріңіз (мысалы: `8763593193:AAEukYqJ1ImsDQMsc2YFaECC2T4-8JmaMXk`)

### 2. Репозиторийді клондау

```bash
git clone https://github.com/dousheng34/telegram-bot.git
cd telegram-bot
```

### 3. Орнату

```bash
# .env файлын құру
cp .env.example .env

# .env файлын өңдеу (BOT_TOKEN-ді қойыңыз)
nano .env
```

### 4. Зависимостіктерді орнату

```bash
pip install -r requirements.txt
```

### 5. Ботты іске қосу

```bash
# Локально
python bot.py

# Koyeb-те (орнату арқылы)
# Koyeb-те BOT_TOKEN орнатыңыз
```

## 🔧 Конфигурация

`.env` файлында:

```bash
BOT_TOKEN=your_token_here          # Telegram Bot Token
WEBAPP_URL=https://...             # Web App URL (опционал)
KOYEB_URL=https://your-url.koyeb.app/  # Koyeb URL
PORT=8000                          # HTTP порт
```

## 📝 Одағайлар қосу

`bot.py` файлында `VIDEOS` сөздігіне қосыңыз:

```python
VIDEOS = {
    "одағай": {
        "file_id": "BAACAgIAAxk...",  # Telegram video file_id
        "caption": "🎬 Фильм атауы",
        "question": "Сұрақ мәтіні",
        "options": ["A. Жауап 1", "Ә. Жауап 2", "Б. Жауап 3", "В. Жауап 4"],
        "correct": 0,  # Дұрыс жауап индексі (0-3)
    },
}
```

### Video file_id алу

1. Ботқа видео жіберіңіз
2. Бот `file_id` қайтарады
3. Оны `VIDEOS` сөздігіне қойыңыз

## 🎯 Команды

- `/start` — Басты мәзір
- `/list` — Барлық одағайлар
- `/help` — Қолдау ақпараты
- Одағай жазыңыз — Видео + тест аласыз

## 🐛 Түзетілген мәселелер

✅ **Қауіпсіздік**: BOT_TOKEN орнына `.env` файлынан оқу
✅ **Callback query**: `menu` батырмасы дұрыс жұмыс істейді
✅ **Error handling**: Барлық қателіктер ұстап алынады
✅ **Logging**: Толық логирование

## 📦 Зависимостіктер

- `requests` — HTTP сұраулар

## 🚀 Koyeb-те орнату

1. GitHub репозиторийін Koyeb-ке байланыстырыңыз
2. Орнату параметрлері:
   - **Build command**: `pip install -r requirements.txt`
   - **Run command**: `python bot.py`
3. Орнату айнымалылары:
   - `BOT_TOKEN` = Ваш токен
   - `KOYEB_URL` = Ваш Koyeb URL

## 📞 Қолдау

Админ: [@aseka0303](https://t.me/aseka0303)

## 📄 Лицензия

MIT License

---

**Түзетілген**: 2026-03-19
**Версия**: 2.0
