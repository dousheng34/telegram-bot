# -*- coding: utf-8 -*- import requests, time, os, logging, threading, re from http.server import HTTPServer, BaseHTTPRequestHandler from concurrent.futures import ThreadPoolExecutor TOKEN = os.environ.get("BOT_TOKEN") PORT = int(os.environ.get("PORT", 8000)) APP_URL = os.environ.get("APP_URL", "") BASE = f"https://api.telegram.org/bot{TOKEN}" if TOKEN else "" if not TOKEN: logging.warning("⚠️ BOT_TOKEN орнатылмаған!") logging.basicConfig(format="%(asctime)s | %(message)s", level=logging.INFO, datefmt="%H:%M:%S") log = logging.getLogger(__name__) session = requests.Session() # тіл тек қазақша (kz only) # ==================== ТІЛДЕР ==================== TEXTS = { "kz": { "welcome": "🎬 <b>Қош келдіңіз!</b>\n\nОдақтарды таңдаңыз:", "list_title": "📋 <b>Одақтар ({n}):</b>\n\n{items}", "help_text": "❓ <b>Қолдау</b>\n\n👤 Админ: @aseka0303", "not_found": "🤔 <b>«{w}»</b> тізімде жоқ.\n/list — барлық одақтар", "quiz_header": "❓ <b>Тест сұрағы:</b>\n\n{q}\n\n👇 <b>Жауапты таңдаңыз:</b>", "correct": "✅ <b>Дұрыс! Керемет!</b>\n\n{ans}", "wrong": "❌ <b>Қате!</b>\n\nСіз: {user}\nДұрыс: <b>{correct}</b>", "btn_list": "📋 Тізім", "btn_help": "❓ Қолдау", "btn_menu": "🔙 Мәзір", } } def t(uid, key, **kw): lang = "kz" tmpl = TEXTS[lang].get(key, key) return tmpl.format(**kw) if kw else tmpl # ==================== ВИДЕО + ТЕСТ ДЕРЕКҚОРЫ ==================== VIDEOS = { # ───── 1. АЛАҚАЙ ───── "алақай": { "file_id": "",  # FILE_ID ҚОСЫҢЫЗ
        "caption_kz": "🎬 Алақай! — Жаужүрек мың бала",
        "question_kz": "«Жаужүрек мың бала» фильмінде қолданылған «Алақай!» одағайы кейіпкердің қандай эмоциясын білдіреді?",
        "options_kz": ["A. Қуаныш 😀", "Ә. Таңдану 😲", "Б. Өкініш 😔", "В. Қорқыныш 😨"],
        "correct": 0,
    },
    # ───── 2. БӘРЕКЕЛДІ ─────
    "бәрекелді": [
        {
            "quiz_id": "b0",
            "file_id": "",  # FILE_ID ҚОСЫҢЫЗ
            "caption_kz": "🎬 1️⃣ Әй, Бәрекелді! — Жаужүрек мың бала",
            "question_kz": "«Жаужүрек мың бала» фильмінде Ақсақалдың «Әй, бәрекелді!» одағайы қандай көңіл күйді білдіреді?",
            "options_kz": ["А. Риза болу, сүйсіну 😍", "Ә. Таңырқау 😲", "Б. Өкініш 😔", "В. Алаңдау 😨"],
            "correct": 0,
        },
        {
            "quiz_id": "b1",
            "file_id": "",  # FILE_ID ҚОСЫҢЫЗ
            "caption_kz": "🎬 2️⃣ Жүртшылықтың Бәрекелді! — Жаужүрек мың бала",
            "question_kz": "«Жаужүрек мың бала» фильмінде балалар күресіп жатқанда үлкендердің «Әй, бәрекелді!», «Әп-бәрекелді!» сөздері қандай көңіл күйді білдіреді?",
            "options_kz": ["А. Мұң, өкініш 😔", "Ә. Ашу, реніш 😡", "Б. Таңдану, абыржу 😲", "В. Риза болу, қолпаштау 🤲"],
            "correct": 3,
        },
    ],
    # ───── 3. ЖӘ-ЖӘ ─────
    "жә-жә": [
        {
            "quiz_id": "je0",
            "file_id": "",  # FILE_ID ҚОСЫҢЫЗ
            "caption_kz": "🎬 1️⃣ Же-Же — Жаужүрек мың бала",
            "question_kz": "«Жаужүрек мың бала» фильміндегі «Жә-жә» одағайы қандай көңіл күйді білдіреді?",
            "options_kz": ["А. Қуаныш 😀", "Ә. Кейіген ашу, зеку 😤", "Б. Мұң 😔", "В. Таңдану 😲"],
            "correct": 1,
        },
        {
            "quiz_id": "je1",
            "file_id": "",  # FILE_ID ҚОСЫҢЫЗ
            "caption_kz": "🎬 2️⃣ Ракымжаннын «Же» — Жаужүрек мың бала",
            "question_kz": "«Жаужүрек мың бала» фильміндегі «Жә» одағайы қандай сезімді білдіреді?",
            "options_kz": ["А. Сабырға шақыру, тоқтату 🤚", "Ә. Ашу, реніш 😡", "Б. Қуаныш, қолпаштау 🤲", "В. Өкініш, мұңаю 😔"],
            "correct": 0,
        },
    ],
    # ───── 4. ҚАП ─────
    "қап": {
        "file_id": "",  # FILE_ID ҚОСЫҢЫЗ
        "caption_kz": "🎬 Қап! — Жаужүрек мың бала",
        "question_kz": "«Жаужүрек мың бала» фильмінде күресте жеңіліс болған сәтте айтылған «Қап!» одағайы қандай сезімді білдіреді?",
        "options_kz": ["А. Қуану, мақтану 😀", "Ә. Өкініш, қапалану 😔", "Б. Қорқу, абыржу 😱", "В. Қолдау, сүйсіну 🤲"],
        "correct": 1,
    },
    # ───── 5. ОЙБАЙ ─────
    "ойбай": [
        {
            "quiz_id": "oybay0",
            "file_id": "",  # FILE_ID ҚОСЫҢЫЗ
            "caption_kz": "🎬 1️⃣ Ойбай, жыланды қара! — Алдар көсе",
            "question_kz": "«Алдар көсе» телехикаясындағы саудагердің «Ойбай, жыланды қара!» деуі қандай көңіл күйді білдіреді?",
            "options_kz": ["А. Риза болу, қолпаштау 🤲", "Ә. Қуану, сүйсіну 😀", "Б. Қорқу, абыржу 😱", "В. Өкініш, қапалану 😔"],
            "correct": 2,
        },
        {
            "quiz_id": "oybay1",
            "file_id": "",  # FILE_ID ҚОСЫҢЫЗ
            "caption_kz": "🎬 2️⃣ Ойбай! — Алдар көсе",
            "question_kz": "«Алдар көсе» телехикаясындағы «Ойбай!» одағайы қандай көңіл күйді білдіреді?",
            "options_kz": ["А. Қуаныш, сүйсіну 😀", "Ә. Қорқу, сасу 😱", "Б. Риза болу, қолпаштау 🤲", "В. Таңқалу, қызығу 😲"],
            "correct": 1,
        },
    ],
    # ───── 6. ЯПЫР-АЙ ─────
    "япыр-ай": {
        "file_id": "",  # FILE_ID ҚОСЫҢЫЗ
        "caption_kz": "🎬 Япыр-ай! — Алдар көсе",
        "question_kz": "«Алдар көсе» телехикаясындағы «Япырай-ай» одағайы қандай сезімді білдіреді?",
        "options_kz": ["А. Мұң, өкініш 😔", "Ә. Қуаныш, риза болу 😀", "Б. Таңдану, қызығу 😲", "В. Ашу, кейіс 😡"],
        "correct": 2,
    },
    # ───── 7. ӘЙ ─────
    "әй": {
        "file_id": "",  # FILE_ID ҚОСЫҢЫЗ
        "caption_kz": "🎬 Әй, әй! — Алдар көсе",
        "question_kz": "«Алдар көсе» телехикаясындағы байдың «Әй, әй!» деуі қандай сезімді білдіреді?",
        "options_kz": ["А. Мұң 😔", "Ә. Қуаныш 😀", "Б. Таңдану 😲", "В. Абдырау 😱"],
        "correct": 3,
    },
    # ───── 8. ӘТТЕГЕН-АЙ ─────
    "әттеген-ай": {
        "file_id": "",  # FILE_ID ҚОСЫҢЫЗ
        "caption_kz": "🎬 Әттеген-ай! — Алдар көсе",
        "question_kz": "«Алдар көсе» телехикаясындағы байдың «Әттеген-ай!» одағайы қандай сезімді білдіреді?",
        "options_kz": ["А. Риза болу, қолпаштау 🤲", "Ә. Өкініш, мұңаю 😔", "Б. Ашу, кейіс 😡", "В. Таңдану, абыржу 😲"],
        "correct": 2,
    },
    # ───── 9. ҚҰДАЙЫМ-АУ ─────
    "құдайым-ау": {
        "file_id": "",  # FILE_ID ҚОСЫҢЫЗ
        "caption_kz": "🎬 Құдайым-ау! — Көшпенділер",
        "question_kz": "«Көшпенділер» фильміндегі «Құдайым-ау» одағайы қандай көңіл күйді білдіреді?",
        "options_kz": ["А. Мұң, өкініш 😔", "Ә. Ашу, реніш 😡", "Б. Таңдану, қуаныш 😲", "В. Қорқыныш, абыржу 😨"],
        "correct": 2,
    },
    # ───── 10. МӘ ─────
    "мә": {
        "file_id": "",  # FILE_ID ҚОСЫҢЫЗ
        "caption_kz": "🎬 Мә! — Жаужүрек мың бала",
        "question_kz": "«Жаужүрек мың бала» фільміндегі «Мә!» одағайы қандай көңіл күйді білдіреді?",
        "options_kz": ["А. Қуаныш, сүйсіну 😀", "Ә. Таңқалу, таңырқау 😲", "Б. Мұң, қапа 😔", "В. Ашу, реніш 😡"],
        "correct": 1,
    },
}

