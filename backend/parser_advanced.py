import requests
import json
import time

class AdvancedParser:
    def __init__(self):
        self.base_url = "https://api.pfdo.ru/v2"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        })
        self.orgs = {}
    
    def get(self, path, params=None):
        try:
            response = self.session.get(
                f"{self.base_url}/{path}",
                params=params,
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None
    
    def parse_all_organizations(self):
        """Парсинг ВСЕХ 515 страниц = 25 744 организаций"""
        print("📋 Парсинг ВСЕХ организаций (515 страниц)...")
        print(f"📊 Ожидается: 25 744 организаций\n")
        
        total_pages = 515
        
        for page in range(1, total_pages + 1):
            data = self.get("organizations", {"page": page, "per-page": 50})
            if data and data.get("data"):
                for org in data["data"]:
                    self.orgs[org["id"]] = org
                
                # Выводим прогресс каждые 10 страниц
                if page % 10 == 0 or page == 1:
                    print(f"  Стр. {page}/{total_pages}: +{len(data['data'])} (всего: {len(self.orgs)})")
            else:
                print(f"  ⚠️ Стр. {page}: нет данных")
                break
            
            # Небольшая задержка
            time.sleep(0.1)
        
        return self.orgs
    
    def save(self):
        orgs_list = list(self.orgs.values())
        with open("parsed_data.json", "w", encoding="utf-8") as f:
            json.dump({"organizations": orgs_list}, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ ИТОГО: {len(orgs_list)} организаций")
        print(f"📁 Сохранено: parsed_data.json")
        return orgs_list

if __name__ == "__main__":
    parser = AdvancedParser()
    parser.parse_all_organizations()
    parser.save()
    print("\n🎉 ПАРСИНГ ЗАВЕРШЁН!")
