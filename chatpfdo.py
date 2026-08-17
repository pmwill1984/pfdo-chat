import json
import re
import requests
import time

class ChatPFDO:
    def __init__(self):
        self.base_url = "https://api.pfdo.ru/v2"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Linux; Android 13)",
            "Accept": "application/json"
        })
        
        # База знаний
        self.knowledge = {
            "приветствия": ["здравствуйте", "привет", "добрый", "hello", "hi"],
            "прощания": ["пока", "до свидания", "спасибо", "благодарю"],
            "вопросы_о_пфдо": {
                "что такое пфдо": "ПФДО — это система персонифицированного финансирования дополнительного образования детей. Родители получают сертификат, которым можно оплачивать кружки и секции.",
                "как получить сертификат": "Для получения сертификата ПФДО:\n1. Зарегистрируйтесь на портале pfdo.ru\n2. Подайте заявление\n3. Получите сертификат в личном кабинете\n4. Выберите кружок или секцию",
                "как использовать": "Сертификат ПФДО можно использовать для оплаты занятий в организациях дополнительного образования, которые входят в реестр.",
                "сколько денег": "Номинал сертификата зависит от региона. Точную сумму можно узнать в личном кабинете на портале.",
                "какие кружки": "В реестре ПФДО есть кружки по направлениям: спорт, искусство, техника, наука, туризм и другие."
            },
            "статусы": {
                "20": "✅ Активна",
                "50": "⚠️ Требует проверки",
                "0": "❌ Исключена"
            }
        }
    
    def analyze_question(self, text):
        """Анализ вопроса и определение намерения"""
        text_lower = text.lower().strip()
        
        # 1. Приветствие
        if any(word in text_lower for word in self.knowledge["приветствия"]):
            return "greeting", None
        
        # 2. Прощание
        if any(word in text_lower for word in self.knowledge["прощания"]):
            return "farewell", None
        
        # 3. Вопросы о ПФДО
        for question, answer in self.knowledge["вопросы_о_пфдо"].items():
            if question in text_lower:
                return "pfdo_question", answer
        
        # 4. Проверка ИНН
        inn_match = re.search(r'\b\d{10}\b|\b\d{12}\b', text)
        if inn_match or "инн" in text_lower:
            return "check_inn", inn_match.group() if inn_match else None
        
        # 5. Поиск организации
        if any(w in text_lower for w in ["найди", "поиск", "покажи", "search"]):
            query = re.sub(r'(найди|поиск|покажи|search)\s*', '', text_lower).strip()
            return "search", query
        
        # 6. Список организаций
        if any(w in text_lower for w in ["список", "все организации", "перечень"]):
            return "list", None
        
        # 7. Статус
        if "статус" in text_lower:
            return "status", None
        
        # 8. Помощь
        if any(w in text_lower for w in ["помощь", "умеешь", "help"]):
            return "help", None
        
        # 9. По умолчанию — поиск
        return "search", text_lower
    
    def get_organizations(self, search=None, page=1, limit=10):
        """Запрос к API ПФДО"""
        try:
            params = {"page": page, "per-page": limit}
            if search:
                params["search"] = search
            
            response = self.session.get(
                f"{self.base_url}/organizations",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])
            return []
        except Exception as e:
            print(f"⚠️ Ошибка API: {e}")
            return []
    
    def get_org_by_inn(self, inn):
        """Поиск по ИНН"""
        try:
            response = self.session.get(
                f"{self.base_url}/organizations/by-inn/{inn}",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("data")
            return None
        except:
            return None
    
    def answer(self, question):
        """Формирование ответа"""
        intent, param = self.analyze_question(question)
        
        if intent == "greeting":
            return "👋 Здравствуйте! Я чат-помощник ПФДО.\n\nМогу помочь:\n• Найти организацию\n• Проверить ИНН\n• Рассказать о ПФДО\n• Показать список организаций\n\nЧто вас интересует?"
        
        elif intent == "farewell":
            return "👋 До свидания! Если появятся вопросы — обращайтесь!"
        
        elif intent == "pfdo_question":
            return param
        
        elif intent == "check_inn":
            if not param:
                return "🔍 Укажите ИНН организации (10 или 12 цифр).\nНапример: 'Проверь 1435177950'"
            
            org = self.get_org_by_inn(param)
            if org:
                status_text = self.knowledge["статусы"].get(str(org.get("status")), "Неизвестен")
                return (f"✅ Организация найдена!\n\n"
                       f"📋 Название: {org.get('short_name')}\n"
                       f"📄 Полное: {org.get('full_name')}\n"
                       f"🔢 ИНН: {org.get('inn')}\n"
                       f"📊 Статус: {status_text}")
            else:
                return f"❌ Организация с ИНН {param} не найдена в реестре ПФДО."
        
        elif intent == "search":
            if not param:
                return "🔍 Что искать? Например:\n• 'Найди спортивные'\n• 'Найди центр'\n• 'Найди школу'"
            
            orgs = self.get_organizations(search=param, limit=10)
            
            if not orgs:
                return f"По запросу «{param}» ничего не найдено."
            
            response = f"🔍 Найдено организаций: {len(orgs)}\n\n"
            for i, org in enumerate(orgs[:10], 1):
                status_text = self.knowledge["статусы"].get(str(org.get("status")), "")
                response += f"{i}. {org.get('short_name')}\n"
                response += f"   ИНН: {org.get('inn')}\n"
                if status_text:
                    response += f"   Статус: {status_text}\n"
                response += "\n"
            
            if len(orgs) > 10:
                response += f"...и ещё {len(orgs) - 10} организаций"
            
            return response
        
        elif intent == "list":
            orgs = self.get_organizations(limit=20)
            
            if not orgs:
                return "Не удалось получить список организаций."
            
            response = f"📋 Первые {len(orgs)} организаций:\n\n"
            for i, org in enumerate(orgs, 1):
                response += f"{i}. {org.get('short_name')}\n"
            
            return response
        
        elif intent == "status":
            return ("📊 Система ПФДО работает\n\n"
                   "Что я умею:\n"
                   "✅ Искать организации\n"
                   "✅ Проверять ИНН\n"
                   "✅ Отвечать на вопросы о ПФДО\n"
                   "✅ Показывать список организаций")
        
        elif intent == "help":
            return ("🤖 Я чат-помощник ПФДО!\n\n"
                   "Примеры вопросов:\n"
                   "• «Найди спортивные секции»\n"
                   "• «Проверь ИНН 1435177950»\n"
                   "• «Что такое ПФДО?»\n"
                   "• «Как получить сертификат?»\n"
                   "• «Список организаций»\n"
                   "• «Статус»")
        
        return "🤔 Не понял вопрос. Напишите «помощь» для списка команд."

# Запуск чата
if __name__ == "__main__":
    chat = ChatPFDO()
    
    print("=" * 50)
    print("🎓 ЧАТ-ПФДО ОБУЧЕН И ГОТОВ К РАБОТЕ")
    print("=" * 50)
    print("\nВведите 'выход' для завершения\n")
    
    # Тестовые вопросы
    test_questions = [
        "Привет",
        "Что такое ПФДО?",
        "Как получить сертификат?",
        "Найди центр",
        "Проверь ИНН 1435177950",
        "Список организаций",
        "Статус",
        "Помощь"
    ]
    
    print("=== ТЕСТОВЫЕ ВОПРОСЫ ===\n")
    for q in test_questions:
        print(f"👤: {q}")
        answer = chat.answer(q)
        print(f"🤖: {answer}\n")
        print("-" * 50 + "\n")
        time.sleep(1)
    
    # Интерактивный режим
    print("\n=== ИНТЕРАКТИВНЫЙ РЕЖИМ ===\n")
    while True:
        try:
            user_input = input("👤: ").strip()
            if user_input.lower() in ["выход", "exit", "quit"]:
                print("🤖: До свидания!")
                break
            if user_input:
                answer = chat.answer(user_input)
                print(f"🤖: {answer}\n")
        except KeyboardInterrupt:
            print("\n🤖: До свидания!")
            break
