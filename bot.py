# -*- coding: utf-8 -*-
import asyncio
import logging
import os
import re
import json

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    CallbackQuery,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.filters import Command
from aiohttp import web

# ──────────────────────────────────
# ENV
# ──────────────────────────────────
TOKEN = os.environ.get("BOT_TOKEN")
PORT = int(os.environ.get("PORT", 8000))
APP_URL = os.environ.get("APP_URL", "")

logging.basicConfig(
    format="%(asctime)s | %(message)s",
    level=logging.INFO,
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

FILE_ID_LOG = "file_ids.json"

# ──────────────────────────────────
# FILE_ID САҚТАУ
# ──────────────────────────────────
def save_file_id(name: str, file_id: str) -> bool:
    try:
        data = {}
        if os.path.exists(FILE_ID_LOG):
            with open(FILE_ID_LOG, "r", encoding="utf-8") as f:
                data = json.load(f)
        data[name] = file_id
        with open(FILE_ID_LOG, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        log.info(f"✅ FILE_ID САҚТАЛДЫ: {name}")
        return True
    except Exception as e:
        log.error(f"FILE_ID сақтау қатесі: {e}")
        return False

# ──────────────────────────────────
# МӘТІНДЕР
# ──────────────────────────────────
TEXTS = {
    "welcome": "🎬 <b>Қош келдіңіз!</b>\n\nОдағайды таңдаңыз:",
    "list_title": "📋 <b>Одағай ({n}):</b>\n\n{items}",
    "help_text": "❓ <b>Қолдау</b>\n\n👤 Админ: @aseka0303\n\n💡 <b>Видео жіберу:</b>\nВидео + Caption-та одағай атауын жазыңыз (мысалы: алақай)",
    "not_found": "🤔 <b>«{w}»</b> тізімде жоқ.\n/list — барлық одағайлар",
    "quiz_header": "❓ <b>Тест сұрағы:</b>\n\n{q}\n\n👇 <b>Жауапты таңдаңыз:</b>",
    "correct": "✅ <b>Дұрыс! Керемет!</b>\n\n{ans}",
    "wrong": "❌ <b>Қате!</b>\n\nСіз: {user}\nДұрыс: <b>{correct}</b>",
    "btn_list": "📋 Тізім",
    "btn_help": "❓ Қолдау",
    "btn_menu": "🔙 Мәзір",
    "video_saved": "✅ <b>FILE_ID САҚТАЛДЫ!</b>\n\n📝 Атауы: <code>{name}</code>\n\n🔑 FILE_ID:\n<code>{file_id}</code>",
}

def t(key: str, **kw) -> str:
    tmpl = TEXTS.get(key, key)
    return tmpl.format(**kw) if kw else tmpl

# ──────────────────────────────────
# ВИДЕО + ТЕСТТЕР
# ──────────────────────────────────
VIDEOS = {
    "алақай": {
        "file_id": "BAACAgIAAxkBAAIHOWm9cBpCjFB6WQ8uUxVxbHR5Qhe3AALBnQAC3jrpSRE6u0kgxgKWOgQ",
        "caption_kz": "🎬 «Алақай!» — Жаужүрек мың бала",
        "question_kz": "«Жаужүрек мың бала» фильмінде қолданылған «Алақай!» одағайы кейіпкердің қандай эмоциясын білдіреді?",
        "options_kz": ["A. Қуаныш 😀", "Ә. Таңдану 😲", "Б. Өкініш 😔", "В. Қорқыныш 😨"],
        "correct": 0,
    },
    "бәрекелді": [
        {
            "quiz_id": "b0",
            "file_id": "BAACAgIAAxkBAAIHRWm9cbfyn67B3pOPhdN6WLmJWZjKAALonQAC3jrpSRMTUjUxdIi8OgQ",
            "caption_kz": "🎬 1️⃣ «Әй, Бәрекелді!» — Жаужүрек мың бала",
            "question_kz": "«Жаужүрек мың бала» фильмінде Ақсақалдың «Әй, бәрекелді!» одағайы қандай көңіл күйді білдіреді?",
            "options_kz": ["А. Риза болу, сүйсіну 😍", "Ә. Таңырқау 😲", "Б. Өкініш 😔", "В. Алаңдау 😨"],
            "correct": 0,
        },
        {
            "quiz_id": "b1",
            "file_id": "BAACAgIAAxkBAAIHRmm9cbf9OEW1Uh9sSS4fmT3Mwf8WAALpnQAC3jrpSZegipoVFlukOgQ",
            "caption_kz": "🎬 2️⃣ «Бәрекелді!» — Жаужүрек мың бала",
            "question_kz": "«Жаужүрек мың бала» фильмінде балалар күресіп жатқанда үлкендердің «Әй, бәрекелді!», «Әп-бәрекелді!» сөздері қандай көңіл күйді білдіреді?",
            "options_kz": ["А. Мұң, өкініш 😔", "Ә. Ашу, реніш 😡", "Б. Таңдану, абыржу 😲", "В. Риза болу, қолпаштау 🤲"],
            "correct": 3,
        },
    ],
    "жә-жә": [
        {
            "quiz_id": "je0",
            "file_id": "BAACAgIAAxkBAAIHSWm9chVPvZacideMpfRbIa-8aOG5AALvnQAC3jrpSSDjTDjHFTEpOgQ",
            "caption_kz": "🎬 1️⃣ «Жә-Жә!»— Жаужүрек мың бала",
            "question_kz": "«Жаужүрек мың бала» фильміндегі «Жә-жә!» одағайы қандай көңіл күйді білдіреді?",
            "options_kz": ["А. Қуаныш 😀", "Ә. Кейіген ашу, зеку 😤", "Б. Мұң 😔", "В. Таңдану 😲"],
            "correct": 1,
        },
        {
            "quiz_id": "je1",
            "file_id": "BAACAgIAAxkBAAIHS2m9cw-fMMLz5u_aXUmeiZN7yXybAAL3nQAC3jrpSehAP174IeUjOgQ",
            "caption_kz": "🎬 2️⃣ «Жә!» — Жаужүрек мың бала",
            "question_kz": "«Жаужүрек мың бала» фильміндегі «Жә!» одағайы қандай сезімді білдіреді?",
            "options_kz": ["А. Сабырға шақыру, тоқтату 🤚", "Ә. Ашу, реніш 😡", "Б. Қуаныш, қолпаштау 🤲", "В. Өкініш, мұңаю 😔"],
            "correct": 0,
        },
    ],
    "қап": {
        "file_id": "BAACAgIAAxkBAAIHTWm9c12lrBMi5YtdhohDYWV15V-JAAL9nQAC3jrpSV2Ohyf9pBuYOgQ",
        "caption_kz": "🎬 «Қап!» — Жаужүрек мың бала",
        "question_kz": "«Жаужүрек мың бала» фильмінде күресте жеңіліс болған сәтте айтылған «Қап!» одағайы қандай сезімді білдіреді?",
        "options_kz": ["А. Қуану, мақтану 😀", "Ә. Өкініш, қапалану 😔", "Б. Қорқу, абыржу 😱", "В. Қолдау, сүйсіну 🤲"],
        "correct": 1,
    },
    "ойбай": [
        {
            "quiz_id": "oybay0",
            "file_id": "BAACAgIAAxkBAAIHT2m9c57wKdORDn6tHeNcQU5t90hkAAIEngAC3jrpSeV5YGeVxMoEOgQ",
            "caption_kz": "🎬 «1️⃣ Ойбай, жыланды қара!» — Алдар көсе",
            "question_kz": "«Алдар көсе» телехикаясындағы саудагердің «Ойбай, жыланды қара!» деуі қандай көңіл күйді білдіреді?",
            "options_kz": ["А. Риза болу, қолпаштау 🤲", "Ә. Қуану, сүйсіну 😀", "Б. Қорқу, абыржу 😱", "В. Өкініш, қапалану 😔"],
            "correct": 2,
        },
        {
            "quiz_id": "oybay1",
            "file_id": "BAACAgIAAxkBAAIHUWm9c_EV2i9Jo6jy3J6GwBl5_FJyAAILngAC3jrpSd6CnXdNB5cFOgQ",
            "caption_kz": "🎬 2️⃣ «Ойбай!» — Алдар көсе",
            "question_kz": "«Алдар көсе» телехикаясындағы «Ойбай!» одағайы қандай көңіл күйді білдіреді?",
            "options_kz": ["А. Қуаныш, сүйсіну 😀", "Ә. Қорқу, сасу 😱", "Б. Риза болу, қолпаштау 🤲", "В. Таңқалу, қызығу 😲"],
            "correct": 1,
        },
        {
            "quiz_id": "oybay2",
            "file_id": "BAACAgIAAxkBAAII9GnEVMCCJ7x7grS9CESdI7pbTjMsAALmkQAEIUpa_BLZNXoluzoE",
            "caption_kz": "🎬 3️⃣ «Ойбай-ай!» — Менің атым Қожа",
            "question_kz": "«Менің атым Қожа» фильміндегі «Ойбай-ай!» одағайы қандай көңіл күйді білдіреді?",
            "options_kz": ["А. Қуаныш, сүйсіну 😀", "Ә. Ауыру, қиналу 😣", "Б. Абыржу, қорқу 😱", "В. Риза болу, қолпаштау 🤲"],
            "correct": 1,
        },
        {
            "quiz_id": "oybay3",
            "file_id": "BAACAgIAAxkBAAII9mnEVRHN41JmaZ4BZS92YALVydNnAALpkQAEIUouHQz2pLtRBDoE",
            "caption_kz": "🎬 4️⃣ «Ойбай» — Ер Төстік",
            "question_kz": "«Ер Төстік» мультфильміндегі Мыстанның «Ойбай, ашулысың ғой өзің!» деуіндегі «Ойбай» одағайы қандай көңіл күйді білдіреді?",
            "options_kz": ["А. Жалған қорқу, мысқыл 😏", "Ә. Қайғы, мұң 😔", "Б. Қуаныш, сүйсіну 😀", "В. Өкініш, қапалану 😔"],
            "correct": 0,
        },
        {
            "quiz_id": "oybay4",
            "file_id": "BAACAgIAAxkBAAIJA2nEWgQkTeDGYLot8Oevzdd-IzRUAAL4kQAEIUpnwoD_hYkGjToE",
            "caption_kz": "🎬 5️⃣ «Ойбай!» — Ер Төстік",
            "question_kz": "«Ер Төстік» мультфильміндегі «Ойбай!» одағайы қандай көңіл күйді білдіреді?",
            "options_kz": ["А. Қуаныш, сүйсіну 😀", "Ә. Қорқу, шошу 😱", "Б. Таңқалу, қызығу 😲", "В. Риза болу, қолпаштау 🤲"],
            "correct": 1,
        },
        {
            "quiz_id": "oybay5",
            "file_id": "BAACAgIAAxkBAAIJBWnEWkXxAAFFweJASmT0x_101HUIvQAC-ZEABCFKZO2XK86lIHQ6BA",
            "caption_kz": "🎬 6️⃣ «Ойбай!» — Көксерек",
            "question_kz": "«Көксерек» фильміндегі «Ойбай!» одағайы қандай көңіл күйді білдіреді?",
            "options_kz": ["А. Қуаныш, сүйсіну 😀", "Ә. Таңқалу, қызығу 😲", "Б. Риза болу, қолпаштау 🤲", "В. Қорқу, сескену 😨"],
            "correct": 3,
        },
    ],
    "япыр-ай": {
        "file_id": "BAACAgIAAxkBAAIHU2m9dGGvvWcAAW8Mz6aF_-v_5sainQACHZ4AAt466UlHraPAKpQUfzoE",
        "caption_kz": "🎬 «Япыр-ай!» — Алдар көсе",
        "question_kz": "«Алдар көсе» телехикаясындағы «Япырай-ай» одағайы қандай сезімді білдіреді?",
        "options_kz": ["А. Мұң, өкініш 😔", "Ә. Қуаныш, риза болу 😀", "Б. Таңдану, қызығу 😲", "В. Ашу, кейіс 😡"],
        "correct": 2,
    },
    "әй": {
        "file_id": "BAACAgIAAxkBAAIHVWm9et2nf-uXSbv_i99vLQkOGsbUAAKpngAC3jrpSU0d28gAATaEhzoE",
        "caption_kz": "🎬 «Әй, әй!» — Алдар көсе",
        "question_kz": "«Алдар көсе» телехикаясындағы байдың «Әй, әй!» деуі қандай сезімді білдіреді?",
        "options_kz": ["А. Мұң 😔", "Ә. Қуаныш 😀", "Б. Таңдану 😲", "В. Абдырау 😱"],
        "correct": 3,
    },
    "әттеген-ай": [
        {
            "quiz_id": "et0",
            "file_id": "BAACAgIAAxkBAAIIEGm9lTF2qNfiXVXVfO57PGBhElBOAAJtlgAC3jrxSRtQklrA74d5OgQ",
            "caption_kz": "🎬 1️ —  «Әттеген-ай!» — Жаужүрек мың бала",
            "question_kz": "«Жаужүрек мың бала» фильміндегі Ақсақалдың «Әттеген-ай!» одағайы қандай көңіл күйді білдіреді?",
            "options_kz": ["А. Қуаныш 😀", "Ә. Таңқалу 😲", "Б. Өкініш 😔", "В. Қорқыныш 😨"],
            "correct": 2,
        },
        {
            "quiz_id": "et1",
            "file_id": "BAACAgIAAxkBAAIH_2m9ku-2U9dBRXS7v8whtDibu2qRAAJXlgAC3jrxSReqXSLGNPJ2OgQ",
            "caption_kz": "🎬 2️ — «Әттеген-ай!» — Алдар көсе",
            "question_kz": "«Алдар көсе» телехикаясында байдың «Әттеген-ай!» одағайы қандай сезімді білдіреді?",
            "options_kz": ["А. Риза болу, қолпаштау 🤲", "Ә. Өкініш, мұңаю 😔", "Б. Ашу, кейіс 😡", "В. Таңдану, абыржу 😲"],
            "correct": 2,
        },
        {
            "quiz_id": "et2",
            "file_id": "BAACAgIAAxkBAAIJL2nEYmjK2vaVw716D3EvA2asxJUOAAIWkgAEIUrUjX7gcsHlMToE",
            "caption_kz": "🎬 3️⃣ — «Әттеген-ай!» — Менің атым Қожа",
            "question_kz": "«Менің атым Қожа» фильміндегі «Әттеген-ай!» одағайы қандай көңіл күйді білдіреді?",
            "options_kz": ["А. Қуаныш, сүйсіну 😀", "Ә. Таңдану, қызығу 😲", "Б. Жеңіл өкініш, қынжылу 😔", "В. Қорқу, сескену 😨"],
            "correct": 2,
        },
        {
            "quiz_id": "et3",
            "file_id": "BAACAgIAAxkBAAIJMWnEYyooHKuZ3ieXMc9C1xV0wyVoAAIYkgAEIUpriA3VlsFvvjoE",
            "caption_kz": "🎬 4️⃣ — «Қап, әттеген-ай!» — Ер Төстік",
            "question_kz": "«Ер Төстік» мультфильміндегі «Қап, әттеген-ай!» одағайлары қандай сезімді білдіреді?",
            "options_kz": ["А. Қорқу, сескену 😨", "Ә. Қуаныш, мақтаныш 😀", "Б. Өкініш, ыза 😤", "В. Таңқалу, абыржу 😲"],
            "correct": 2,
        },
    ],
    "құдайым-ау": {
        "file_id": "BAACAgIAAxkBAAIHW2m9e-YHX5THDxrJHJ_4jA2IrDZnAAK7ngAC3jrpSZHUQU6q5lNQOgQ",
        "caption_kz": "🎬 «Құдайым-ау!» — Көшпенділер",
        "question_kz": "«Көшпенділер» фильміндегі «Құдайым-ау» одағайы қандай көңіл күйді білдіреді?",
        "options_kz": ["А. Мұң, өкініш 😔", "Ә. Ашу, реніш 😡", "Б. Таңдану, қуаныш 😲", "В. Қорқыныш, абыржу 😨"],
        "correct": 2,
    },
    "мә": {
        "file_id": "BAACAgIAAxkBAAIHXWm9fBSnGvVD_piGamYpXSF4KNDsAAK-ngAC3jrpSY0E7ByBWekVOgQ",
        "caption_kz": "🎬 «Мә!» — Жаужүрек мың бала",
        "question_kz": "«Жаужүрек мың бала» фильміндегі «Мә!» одағайы қандай көңіл күйді білдіреді?",
        "options_kz": ["А. Қуаныш, сүйсіну 😀", "Ә. Таңқалу, таңырқау 😲", "Б. Мұң, қапа 😔", "В. Ашу, реніш 😡"],
        "correct": 1,
    },
    "құдай-ау": {
        "file_id": "BAACAgIAAxkBAAIHWWm9e3mK_8Poah2nrltrU6atPJRUAAK2ngAC3jrpSR5ZKDatWkbNOgQ",
        "caption_kz": "🎬 Құдай-ау!» — Жаужүрек мың бала",
        "question_kz": "«Жаужүрек мың бала» фильміндегі «Құдай-ау!» одағайы қандай көңіл күйді білдіреді?",
        "options_kz": ["А. Қуаныш 😀", "Ә. Таңқалу 😲", "Б. Қайғы, шошу 😔", "В. Риза болу 🤲"],
        "correct": 2,
    },
    "ура": {
        "file_id": "BAACAgIAAxkBAAIJQGnEZPeFze1BMFSShJqVqd1egK0eAAIckgAEIUqKwUDiVv_iCzoE",
        "caption_kz": "🎬 «Ура!» — Менің атым Қожа",
        "question_kz": "«Менің атым Қожа» фильміндегі «Ура!» одағайы қандай көңіл күйді білдіреді?",
        "options_kz": ["А. Таңдану 😲", "Ә. Қуаныш 😀", "Б. Өкініш 😔", "В. Қорқу 😨"],
        "correct": 1,
    },
    "шіркін": [
        {
            "quiz_id": "sh0",
            "file_id": "BAACAgIAAxkBAAIJT2nEZqaTIaLMrVWjB6fH5nb6LysBAAIpkgAEIUpS35mlMF_USToE",
            "caption_kz": "🎬 1️⃣ «Шіркін-ай!» — Менің атым Қожа",
            "question_kz": "«Менің атым Қожа» фільміндегі «Шіркін-ай!» одағайы қандай сезімді білдіреді?",
            "options_kz": ["А. Аңсау 🥺", "Ә. Қуаныш 😀", "Б. Қайғы 😔", "В. Таңқалу 😲"],
            "correct": 0,
        },
        {
            "quiz_id": "sh1",
            "file_id": "BAACAgIAAxkBAAIJUWnEZ53XMsovwkQlqPppnmt350iZAAIrkgAEIUofd4YpIRA8QDoE",
            "caption_kz": "🎬 2️⃣ «Шіркін!» — Ер Төстік",
            "question_kz": "«Ер Төстік» мультфильміндегі «Шіркін!» одағайы қандай көңіл күйді білдіреді?",
            "options_kz": ["А. Таңдану, қызығу 😲", "Ә. Риза болу, сүйсіну 😍", "Б. Қорқу, сескену 😨", "В. Өкініш, қапа 😔"],
            "correct": 1,
        },
        {
            "quiz_id": "sh2",
            "file_id": "BAACAgIAAxkBAAIJU2nEZ8bHsI-PwqoK8of_eFOuoEUvAAIskgAEIUr0Zikc65oxGjoE",
            "caption_kz": "🎬 3️⃣ «Шіркін» — Көксерек",
            "question_kz": "«Көксерек» фильміндегі «Шіркін» одағайы қандай көңіл күйді білдіреді?",
            "options_kz": ["А. Қуаныш, сүйсіну 😀", "Ә. Сескену, қауіптену 😨", "Б. Таңдану, қызығу 😲", "В. Өкініш, қапа 😔"],
            "correct": 1,
        },
    ],
    "өй": [
        {
            "quiz_id": "oy0",
            "file_id": "BAACAgIAAxkBAAIJVWnEaKSfen-Rd9ugMvpJpDBokO30AAIykgAEIUqUYQv99e2AijoE",
            "caption_kz": "🎬 1️⃣ «Өй» — Ер Төстік",
            "question_kz": "«Ер Төстік» мультфильміндегі кейіпкердің «Өй, мынауың Төстік емес қой» деуіндегі «Өй» одағайы қандай көңіл күйді білдіреді?",
            "options_kz": ["А. Қуаныш, сүйсіну 😀", "Ә. Қорқу, сескену 😨", "Б. Таңқалу, абыржу 😲", "В. Өкініш, қапа 😔"],
            "correct": 2,
        },
        {
            "quiz_id": "oy1",
            "file_id": "BAACAgIAAxkBAAIJV2nEaL6XEx1plRuOckh0NstTR1yEAAI1kgAEIUpjLz7GCOT-ozoE",
            "caption_kz": "🎬 2️⃣ «Өй» — Көксерек",
            "question_kz": "«Көксерек» фильміндегі «Өй» одағайы қандай көңіл күйді білдіреді?",
            "options_kz": ["А. Мүсіркеу, жұбату 🤗", "Ә. Кейіс, мін тағу 😤", "Б. Қуаныш, сүйсіну 😀", "В. Таңдану, қызығу 😲"],
            "correct": 1,
        },
    ],
}

# ──────────────────────────────────
# КЛАВИАТУРАЛАР
# ──────────────────────────────────
def main_kb() -> ReplyKeyboardMarkup:
    buttons = []
    row = []
    for word in VIDEOS:
        row.append(KeyboardButton(text=f"🎬 {word}"))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([
        KeyboardButton(text=t("btn_list")),
        KeyboardButton(text=t("btn_help")),
    ])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, is_persistent=True)

def back_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("btn_menu"), callback_data="menu")]
    ])

