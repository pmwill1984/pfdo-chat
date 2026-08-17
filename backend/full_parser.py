import requests
import json
import time
import re

class PFDOParser:
    def __init__(self):
        self.base_url = "https://api.pfdo.ru/v2"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Linux; Android 13)",
            "Accept": "application/json"
        })
        self.all_data = {}
    
    def get(self, path, params=None):
        """GET запрос с обработкой ошибок"""
        try:
            response = self.session.get(
                f"{self.base_url}/{path}",
                params=params,
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            return None
    
    def parse_organizations(self, max_pages=50):
        """Парсинг ВСЕХ организаций"""
        print("📋 Парсинг организаций...")
        orgs = []
        
        for page in range(1, max_pages + 1):
            data = self.get("organizations", {"page": page, "per-page": 50})
            if data and data.get("data"):
                orgs.extend(data["data"])
                print(f"  Страница {page}: {len(data['data'])} орг.")
                if len(data["data"]) < 50:
                    break
            else:
                break
            time.sleep(0.3)
        
        self.all_data["organizations"] = orgs
        print(f"✅ Организаций: {len(orgs)}")
        return orgs
    
    def parse_organization_details(self, org_id):
        """Парсинг деталей организации"""
        return self.get(f"organizations/{org_id}")
    
    def parse_by_inn(self, inn):
        """Поиск по ИНН"""
        return self.get(f"organizations/by-inn/{inn}")
    
    def parse_directories(self):
        """Парсинг всех справочников"""
        print("\n📚 Парсинг справочников...")
        
        directories = {
            "organization_types": "directory/organization-types",
            "organizational_forms": "directory-organizational-forms",
            "program_directions": "directory-program-directions",
            "program_activities": "directory-program-activities/",
            "program_documents": "directory-program-documents",
        }
        
        for name, path in directories.items():
            data = self.get(path)
            if data:
                self.all_data[name] = data
                count = len(data.get("data", [])) if isinstance(data, dict) else len(data)
                print(f"  {name}: {count} записей")
            time.sleep(0.2)
    
    def parse_regions(self):
        """Парсинг регионов"""
        print("\n🏛 Парсинг регионов...")
        
        endpoints = [
            "main-page/regions",
            "operator/regions",
            "public/select-region",
        ]
        
        for endpoint in endpoints:
            data = self.get(endpoint)
            if data:
                self.all_data["regions"] = data
                print(f"  {endpoint}: найдено")
                break
    
    def parse_news(self):
        """Парсинг новостей"""
        print("\n📰 Парсинг новостей...")
        data = self.get("public/news")
        if data:
            self.all_data["news"] = data
            print(f"  Новостей: {len(data.get('data', []))}")
    
    def parse_faq(self):
        """Парсинг FAQ"""
        print("\n❓ Парсинг FAQ...")
        endpoints = [
            "faq/checklist",
            "faq/instructions",
            "faq/lessons",
        ]
        
        for endpoint in endpoints:
            data = self.get(endpoint)
            if data:
                self.all_data["faq_" + endpoint.split("/")[-1]] = data
                print(f"  {endpoint}: найдено")
            time.sleep(0.2)
    
    def parse_all(self):
        """Полный парсинг всего портала"""
        print("🚀 ПОЛНЫЙ ПАРСИНГ PFDO.RU\n")
        print("=" * 50)
        
        # 1. Организации
        self.parse_organizations(max_pages=50)
        
        # 2. Справочники
        self.parse_directories()
        
        # 3. Регионы
        self.parse_regions()
        
        # 4. Новости
        self.parse_news()
        
        # 5. FAQ
        self.parse_faq()
        
        # Сохраняем всё
        print("\n💾 Сохранение...")
        with open("parsed_data.json", "w", encoding="utf-8") as f:
            json.dump(self.all_data, f, ensure_ascii=False, indent=2)
        
        print("✅ Данные сохранены в parsed_data.json")
        print(f"📊 Всего записей: {sum(len(v) if isinstance(v, list) else 1 for v in self.all_data.values())}")
        
        return self.all_data

if __name__ == "__main__":
    parser = PFDOParser()
    data = parser.parse_all()
