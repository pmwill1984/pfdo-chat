import requests
import json
import time
from datetime import datetime

class PFDOParser:
    def __init__(self):
        self.base_url = "https://api.pfdo.ru/v2"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Linux; Android 13)",
            "Accept": "application/json",
            "Content-Type": "application/json"
        })
        self.rate_limit_delay = 0.3
    
    def get(self, path, params=None):
        """Базовый GET запрос"""
        time.sleep(self.rate_limit_delay)
        url = f"{self.base_url}/{path}"
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # Проверяем разные форматы ответа
                if "data" in data:
                    return data["data"]
                return data
            else:
                print(f"⚠️ HTTP {response.status_code}: {url}")
                return None
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return None
    
    def get_organizations(self, page=1, limit=20, search=None):
        """Список организаций"""
        params = {"page": page, "per-page": limit}
        if search:
            params["search"] = search
        return self.get("organizations", params)
    
    def get_organization(self, org_id):
        """Конкретная организация"""
        return self.get(f"organizations/{org_id}")
    
    def get_organization_by_inn(self, inn):
        """Организация по ИНН"""
        return self.get(f"organizations/by-inn/{inn}")
    
    def search(self, query):
        """Поиск организаций"""
        return self.get("organizations", {"search": query})
    
    def collect_all(self, max_pages=50):
        """Сбор всех организаций"""
        all_orgs = []
        
        for page in range(1, max_pages + 1):
            data = self.get_organizations(page=page, limit=50)
            
            if not data:
                break
            
            # Если data - список
            if isinstance(data, list):
                all_orgs.extend(data)
                print(f"📄 Стр. {page}: {len(data)} орг.")
                if len(data) < 50:
                    break
            # Если data - словарь с ключом data
            elif isinstance(data, dict) and "data" in data:
                orgs = data["data"]
                all_orgs.extend(orgs)
                print(f"📄 Стр. {page}: {len(orgs)} орг.")
                if len(orgs) < 50:
                    break
            else:
                break
        
        print(f"\n✅ Всего: {len(all_orgs)} организаций")
        return all_orgs
    
    def save_json(self, data, filename):
        """Сохранение в JSON"""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ Сохранено: {filename}")

# Тестирование
if __name__ == "__main__":
    parser = PFDOParser()
    
    print("🚀 ТЕСТ ПАРСЕРА ПФДО v2\n")
    
    # Тест 1: Список
    print("=" * 50)
    print("ТЕСТ 1: СПИСОК ОРГАНИЗАЦИЙ")
    print("=" * 50)
    orgs = parser.get_organizations(page=1, limit=3)
    if orgs:
        for org in orgs:
            print(f"  {org.get('short_name', 'N/A')} | ИНН: {org.get('inn', 'N/A')}")
    
    # Тест 2: По ИНН
    print("\n" + "=" * 50)
    print("ТЕСТ 2: ПОИСК ПО ИНН 1435177950")
    print("=" * 50)
    org = parser.get_organization_by_inn("1435177950")
    if org:
        if isinstance(org, list):
            org = org[0] if org else None
        if org:
            print(f"  Название: {org.get('short_name')}")
            print(f"  Полное: {org.get('full_name')}")
            print(f"  ИНН: {org.get('inn')}")
    
    # Тест 3: Конкретная
    print("\n" + "=" * 50)
    print("ТЕСТ 3: ОРГАНИЗАЦИЯ №37")
    print("=" * 50)
    org = parser.get_organization(37)
    if org:
        if isinstance(org, list):
            org = org[0] if org else None
        if org:
            print(f"  Название: {org.get('short_name')}")
            print(f"  Полное: {org.get('full_name')}")
            print(f"  ИНН: {org.get('inn')}")
            print(f"  Статус: {org.get('status')}")
    
    # Тест 4: Поиск
    print("\n" + "=" * 50)
    print("ТЕСТ 4: ПОИСК 'Центр'")
    print("=" * 50)
    results = parser.search("Центр")
    if results:
        if isinstance(results, list):
            for org in results[:3]:
                print(f"  {org.get('short_name')}")
        elif isinstance(results, dict) and "data" in results:
            for org in results["data"][:3]:
                print(f"  {org.get('short_name')}")
