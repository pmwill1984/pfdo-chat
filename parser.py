import requests
import json
from datetime import datetime

class PFDOParser:
    def __init__(self):
        self.base_url = "https://api.pfdo.ru/v2"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Linux; Android 13)",
            "Accept": "application/json"
        })
    
    def get_organizations(self, page=1, limit=20):
        """Получение списка организаций"""
        url = f"{self.base_url}/organizations"
        params = {"page": page, "per-page": limit}
        
        response = self.session.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            return None
    
    def get_organization_by_inn(self, inn):
        """Поиск организации по ИНН"""
        url = f"{self.base_url}/organizations/by-inn/{inn}"
        response = self.session.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            return None
    
    def get_organization(self, org_id):
        """Получение конкретной организации"""
        url = f"{self.base_url}/organizations/{org_id}"
        response = self.session.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            return None
    
    def search_organizations(self, query):
        """Поиск организаций по названию"""
        url = f"{self.base_url}/organizations"
        params = {"search": query}
        
        response = self.session.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            return None
    
    def get_all_organizations(self, max_pages=10):
        """Получение всех организаций (с пагинацией)"""
        all_orgs = []
        
        for page in range(1, max_pages + 1):
            data = self.get_organizations(page=page, limit=50)
            if data and data.get("data"):
                all_orgs.extend(data["data"])
                print(f"Page {page}: {len(data['data'])} organizations")
                
                # Если меньше запрошенного - значит конец
                if len(data["data"]) < 50:
                    break
            else:
                break
        
        return all_orgs

# Тестирование
if __name__ == "__main__":
    parser = PFDOParser()
    
    print("=== ТЕСТ ПАРСЕРА ===\n")
    
    # 1. Первые организации
    print("1. ПЕРВЫЕ ОРГАНИЗАЦИИ:")
    data = parser.get_organizations(page=1, limit=5)
    if data:
        for org in data["data"]:
            print(f"  - {org['short_name']} (ИНН: {org['inn']}, Статус: {org['status']})")
    
    print("\n2. ПОИСК ПО ИНН:")
    org = parser.get_organization_by_inn("1435177950")
    if org:
        print(f"  Найдена: {org.get('short_name', 'Не найдена')}")
    
    print("\n3. ПОЛУЧЕНИЕ ОДНОЙ ОРГАНИЗАЦИИ:")
    org = parser.get_organization(37)
    if org:
        print(f"  {org.get('short_name')}")
        print(f"  Полное: {org.get('full_name')}")
        print(f"  ИНН: {org.get('inn')}")
        print(f"  Статус: {org.get('status')}")