def quiz_kb(qid: str, opts: list) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=opts[0], callback_data=f"q|{qid}|0")],
        [InlineKeyboardButton(text=opts[1], callback_data=f"q|{qid}|1")],
        [InlineKeyboardButton(text=opts[2], callback_data=f"q|{qid}|2")],
        [InlineKeyboardButton(text=opts[3], callback_data=f"q|{qid}|3")],
    ])

# ──────────────────────────────────
# QUIZ ІЗДЕУ
# ──────────────────────────────────
def get_quiz(qid: str):
    for w, d in VIDEOS.items():
        for vd in (d if isinstance(d, list) else [d]):
            if vd.get("quiz_id", w) == qid:
                return vd
    return None

# ──────────────────────────────────
# BOT + DISPATCHER
# ──────────────────────────────────
bot = Bot(token=TOKEN) if TOKEN else None
dp = Dispatcher()

# ──────────────────────────────────
# HANDLERS
# ──────────────────────────────────
@dp.message(Command("start", "menu"))
async def cmd_start(msg: Message):
    await msg.answer(t("welcome"), reply_markup=main_kb(), parse_mode="HTML")

@dp.message(Command("list"))
async def cmd_list(msg: Message):
    items = " • ".join(f"<code>{w}</code>" for w in VIDEOS)
    await msg.answer(
        t("list_title", n=len(VIDEOS), items=items),
        reply_markup=back_kb(),
        parse_mode="HTML",
    )

