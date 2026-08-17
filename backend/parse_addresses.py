import requests
import json
import time
import re

class AddressParser:
    def __init__(self):
        self.base_url = "https://api.pfdo.ru/v2"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        })
    
    def try_get_address(self, org_id):
        """Пробуем получить адрес из разных endpoint'ов"""
        endpoints = [
            f"organizations/{org_id}",
            f"organizations/{org_id}/main-documents",
            f"organizations/{org_id}/user",
        ]
        
        for endpoint in endpoints:
            try:
                response = self.session.get(
                    f"{self.base_url}/{endpoint}",
                    timeout=5
                )
                if response.status_code == 200:
                    data = response.json().get("data", {})
                    if isinstance(data, dict):
                        for key in ["address", "адрес", "location", "legal_address", "actual_address", "city", "region"]:
                            if key in data and data[key]:
                                return str(data[key])
            except:
                pass
        
        return None
    
    def extract_from_name(self, full_name):
        """Извлечение адреса из названия"""
        if not full_name:
            return None
        
        # Ищем в кавычках
        quoted = re.findall(r'[«"]([^»"]+)[»"]', full_name)
        if quoted:
            return quoted[-1]
        
        # Ищем "г. Название"
        match = re.search(r'г\.\s*([А-ЯЁ][а-яё]+)', full_name)
        if match:
            return f"г. {match.group(1)}"
        
        # Ищем район/улус
        match = re.search(r'(?:район|улус)[а-яё]*\s*[«"]?([А-ЯЁ][а-яё]+)', full_name)
        if match:
            return f"{match.group(1)} район"
        
        # Ищем ГО
        match = re.search(r'ГО\s*[«"]?\s*([А-ЯЁ][а-яё]+)', full_name)
        if match:
            return f"г. {match.group(1)}"
        
        return None
    
    def parse_all(self):
        print("📍 ПАРСИНГ АДРЕСОВ\n")
        
        with open("parsed_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        orgs = data["organizations"]
        total = len(orgs)
        
        print(f"📊 Организаций: {total}\n")
        
        addresses = {}
        found = 0
        
        for i, org in enumerate(orgs, 1):
            org_id = org.get("id")
            full_name = org.get("full_name", "")
            short_name = org.get("short_name", "")
            
            # 1. Пробуем из названия (быстро)
            address = self.extract_from_name(full_name) or self.extract_from_name(short_name)
            
            # 2. Если не нашли — пробуем API
            if not address:
                address = self.try_get_address(org_id)
            
            if address:
                addresses[org_id] = address
                found += 1
            
            # Прогресс
            if i % 500 == 0:
                print(f"  Обработано: {i}/{total} (адресов: {found})")
        
        # Сохраняем
        with open("addresses.json", "w", encoding="utf-8") as f:
            json.dump(addresses, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ ИТОГО:")
        print(f"  Организаций: {total}")
        print(f"  С адресами: {found} ({found*100//total}%)")
        print(f"  Файл: addresses.json")
        
        return addresses

if __name__ == "__main__":
    parser = AddressParser()
    parser.parse_all()
