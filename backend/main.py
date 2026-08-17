from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
import re
import random
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ""))
from knowledge_base import KNOWLEDGE_BASE, DIRECTIONS, REGIONS, find_answer

app = Flask(__name__)
CORS(app)

# ===== ЗАГРУЗКА ГЛАВНОЙ БАЗЫ =====
DB_FILE = os.path.join(os.path.dirname(__file__), "orgs_full_programs.json")

def load_db():
    """Загрузка главной базы"""
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            db = json.load(f)
            print(f"✅ База: {len(db)} организаций")
            return db
    except Exception as e:
        print(f"⚠️ Ошибка загрузки: {e}")
        return {}

DB = load_db()

# ===== ШУТКИ =====
JOKES = [
    "🔥 Пусто! Как мы с братом муравьёв жарили! Мы были маленькими и счастливыми... А теперь один бизнесмен, другой шизофреник;))",
    "😄 Не нашёл! Как муравьёв — тоже пусто!",
    "🐜 Нет данных! Наверное, как мой брат — ушёл в бизнес и забыл про муравьёв!",
]

# ===== ВСПОМОГАТЕЛЬНЫЕ =====
def get_org(org_id):
    """Получение организации по ID"""
    return DB.get(str(org_id))

def get_org_name(org):
    return org.get("name") or org.get("full_name", "Без названия")

def get_org_programs(org):
    return org.get("programs", [])

def format_org_card(org, index=None):
    """Краткая карточка с data-inn для клика"""
    name = get_org_name(org)
    inn = org.get("inn", "")
    status = org.get("status", "")
    emoji = {20: "✅", 50: "⚠️", 40: "🔒"}.get(status, "📊")
    region = org.get("region", "")
    
    # HTML с data-inn для фронтенда
    html = f'<div class="org-card" data-inn="{inn}">'
    html += f"<b>{index}. {name}</b><br>"
    html += f"🔢 ИНН: {inn}<br>"
    if region:
        html += f"🏛 {region}<br>"
    html += f"{emoji} Статус: {status}"
    html += "</div>"
    
    return html

def format_full_org_card(org):
    """Полная карточка"""
    parts = []
    parts.append(f"📋 <b>{get_org_name(org)}</b>")
    parts.append("─" * 25)
    
    full_name = org.get("full_name")
    if full_name and full_name != org.get("name"):
        parts.append(f"📄 {full_name}")
    
    known = org.get("known_name")
    if known and known != "None":
        parts.append(f"🏷 {known}")
    
    inn = org.get("inn")
    if inn:
        parts.append(f"🔢 ИНН: {inn}")
    
    region = org.get("region")
    if region:
        parts.append(f"🏛 Регион: {region}")
    
    city = org.get("city")
    if city:
        parts.append(f"🏙 Нас. пункт: {city}")
    
    status = org.get("status", "")
    emoji = {20: "✅", 50: "⚠️", 40: "🔒"}.get(status, "📊")
    parts.append(f"{emoji} Статус: {status}")
    
    if org.get("has_limit"):
        parts.append("👥 Лимит: Да")
    
    programs = get_org_programs(org)
    if programs:
        parts.append(f"\n📚 <b>ПРОГРАММЫ ({len(programs)}):</b>")
        for i, prog in enumerate(programs[:20], 1):
            parts.append(f"{i}. {prog}")
        if len(programs) > 20:
            parts.append(f"...и ещё {len(programs) - 20}")
    
    return "\n".join(parts)

def search_orgs(query, limit=10):
    """Поиск организаций"""
    q = query.lower()
    results = []
    
    # По направлению
    for direction in DIRECTIONS:
        if direction in q:
            kws = DIRECTIONS[direction]
            for org_id, org in DB.items():
                text = (get_org_name(org) + " " + " ".join(get_org_programs(org))).lower()
                if any(kw in text for kw in kws):
                    results.append(org)
            if results:
                return results[:limit]
    
    # По названию или программам
    for org_id, org in DB.items():
        name = get_org_name(org).lower()
        programs = " ".join(get_org_programs(org)).lower()
        
        # Ищем по словам запроса
        query_words = q.split()
        if any(w in name or w in programs for w in query_words if len(w) > 2):
            results.append(org)
        
        if len(results) >= limit:
            break
    
    return results

@app.route("/api/chat")
def chat():
    query = request.args.get("query", "").strip()
    if not query:
        return jsonify({"success": False})
    
    text_lower = query.lower()
    
    # 1. База знаний
    answer = find_answer(query)
    if answer:
        return jsonify({"success": True, "type": "knowledge", "answer": answer})
    
    # 2. ИНН
    inn_match = re.search(r'\b(\d{10}|\d{12})\b', query)
    if inn_match:
        inn = inn_match.group(1)
        for org_id, org in DB.items():
            if org.get("inn") == inn:
                return jsonify({"success": True, "type": "organization", "formatted": format_full_org_card(org)})
        return jsonify({"success": True, "type": "knowledge", "answer": random.choice(JOKES)})
    
    # 3. Поиск
    results = search_orgs(query, 10)
    if results:
        # Возвращаем МАССИВ организаций — фронтенд сам разобьёт
        orgs_data = []
        for i, org in enumerate(results, 1):
            orgs_data.append({
                "index": i,
                "name": get_org_name(org),
                "inn": org.get("inn", ""),
                "region": org.get("region", ""),
                "status": org.get("status", ""),
            })
        
        return jsonify({
            "success": True,
            "type": "search_list",
            "count": len(results),
            "organizations": orgs_data
        })
    
    return jsonify({"success": True, "type": "knowledge", "answer": random.choice(JOKES)})

@app.route("/api/random")
def random_org():
    if not DB:
        return jsonify({"success": False})
    org = random.choice(list(DB.values()))
    return jsonify({"success": True, "formatted": "🎲 <b>Случайная:</b>\n\n" + format_full_org_card(org)})

@app.route("/api/stats")
def stats():
    total_progs = sum(len(o.get("programs", [])) for o in DB.values())
    return jsonify({
        "success": True,
        "organizations": len(DB),
        "programs": total_progs
    })

@app.route("/")
def index():
    """Простая HTML страница"""
    return """<!DOCTYPE html>
<html>
<head><title>ChatBolt ПФДО</title><meta charset="utf-8"></head>
<body style="font-family:sans-serif;max-width:600px;margin:50px auto;padding:20px;background:#f0f4ff;border-radius:15px;">
<h1>🤖 ChatBolt ПФДО</h1>
<p>API работает! Используйте:</p>
<ul>
<li><code>?query=танцы</code> — поиск организаций</li>
<li><code>1435177950</code> — проверка по ИНН</li>
</ul>
<form action="/" method="get">
<input type="text" name="query" placeholder="Введите запрос..." style="padding:10px;width:300px;border-radius:8px;border:1px solid #ccc;">
<button style="padding:10px 20px;background:#4f46e5;color:white;border:none;border-radius:8px;cursor:pointer;">Найти</button>
</form>
</body></html>"""