@dp.message(Command("help"))
async def cmd_help(msg: Message):
    await msg.answer(t("help_text"), reply_markup=back_kb(), parse_mode="HTML")

@dp.message(F.video)
async def handle_video(msg: Message):
    file_id = msg.video.file_id
    file_name = (msg.caption or "video").lower().strip()
    if file_id and file_name:
        save_file_id(file_name, file_id)
        await msg.answer(
            t("video_saved", name=file_name, file_id=file_id),
            parse_mode="HTML",
        )
        log.info(f"📹 Видео қабылданды: {file_name}")

@dp.message(F.text)
async def handle_text(msg: Message):
    text = msg.text.strip()

    # Emoji-ді алып тастамас бұрын навигация тексеру
    nav = {
        "📋 Тізім": "/list",
        "❓ Қолдау": "/help",
    }
    if text in nav:
        text = nav[text]

    # Emoji-сіз тазалау
    clean = re.sub(r"^[\U0001F000-\U0001FFFF\u2600-\u27FF\U00010000-\U0010FFFF]\s*", "", text).strip()
    if not clean:
        clean = text

    cmd = clean.lower().split()[0]
    if cmd in ("/start", "/menu"):
        await msg.answer(t("welcome"), reply_markup=main_kb(), parse_mode="HTML")
    elif cmd == "/list":
        items = " • ".join(f"<code>{w}</code>" for w in VIDEOS)
        await msg.answer(t("list_title", n=len(VIDEOS), items=items), reply_markup=back_kb(), parse_mode="HTML")
    elif cmd == "/help":
        await msg.answer(t("help_text"), reply_markup=back_kb(), parse_mode="HTML")
    else:
        word = clean.lower().strip()
        if word in VIDEOS:
            await send_video_quiz(msg.chat.id, word)
        else:
            await msg.answer(t("not_found", w=clean), parse_mode="HTML")