# ==================== HEALTH CHECK ==================== class Health(BaseHTTPRequestHandler): def do_GET(self): self.send_response(200); self.end_headers(); self.wfile.write(b"OK") def log_message(self, *a): pass # ==================== УТИЛИТТЕР ==================== def self_ping(): if not APP_URL: return while True: time.sleep(300) try: session.get(APP_URL, timeout=10) except Exception as e: log.warning(f"Self-ping қатесі: {e}") def set_bot_commands(): if not TOKEN: return cmds = [ {"command": "start", "description": "🎬 Басты мәзір / Главное меню"}, {"command": "list", "description": "📋 Одақтар тізімі / Список союзов"}, {"command": "lang", "description": "🌐 Тіл өзгерту / Сменить язык"}, {"command": "help", "description": "❓ Қолдау / Помощь"}, ] try: session.post(f"{BASE}/setMyCommands", json={"commands": cmds}, timeout=10) log.info("✅ Bot commands орнатылды!") except Exception as e: log.error(f"set_bot_commands: {e}") # ==================== КЛАВИАТУРАЛАР ==================== def lang_kb(): return {"inline_keyboard": [[ {"text": "🇰🇿 Қазақша", "callback_data": "lang_kz"}, ]]} def main_kb(uid): rows = [] row = [] for word in VIDEOS: row.append({"text": f"🎬 {word}"}) if len(row) == 3: rows.append(row); row = [] if row: rows.append(row) rows.append([ {"text": t(uid, "btn_list")}, {"text": t(uid, "btn_help")}, ]) return {"keyboard": rows, "resize_keyboard": True, "persistent": True} def back_kb(uid): return {"inline_keyboard": [[{"text": t(uid, "btn_menu"), "callback_data": "menu"}]]} def quiz_kb(qid, opts): return {"inline_keyboard": [ [{"text": opts[0], "callback_data": f"q|{qid}|0"}], [{"text": opts[1], "callback_data": f"q|{qid}|1"}], [{"text": opts[2], "callback_data": f"q|{qid}|2"}], [{"text": opts[3], "callback_data": f"q|{qid}|3"}], ]} # ==================== TELEGRAM ==================== def send(cid, text, kb=None): d = {"chat_id": cid, "text": text, "parse_mode": "HTML"} if kb: d["reply_markup"] = kb try: session.post(f"{BASE}/sendMessage", json=d, timeout=10) except Exception as e: log.error(f"send(): {e}") def edit(cid, mid, text, kb=None): d = {"chat_id": cid, "message_id": mid, "text": text, "parse_mode": "HTML"} if kb: d["reply_markup"] = kb try: session.post(f"{BASE}/editMessageText", json=d, timeout=10) except Exception as e: log.error(f"edit(): {e}") def send_video_quiz(cid, word): lang = "kz" data = VIDEOS.get(word) if not data: send(cid, t(cid, "not_found", w=word)); return vlist = data if isinstance(data, list) else [data] for vd in vlist: qid = vd.get("quiz_id", word) cap = vd.get(f"caption_{lang}", vd.get("caption_kz", "")) q = vd.get(f"question_{lang}", vd.get("question_kz", "")) opts = vd.get(f"options_{lang}", vd.get("options_kz", [])) fid = vd.get("file_id", "") if fid: try: session.post(f"{BASE}/sendVideo", json={ "chat_id": cid, "video": fid, "caption": cap, "parse_mode": "HTML", "supports_streaming": True, }, timeout=20) except Exception as e: log.error(f"sendVideo ({word}): {e}") send(cid, t(cid, "quiz_header", q=q), kb=quiz_kb(qid, opts)) log.info(f"✅ {word} → {cid} [{lang}]") def get_quiz(qid): for w, d in VIDEOS.items(): for vd in (d if isinstance(d, list) else [d]): if vd.get("quiz_id", w) == qid: return vd return None # ==================== ХАБАРЛАМА ӨҢДЕУ ==================== def on_message(msg): cid = msg.get("chat", {}).get("id") text = msg.get("text", "").strip() if not cid or not text: return clean = re.sub(r"^[\U0001F000-\U0001FFFF\u2600-\u27FF\U00010000-\U0010FFFF]\s*", "", text).strip() if not clean: clean = text nav = { "📋 Тізім": "/list", "📋 Список": "/list", "❓ Қолдау": "/help", "❓ Помощь": "/help", "🌐 Тіл": "/lang", "🌐 Язык": "/lang", } if clean in nav: clean = nav[clean] cmd = clean.lower().split()[0] if cmd in ("/start", "/menu"): send(cid, t(cid, "welcome"), kb=main_kb(cid)) elif cmd == "/list": items = " • ".join(f"<code>{w}</code>" for w in VIDEOS) send(cid, t(cid, "list_title", n=len(VIDEOS), items=items), kb=back_kb(cid)) elif cmd == "/help": send(cid, t(cid, "help_text"), kb=back_kb(cid)) else: word = clean.lower().strip() if word in VIDEOS: send_video_quiz(cid, word) else: send(cid, t(cid, "not_found", w=clean)) def on_callback(cb): try: cid = cb.get("message", {}).get("chat", {}).get("id") mid = cb.get("message", {}).get("message_id") data = cb.get("data", "") try: session.post(f"{BASE}/answerCallbackQuery", json={"callback_query_id": cb["id"]}, timeout=5) except Exception: pass if data.startswith("q|"): parts = data.split("|") if len(parts) != 3: return _, qid, ans_str = parts try: ans = int(ans_str) except ValueError: return vd = get_quiz(qid) if vd: lang = "kz" c = vd["correct"] opts = vd.get(f"options_{lang}", vd.get("options_kz", [])) if ans == c: edit(cid, mid, t(cid, "correct", ans=opts[c]), kb=back_kb(cid)) else: edit(cid, mid, t(cid, "wrong", user=opts[ans], correct=opts[c]), kb=back_kb(cid)) elif data == "menu": send(cid, t(cid, "welcome"), kb=main_kb(cid)) except Exception as e: log.error(f"on_callback: {e}") def get_updates(offset=None): try: r = session.get(f"{BASE}/getUpdates", params={ "timeout": 30, "offset": offset, "allowed_updates": ["message", "callback_query"], }, timeout=35) return r.json().get("result", []) except Exception as e: log.error(f"getUpdates: {e}"); return [] def process(u): try: if "message" in u: on_message(u["message"]) elif "callback_query" in u: on_callback(u["callback_query"]) except Exception as e: log.error(f"process(): {e}") # ==================== MAIN ==================== def main(): threading.Thread( target=lambda: HTTPServer(("0.0.0.0", PORT), Health).serve_forever(), daemon=True ).start() if APP_URL: threading.Thread(target=self_ping, daemon=True).start() log.info(f"🚀 Bot started! PORT:{PORT}") if not TOKEN: log.error("❌ BOT_TOKEN жоқ!") while True: time.sleep(60) set_bot_commands() offset, delay = None, 1 with ThreadPoolExecutor(max_workers=10) as pool: while True: try: updates = get_updates(offset) for u in updates: offset = u["update_id"] + 1 pool.submit(process, u) if updates: delay = 1 else: time.sleep(1) except Exception as e: log.warning(f"Main loop: {e}") time.sleep(delay) delay = min(delay * 2, 30) if __name__ == "__main__": main()
