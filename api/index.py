from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import re
import sys
import time
import json
import os
import random

sys.path.append(os.path.dirname(__file__))

from knowledge_base import KNOWLEDGE_BASE, DIRECTIONS, REGIONS, NUMBER_WORDS, find_answer

app = Flask(__name__)
CORS(app)

PFDO_API = "https://api.pfdo.ru/v2"

# ===== ЗАГРУЗКА ЕДИНОЙ БАЗЫ =====
def load_unified_db():
    filepath = os.path.join(os.path.dirname(__file__), "unified_db.json")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            db = json.load(f)
            meta = db.get("meta", {})
            print(f"✅ База: {meta.get('total_orgs', 0)} орг, {meta.get('total_progs', 0)} прогр")
            return db
    except Exception as e:
        print(f"⚠️ unified_db.json: {e}")
        return {"orgs": [], "addr": {}, "progs": {}, "org_progs": {}}

DB = load_unified_db()

def get_org_name(org):
    return org.get("name") or org.get("short_name") or "Без названия"

def get_org_address(org):
    org_id = str(org.get("id", ""))
    addr = DB.get("addr", {}).get(org_id)
    if addr:
        return addr
    full = org.get("full_name", "")
    match = re.search(r'г\.\s*([А-ЯЁ][а-яё]+)', full)
    if match:
        return f"г. {match.group(1)}"
    return None

def get_org_programs(org_id):
    prog_ids = DB.get("org_progs", {}).get(str(org_id), [])
    result = []
    for pid in prog_ids:
        prog = DB.get("progs", {}).get(str(pid))
        if prog:
            result.append({
                "id": pid,
                "name": prog.get("n", "Без названия"),
                "status": prog.get("s", 1)
            })
    return result

def format_org_card(org, index=None):
    parts = []
    prefix = f"<b>{index}. </b>" if index else ""
    parts.append(f"{prefix}<b>{get_org_name(org)}</b>")
    inn = org.get("inn")
    if inn:
        parts.append(f"🔢 ИНН: {inn}")
    addr = get_org_address(org)
    if addr:
        parts.append(f"📍 {addr}")
    city = org.get("city")
    if city:
        parts.append(f"🏙 {city}")
    region = org.get("region")
    if region:
        parts.append(f"🏛 {region}")
    status_text = org.get("status_text", "")
    emoji = {"Активна": "✅", "Проверка": "⚠️", "Заблокирована": "🔒"}.get(status_text, "📊")
    parts.append(f"{emoji} {status_text}")
    return "\n".join(parts)

def format_full_org_card(org):
    parts = []
    parts.append(f"📋 <b>{get_org_name(org)}</b>")
    parts.append("─" * 25)
    full_name = org.get("full_name")
    if full_name and full_name != get_org_name(org):
        parts.append(f"📄 {full_name}")
    known = org.get("known_name")
    if known and known != "None" and known != "":
        parts.append(f"🏷 Известна как: {known}")
    inn = org.get("inn")
    if inn:
        parts.append(f"🔢 ИНН: {inn}")
    addr = get_org_address(org)
    parts.append(f"📍 Адрес: {addr or 'не указан'}")
    region = org.get("region")
    if region:
        parts.append(f"🏛 Регион: {region}")
    city = org.get("city")
    if city:
        parts.append(f"🏙 Город: {city}")
    org_type = org.get("type")
    if org_type:
        parts.append(f"🏢 Тип: {org_type}")
    status_text = org.get("status_text", "Неизвестен")
    parts.append(f"📊 Статус: {status_text}")
    parts.append(f"👥 Лимит: {'Да' if org.get('has_limit') else 'Нет'}")
    if org.get("id"):
        parts.append(f"🆔 ID: {org['id']}")
    programs = get_org_programs(org.get("id"))
    if programs:
        parts.append(f"\n📚 <b>ПРОГРАММЫ ({len(programs)}):</b>")
        for i, prog in enumerate(programs, 1):
            emoji = "✅" if prog.get("status") == 1 else "❌"
            parts.append(f"{i}. {prog['name']} {emoji}")
    else:
        parts.append("\n📚 Программы: не найдены")
    return "\n".join(parts)

def extract_number(text):
    match = re.search(r'\b(\d{1,2})\b', text)
    if match and int(match.group(1)) <= 50:
        return int(match.group(1))
    for word, num in NUMBER_WORDS.items():
        if word in text.lower():
            return num
    return None

def extract_direction(text):
    text_lower = text.lower()
    for dir_name in sorted(DIRECTIONS.keys(), key=len, reverse=True):
        for kw in DIRECTIONS[dir_name]:
            if kw in text_lower:
                return dir_name
    return None

def extract_region(text):
    text_lower = text.lower()
    for region, keywords in REGIONS.items():
        for kw in keywords:
            if kw in text_lower:
                return region
    return None

