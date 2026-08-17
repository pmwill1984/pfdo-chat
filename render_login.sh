#!/bin/bash

echo "🔑 ВХОД В RENDER ЧЕРЕЗ CURL"
echo "============================"
echo ""

# Шаг 1: Получаем ссылку для авторизации
echo "1. Открой на телефоне эту ссылку:"
echo "   https://render.com/login"
echo ""
echo "2. Войди через GitHub"
echo ""
echo "3. После входа, открой:"
echo "   https://render.com/settings/api-keys"
echo ""
echo "4. Нажми New API Key"
echo "5. Скопируй токен"
echo ""
echo "Потом:"
echo '   export RENDER_TOKEN="ТОКЕН"'
echo ""
echo "И выполни деплой:"
echo ""
cat << 'DEPLOY'
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
