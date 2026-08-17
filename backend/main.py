import os
import sys
import json
import re

from flask import Flask, jsonify, request
from flask_cors import CORS

# Добавляем путь к backend
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from knowledge_base import find_answer

app = Flask(__name__)
CORS(app)

# База организаций
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "orgs_full_programs.json")

def load_db():
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Ошибка загрузки базы: {e}")
        return {}

DB = load_db()
print(f"Загружено организаций: {len(DB)}")

@app.route("/")
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head><title>ChatBolt ПФДО</title><meta charset="utf-8"></head>
    <body style="font-family:sans-serif;padding:50px;text-align:center;">
        <h1>🤖 ChatBolt ПФДО работает!</h1>
        <p>Организаций в базе: """ + str(len(DB)) + """</p>
        <form action="/api/chat" method="get">
            <input name="query" placeholder="Например: танцы" style="padding:10px;width:300px;border-radius:8px;border:1px solid #ccc;">
            <button style="padding:10px 20px;background:#4f46e5;color:white;border:none;border-radius:8px;cursor:pointer;">Найти</button>
        </form>
    </body>
    </html>
    """

@app.route("/api/chat")
def chat():
    query = request.args.get("query", "").strip()
    if not query:
        return jsonify({"success": False, "message": "Пустой запрос"})
    
    # 1. База знаний
    answer = find_answer(query)
    if answer:
        return jsonify({"success": True, "type": "knowledge", "answer": answer})
    
    # 2. Поиск по ИНН
    inn_match = re.search(r'\b(\d{10}|\d{12})\b', query)
    if inn_match:
        inn = inn_match.group(1)
        for org_id, org in DB.items():
            if org.get("inn") == inn:
                return jsonify({
                    "success": True,
                    "type": "organization",
                    "formatted": f"{org.get('name')} | ИНН: {org.get('inn')} | {org.get('region', '')}"
                })
    
    # 3. Поиск по названию/программам
    results = []
    text_lower = query.lower()
    
    for org_id, org in DB.items():
        name = org.get("name", "").lower()
        programs = " ".join(org.get("programs", [])).lower()
        
        if text_lower in name or text_lower in programs:
            results.append({
                "name": org.get("name"),
                "inn": org.get("inn"),
                "region": org.get("region"),
            })
        
        if len(results) >= 10:
            break
    
    if results:
        return jsonify({
            "success": True,
            "type": "search",
            "count": len(results),
            "organizations": results
        })
    
    # 4. Шутка
    return jsonify({
        "success": True,
        "type": "knowledge",
        "answer": "😄 Ничего не найдено! Как мы с братом муравьёв жарили — тоже пусто!"
    })

