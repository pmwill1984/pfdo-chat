import json
import requests
import time

print("1. Загрузка базы...")
try:
    with open("/storage/emulated/0/chatbolt/knowledge.json", "r", encoding="utf-8") as f:
        kb = json.load(f)
    print(f"   База загружена: {len(kb)} записей")
except Exception as e:
    print(f"   Ошибка: {e}")
    kb = {}

print("2. Запрос к API ПФДО...")
try:
    response = requests.get(
        "https://api.pfdo.ru/v2/organizations",
        params={"page": 1, "per-page": 5},
        headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"},
        timeout=15
    )
    print(f"   HTTP {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        orgs = data.get("data", [])
        print(f"   Получено: {len(orgs)} организаций")
        
        # Добавляем в базу
        kb["ПФДО"] = {
            "организации": {},
            "общая_информация": {
                "api": "https://api.pfdo.ru/v2",
                "всего_организаций": len(orgs)
            }
        }
        
        for org in orgs:
            kb["ПФДО"]["организации"][str(org["id"])] = {
                "название": org.get("short_name"),
                "инн": org.get("inn")
            }
        
        print("3. Сохранение...")
        with open("/storage/emulated/0/chatbolt/knowledge.json", "w", encoding="utf-8") as f:
            json.dump(kb, f, ensure_ascii=False, indent=2)
        print("   ✅ Сохранено!")
    else:
        print(f"   Ошибка API: {response.status_code}")
except Exception as e:
    print(f"   Ошибка: {e}")

print("\n✅ ГОТОВО!")
