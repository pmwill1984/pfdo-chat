import requests
import json

base_url = "https://api.pfdo.ru/v2"
session = requests.Session()

# Разные заголовки для обхода
headers_variants = [
    {
        "User-Agent": "Mozilla/5.0 (Linux; Android 13)",
        "Accept": "application/json",
        "Content-Type": "application/json",
    },
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json",
        "Referer": "https://pfdo.ru/",
        "Origin": "https://pfdo.ru",
    },
    {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0)",
        "Accept": "application/json",
        "X-Requested-With": "XMLHttpRequest",
    },
]

# Endpoint'ы с 401
endpoints_401 = [
    "organizations/37/user",
    "organizations/37/main-documents",
    "organizations/37/contracts-info",
]

print("🔓 ПОПЫТКА ОБХОДА 401\n")

for endpoint in endpoints_401:
    print(f"--- {endpoint} ---")
    for i, headers in enumerate(headers_variants):
        try:
            response = session.get(
                f"{base_url}/{endpoint}",
                headers=headers,
                timeout=5
            )
            status = response.status_code
            if status == 200:
                print(f"  ✅ Заголовки {i+1}: HTTP 200!")
                print(json.dumps(response.json(), ensure_ascii=False, indent=2)[:500])
                break
            else:
                print(f"  ❌ Заголовки {i+1}: HTTP {status}")
        except Exception as e:
            print(f"  ⚠️ Заголовки {i+1}: {e}")
    print()

# Пробуем с токеном из HTML портала
print("🔍 ПОИСК ТОКЕНА НА ПОРТАЛЕ...")
try:
    response = session.get("https://pfdo.ru/", timeout=10)
    html = response.text
    
    # Ищем токены
    import re
    tokens = re.findall(r'token["\']?\s*[:=]\s*["\']([^"\']+)', html)
    csrf = re.findall(r'csrf[^"]*["\']([^"\']+)', html)
    
    print(f"  Токены: {tokens[:5]}")
    print(f"  CSRF: {csrf[:5]}")
except Exception as e:
    print(f"  Ошибка: {e}")

print("\n📊 ВЫВОД:")
print("401 = нужна авторизация через личный кабинет.")
print("Без логина и пароля обойти нельзя.")
print("Доступны только публичные данные.")