async def send_video_quiz(cid: int, word: str):
    data = VIDEOS.get(word)
    if not data:
        await bot.send_message(cid, t("not_found", w=word), parse_mode="HTML")
        return
    vlist = data if isinstance(data, list) else [data]
    for vd in vlist:
        qid = vd.get("quiz_id", word)
        cap = vd.get("caption_kz", "")
        q = vd.get("question_kz", "")
        opts = vd.get("options_kz", [])
        fid = vd.get("file_id", "")
        if fid:
            await bot.send_video(cid, fid, caption=cap, parse_mode="HTML", supports_streaming=True)
        await bot.send_message(cid, t("quiz_header", q=q), reply_markup=quiz_kb(qid, opts), parse_mode="HTML")
        log.info(f"✅ {word} → {cid}")

@dp.callback_query(F.data.startswith("q|"))
async def handle_quiz_answer(cb: CallbackQuery):
    await cb.answer()
    parts = cb.data.split("|")
    if len(parts) != 3:
        return
    _, qid, ans_str = parts
    try:
        ans = int(ans_str)
    except ValueError:
        return

    vd = get_quiz(qid)
    if not vd:
        return

    c = vd["correct"]
    opts = vd.get("options_kz", [])
    cid = cb.message.chat.id
    mid = cb.message.message_id

    if ans == c:
        await bot.edit_message_text(
            t("correct", ans=opts[c]),
            chat_id=cid,
            message_id=mid,
            reply_markup=back_kb(),
            parse_mode="HTML",
        )
    else:
        q = vd.get("question_kz", "")
        await bot.edit_message_text(
            t("wrong", user=opts[ans], correct=opts[c]),
            chat_id=cid,
            message_id=mid,
            reply_markup=quiz_kb(qid, opts),
            parse_mode="HTML",
        )

