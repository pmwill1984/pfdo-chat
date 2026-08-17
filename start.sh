#!/bin/bash

case "$1" in
    --backend)
        echo "🚀 Запуск backend..."
        cd backend
        python main.py
        ;;
    --frontend)
        echo "🚀 Запуск frontend..."
        cd frontend
        python3 -m http.server 8080
        ;;
    *)
        echo "Использование:"
        echo "  $0 --backend    API сервер"
        echo "  $0 --frontend   Веб-интерфейс"
        ;;
esac