@app.route("/api/chat")
def chat():
    query = request.args.get("query", "").strip()
    if not query:
        return jsonify({"success": False})
    
    text_lower = query.lower()
    
    if "мурав" in text_lower:
        return jsonify({"success": True, "type": "knowledge", "answer": "🐜 Ах да, муравьи! 😄 Мы с братом жарили их в детстве! Что хочешь узнать о ПФДО?"})
    
    answer = find_answer(query)
    if answer:
        return jsonify({"success": True, "type": "knowledge", "answer": answer})
    
    inn_match = re.search(r'\b(\d{10}|\d{12})\b', query)
    if inn_match:
        inn = inn_match.group(1)
        for org in DB.get("orgs", []):
            if org.get("inn") == inn:
                return jsonify({"success": True, "type": "organization", "organization": org, "formatted": format_full_org_card(org)})
        jokes = [
            f"😄 ИНН {inn} не найден! Наверное, как мой брат — потерял его вместе с муравьями! Мы были маленькими и счастливыми... А теперь один бизнесмен, другой шизофреник;))",
            f"🐜 ИНН {inn} нет в базе! Как и муравьёв, которых мы с братом жарили! Мы были маленькими и счастливыми... А теперь один бизнесмен, другой шизофреник;))",
        ]
        return jsonify({"success": True, "type": "knowledge", "answer": random.choice(jokes)})
    
    if "сколько" in text_lower and "организац" in text_lower:
        orgs = DB.get("orgs", [])
        region = extract_region(query)
        if region:
            keywords = REGIONS[region]
            region_orgs = [o for o in orgs if any(kw in (get_org_name(o) + " " + o.get("full_name", "") + " " + (o.get("region") or "")).lower() for kw in keywords)]
            return jsonify({"success": True, "type": "knowledge", "answer": f"📊 В «{region}»: <b>{len(region_orgs)}</b> организаций"})
        return jsonify({"success": True, "type": "knowledge", "answer": f"📊 Всего: <b>{len(orgs)}</b> организаций"})
    
    limit = extract_number(query) or 5
    limit = min(limit, 20)
    direction = extract_direction(query)
    region = extract_region(query)
    
    orgs = DB.get("orgs", [])
    filtered = orgs
    
    if direction:
        keywords = DIRECTIONS[direction]
        filtered = [o for o in filtered if any(kw in (get_org_name(o) + " " + o.get("full_name", "") + " " + o.get("type", "")).lower() for kw in keywords)]
    
    if region:
        keywords = REGIONS[region]
        filtered = [o for o in filtered if any(kw in (get_org_name(o) + " " + o.get("full_name", "") + " " + (o.get("region") or "") + " " + (o.get("city") or "")).lower() for kw in keywords)]
    
    # Фильтр по городу/региону — ищем совпадения
    query_words = [w for w in text_lower.split() if len(w) > 3]
    if query_words:
        city_matches = []
        for o in filtered:
            search_text = (o.get("city") or "") + " " + (o.get("region") or "") + " " + (o.get("full_name") or "")
            if any(w in search_text.lower() for w in query_words):
                city_matches.append(o)
        if city_matches:
            filtered = city_matches
    
    exact = [o for o in filtered if text_lower in get_org_name(o).lower()]
    if exact:
        filtered = exact
    
    if len(filtered) == 1:
        return jsonify({"success": True, "type": "organization", "organization": filtered[0], "formatted": format_full_org_card(filtered[0])})
    
    if not filtered:
        jokes = [
            "😄 Ничего не найдено! Прямо как в тот раз, когда мы с братом искали муравьёв для жарки — тоже пусто! Мы были маленькими и счастливыми... А теперь один бизнесмен, другой шизофреник;))",
            "🐜 Пусто! Как сковородка после того, как мы с братом пожарили всех муравьёв! Эх, были времена... Мы были маленькими и счастливыми. А теперь один бизнесмен, другой шизофреник;))",
            "🤔 Не нашёл. Наверное, как мой брат — ушёл в бизнес и забыл про муравьёв! Мы были маленькими и счастливыми... А теперь один бизнесмен, другой шизофреник;))",
            "😅 Нет данных! Прямо как мой брат не помнит, как мы жарили муравьёв. Мы были маленькими и счастливыми... А теперь один бизнесмен, другой шизофреник;))",
            "🔥 Пусто! Но зато я помню, как мы с братом жарили муравьёв! Мы были маленькими и счастливыми... А теперь один бизнесмен, другой шизофреник;))",
        ]
        return jsonify({"success": True, "type": "knowledge", "answer": random.choice(jokes)})
    
    result = filtered[:limit]
    cards = [format_org_card(o, i) for i, o in enumerate(result, 1)]
    text = "\n\n".join(cards)
    if len(filtered) > limit:
        text += f"\n\n📄 Показано {limit} из {len(filtered)}."
    
    return jsonify({"success": True, "type": "search", "count": len(result), "total_found": len(filtered), "direction": direction, "region": region, "organizations": result, "formatted": text})

@app.route("/api/random")
def random_org():
    orgs = DB.get("orgs", [])
    if not orgs:
        return jsonify({"success": False})
    org = random.choice(orgs)
    return jsonify({"success": True, "type": "organization", "organization": org, "formatted": "🎲 <b>Случайная:</b>\n\n" + format_full_org_card(org)})

@app.route("/api/stats")
def stats():
    return jsonify({
        "success": True,
        "total_organizations": len(DB.get("orgs", [])),
        "total_addresses": len(DB.get("addr", {})),
        "total_programs": len(DB.get("progs", {})),
    })

@app.route("/")
def index():
    return jsonify({"name": "ChatBolt ПФДО API", "status": "active"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