@dp.callback_query(F.data == "menu")
async def handle_menu(cb: CallbackQuery):
    await cb.answer()
    await cb.message.answer(t("welcome"), reply_markup=main_kb(), parse_mode="HTML")

# ──────────────────────────────────
# HEALTH CHECK (aiohttp)
# ──────────────────────────────────
async def health_handler(request):
    return web.Response(text="OK")

async def run_health_server():
    app = web.Application()
    app.router.add_get("/", health_handler)
    app.router.add_get("/health", health_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    log.info(f"✅ Health server: port {PORT}")

# ──────────────────────────────────
# SELF-PING
# ──────────────────────────────────
async def self_ping():
    if not APP_URL:
        return
    import aiohttp
    async with aiohttp.ClientSession() as session:
        while True:
            await asyncio.sleep(300)
            try:
                async with session.get(APP_URL, timeout=aiohttp.ClientTimeout(total=10)):
                    pass
            except Exception as e:
                log.warning(f"Self-ping қатесі: {e}")

# ──────────────────────────────────
# BOT COMMANDS
# ──────────────────────────────────
async def set_bot_commands():
    from aiogram.types import BotCommand
    for attempt in range(5):
        try:
            await bot.set_my_commands([
                BotCommand(command="start", description="🎬 Басты мәзір"),
                BotCommand(command="list", description="📋 Одақтар тізімі"),
                BotCommand(command="help", description="❓ Қолдау"),
            ])
            log.info("✅ Bot commands орнатылды!")
            return
        except Exception as e:
            log.warning(f"set_bot_commands attempt {attempt+1} failed: {e}")
            await asyncio.sleep(5)
    log.error("❌ set_bot_commands: барлық әрекет сәтсіз аяқталды")

# ──────────────────────────────────
# MAIN
# ──────────────────────────────────
async def main():
    if not TOKEN:
        log.error("❌ BOT_TOKEN жоқ!")
        return

    log.info(f"🚀 Bot started! PORT:{PORT}")

    await run_health_server()

    # Background tasks — бот бұлар болмаса да жұмыс істейді
    asyncio.create_task(set_bot_commands())
    if APP_URL:
        asyncio.create_task(self_ping())

    await dp.start_polling(bot, allowed_updates=["message", "callback_query"])

if __name__ == "__main__":
    asyncio.run(main())
