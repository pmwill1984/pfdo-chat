#!/bin/bash

echo "🤖 CHATBOLT: ДЕПЛОЙ НА RENDER ЧЕРЕЗ CURL"
echo "=========================================="
echo ""

# Токен Render (нужно получить через браузер ОДИН раз)
# После получения — вставь сюда:
RENDER_TOKEN=""

if [ -z "$RENDER_TOKEN" ]; then
    echo "❌ Токен пустой!"
    echo ""
    echo "КАК ПОЛУЧИТЬ ТОКЕН:"
    echo "1. Открой на телефоне: https://dashboard.render.com/settings/api-keys"
    echo "2. Войди через GitHub"
    echo "3. New API Key → скопируй"
    echo ""
    echo "Потом:"
    echo '  sed -i "s/RENDER_TOKEN=\"\"/RENDER_TOKEN=\"ТВОЙ_ТОКЕН\"/" render_curl.sh'
    echo ""
    exit 1
fi

echo "✅ Токен найден!"
echo ""

# Деплой через Render API
echo "🚀 Создание сервиса..."
curl -X POST "https://api.render.com/v1/services" \
  -H "Authorization: Bearer $RENDER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "web_service",
    "name": "pfdo-chat",
    "runtime": "python",
    "repo": "https://github.com/pmwill1984/pfdo-chat.git",
    "branch": "main",
    "buildCommand": "pip install flask flask-cors requests",
    "startCommand": "cd backend && python main.py",
    "plan": "free"
  }' | python3 -m json.tool

echo ""
echo "✅ Готово! URL будет через 2-5 минут"
