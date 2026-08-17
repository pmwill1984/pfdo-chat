#!/bin/bash

echo "🔑 ПОЛУЧЕНИЕ ТОКЕНА RENDER"
echo "=========================="
echo ""
echo "1. Открой на телефоне: https://render.com"
echo "2. Войди через GitHub"
echo "3. Нажми: Settings (⚙️) → API Keys"
echo "4. Нажми: New API Key"
echo "5. Скопируй токен"
echo ""
echo "После этого выполни:"
echo ""
echo 'export RENDER_TOKEN="ВСТАВЬ_ТОКЕН_СЮДА"'
echo ""
echo "И потом деплой:"
echo ""
cat << 'DEPLOY'
# Деплой через API
curl -X POST "https://api.render.com/v1/services" \
  -H "Authorization: Bearer $RENDER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "web_service",
    "name": "pfdo-chat",
    "runtime": "python",
    "repo": "https://github.com/pmwill1984/pfdo-chat.git",
    "buildCommand": "pip install flask flask-cors requests",
    "startCommand": "cd backend && python main.py"
  }'
DEPLOY
