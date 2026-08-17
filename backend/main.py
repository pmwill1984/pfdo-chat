import os
import sys
import json
import re
import random

from flask import Flask, jsonify, request
from flask_cors import CORS

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from knowledge_base import find_answer

app = Flask(__name__)
CORS(app)

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "orgs_full_programs.json")

def load_db():
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

DB = load_db()

@app.route("/")
def index():
    return "ChatBolt ПФДО работает!"

@app.route("/api/chat")
def chat():
    query = request.args.get("query", "").strip()
    answer = find_answer(query)
    if answer:
        return jsonify({"success": True, "answer": answer})
    return jsonify({"success": True, "message": f"Запрос: {query}"})

if __name__ == "__main__":
    import os
port = int(os.environ.get("PORT", 8000))
app.run(host="0.0.0.0", port=port)
