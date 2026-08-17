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
        self.rate_limit_delay = 0.5  # Задержка между запросами
    
    def get(self, path, params=None):
        """Базовый GET запрос с задержкой"""
        time.sleep(self.rate_limit_delay)
        url = f"{self.base_url}/{path}"
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                print("⚠️ Требуется авторизация")
                return None
            elif response.status_code == 404:
                print("⚠️ Не найдено")
                return None
            else:
                print(f"⚠️ Ошибка {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Ошибка запроса: {e}")
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
    
    def get_programs(self, org_id):
        """Программы организации"""
        return self.get(f"organizations/{org_id}/programs")
    
    def save_to_json(self, data, filename):
        """Сохранение в JSON"""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ Сохранено в {filename}")
    
    def collect_all_organizations(self, save=True):
        """Сбор всех организаций"""
        all_orgs = []
        page = 1
        
        while True:
            data = self.get_organizations(page=page, limit=50)
            if not data or not data.get("data"):
                break
            
            orgs = data["data"]
            all_orgs.extend(orgs)
            print(f"📄 Страница {page}: {len(orgs)} организаций")
            
            if len(orgs) < 50:
                break
            
            page += 1
            
            # Ограничение для теста
            if page > 100:
                break
        
        print(f"\n✅ Всего собрано: {len(all_orgs)} организаций")
        
        if save:
            self.save_to_json(
                {"collected_at": datetime.now().isoformat(), "organizations": all_orgs},
                "organizations_full.json"
            )
        
        return all_orgs

# Запуск
if __name__ == "__main__":
    parser = PFDOParser()
    
    print("🚀 ЗАПУСК ПАРСЕРА ПФДО\n")
    
    # Тест: первые организации
    print("=" * 50)
    print("ТЕСТ 1: ПЕРВЫЕ ОРГАНИЗАЦИИ")
    print("=" * 50)
    data = parser.get_organizations(page=1, limit=3)
    if data:
        for org in data["data"]:
            print(f"\n📋 {org['short_name']}")
            print(f"   ИНН: {org['inn']}")
            print(f"   Статус: {org['status']}")
            print(f"   ID: {org['id']}")
    
    # Тест: поиск по ИНН
    print("\n" + "=" * 50)
    print("ТЕСТ 2: ПОИСК ПО ИНН")
    print("=" * 50)
    org = parser.get_organization_by_inn("1435177950")
    if org:
        print(f"\n✅ Найдена: {org.get('short_name')}")
        print(f"   Полное: {org.get('full_name')}")
    
    # Тест: конкретная организация
    print("\n" + "=" * 50)
    print("ТЕСТ 3: ОРГАНИЗАЦИЯ №37")
    print("=" * 50)
    org = parser.get_organization(37)
    if org:
        print(f"\n📋 {org.get('short_name')}")
        print(f"   {org.get('full_name')}")
        print(f"   ИНН: {org.get('inn')}")
        print(f"   Статус: {org.get('status')}")
        
        # Ссылки
        if org.get('_links'):
            print("\n   Ссылки:")
            for link_name, link_data in org['_links'].items():
                print(f"   - {link_name}: {link_data['href']}")
