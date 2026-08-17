from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import re
import random
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from knowledge_base import KNOWLEDGE_BASE, DIRECTIONS, REGIONS, find_answer

app = Flask(__name__)
CORS(app)

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "orgs_full_programs.json")

def load_db():
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Ошибка: {e}")
        return {}

DB = load_db()

def get_name(org):
    return org.get("name") or "Без названия"

@app.route("/")
def index():
    return """<!DOCTYPE html>
<html><head><title>ChatBolt ПФДО</title><meta charset="utf-8"></head>
<body><h1>🤖 ChatBolt ПФДО</h1>
<form action="/api/chat" method="get">
<input name="query" placeholder="Например: танцы">
<button>Найти</button>
</form></body></html>"""

@app.route("/api/chat")
def chat():
    query = request.args.get("query", "").strip()
    if not query:
        return jsonify({"success": False})
    
    answer = find_answer(query)
    if answer:
        return jsonify({"success": True, "type": "knowledge", "answer": answer})
    
    inn_match = re.search(r'\b(\d{10}|\d{12})\b', query)
    if inn_match:
        inn = inn_match.group(1)
        for org_id, org in DB.items():
            if org.get("inn") == inn:
                return jsonify({"success": True, "type": "organization", "formatted": f"{get_name(org)}"})
    
    results = []
    text_lower = query.lower()
    for org_id, org in DB.items():
        text = (get_name(org) + " " + " ".join(org.get("programs", []))).lower()
        if text_lower in text:
            results.append(org)
        if len(results) >= 10:
            break
    
    if results:
        return jsonify({"success": True, "type": "search", "count": len(results), "organizations": results})
    
    return jsonify({"success": True, "type": "knowledge", "answer": "Ничего не найдено"})

