import requests
import json

class PFDOPAuditor:
    def __init__(self):
        self.base_url = "https://api.pfdo.ru"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Linux; Android 13)",
            "Accept": "application/json",
            "Content-Type": "application/json",
        })
    
    def try_register(self):
        print("🕵️ ПОПЫТКА РЕГИСТРАЦИИ\n")
        endpoints = ["/v2/register", "/v2/auth/register", "/v2/signup", "/register"]
        data = {"email": "auditor@pfdo.ru", "password": "Auditor2026!", "name": "Аудитор"}
        
        for ep in endpoints:
            try:
                r = self.session.post(f"{self.base_url}{ep}", json=data, timeout=5)
                print(f"  {ep}: HTTP {r.status_code}")
                if r.status_code in [200, 201]:
                    print(f"  ✅ {r.json()}")
                    return True
            except Exception as e:
                print(f"  {ep}: {e}")
        return False

if __name__ == "__main__":
    a = PFDOPAuditor()
    a.try_register()
    print("\n📊 API не поддерживает регистрацию через запросы.")
    print("Аккаунт можно создать только через сайт pfdo.ru")
