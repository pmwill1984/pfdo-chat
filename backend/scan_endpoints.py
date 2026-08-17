import requests

base_url = "https://api.pfdo.ru/v2"
session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0", "Accept": "application/json"})

# Возможные скрытые endpoint'ы
hidden_paths = [
    # Организации
    "organizations/37/details",
    "organizations/37/info",
    "organizations/37/address",
    "organizations/37/contacts",
    "organizations/37/phone",
    "organizations/37/email",
    "organizations/37/programs",
    "organizations/37/courses",
    "organizations/37/schedule",
    "organizations/37/teachers",
    "organizations/37/staff",
    "organizations/37/students",
    "organizations/37/rating",
    "organizations/37/reviews",
    "organizations/37/photos",
    
    # Справочники
    "directory/cities",
    "directory/regions",
    "directory/municipalities",
    "directory/districts",
    "directory/settlements",
    
    # Поиск
    "search/organizations",
    "search/programs",
    "search/courses",
    
    # Статистика
    "stats/organizations",
    "stats/programs",
    "stats/students",
    "statistics",
    
    # Прочее
    "health",
    "status",
    "version",
    "ping",
    "debug",
    "docs",
    "swagger",
    "openapi",
]

print("🕵️ СКАНИРОВАНИЕ СКРЫТЫХ ENDPOINT'ОВ\n")

found = []
for path in hidden_paths:
    url = f"{base_url}/{path}"
    try:
        response = session.get(url, timeout=3)
        status = response.status_code
        
        if status == 200:
            found.append(path)
            print(f"  ✅ {path}: HTTP 200")
        elif status == 401:
            print(f"  🔒 {path}: HTTP 401 (нужна авторизация)")
        elif status == 404:
            pass  # Не найдено
        else:
            print(f"  ⚠️ {path}: HTTP {status}")
    except:
        pass

print(f"\n📊 НАЙДЕНО ОТКРЫТЫХ: {len(found)}")
for path in found:
    print(f"  ✅ {path}")
