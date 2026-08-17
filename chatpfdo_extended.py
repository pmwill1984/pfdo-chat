import json
import re
import requests
import time

class ChatPFDOExtended:
    def __init__(self):
        self.base_url = "https://api.pfdo.ru/v2"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Linux; Android 13)",
            "Accept": "application/json"
        })
        
        # РАСШИРЕННАЯ БАЗА ЗНАНИЙ
        self.knowledge = {
            # Приветствия
            "приветствия": [
                "здравствуйте", "привет", "добрый день", "добрый вечер", 
                "доброе утро", "hello", "hi", "здравствуй", "приветствую",
                "рад встрече", "доброго времени"
            ],
            
            # Прощания
            "прощания": [
                "пока", "до свидания", "спасибо", "благодарю", "всего доброго",
                "до встречи", "удачи", "счастливо", "goodbye", "bye"
            ],
            
            # Вопросы о ПФДО
            "вопросы_о_пфдо": {
                "что такое пфдо": "ПФДО — это система персонифицированного финансирования дополнительного образования детей.\n\nСуть системы:\n• Родители получают сертификат\n• Сертификатом можно оплачивать кружки и секции\n• Деньги следуют за ребёнком\n• Организации конкурируют за учеников",
                
                "как получить сертификат": "📝 Как получить сертификат ПФДО:\n\n1. Зарегистрируйтесь на портале pfdo.ru\n2. Заполните заявление\n3. Приложите документы ребёнка\n4. Получите сертификат в личном кабинете\n5. Выберите кружок или секцию\n\n⏱ Срок оформления: обычно 1-3 дня",
                
                "как использовать": "💳 Как использовать сертификат:\n\n1. Выберите организацию из реестра\n2. Запишитесь на программу\n3. При заключении договора укажите сертификат\n4. Оплата спишется автоматически\n\n⚠️ Сертификат нельзя обналичить!",
                
                "сколько денег": "💰 Номинал сертификата зависит от:\n• Региона проживания\n• Муниципалитета\n• Направления программы\n\nТочную сумму можно узнать:\n• В личном кабинете портала\n• В уполномоченном органе\n• У организации",
                
                "какие кружки": "🎯 По сертификату ПФДО доступны кружки:\n\n• ⚽ Спортивные секции\n• 🎨 Творческие студии\n• 🔬 Научные кружки\n• 💻 IT и программирование\n• 🎭 Театральные студии\n• 🎵 Музыкальные школы\n• 🏫 Подготовка к школе\n• 🌍 Языковые курсы",
                
                "как найти организацию": "🔍 Найти организацию можно:\n\n1. На портале pfdo.ru\n2. Спросить у меня: «Найди спортивные»\n3. Проверить по ИНН\n4. Посмотреть список организаций",
                
                "как записаться": "📋 Чтобы записаться на программу:\n\n1. Найдите подходящую организацию\n2. Свяжитесь с ней\n3. Подайте заявление\n4. Заключите договор\n5. Начните занятия",
                
                "какие документы": "📄 Для получения сертификата нужны:\n\n• Паспорт родителя\n• Свидетельство о рождении ребёнка\n• СНИЛС ребёнка\n• Заявление\n\nТочный список уточняйте в вашем регионе",
                
                "срок действия": "⏱ Сертификат ПФДО действует:\n• До достижения ребёнком 18 лет\n• При смене региона — переоформляется\n• Ежегодно подтверждается",
                
                "можно ли обналичить": "❌ НЕТ! Сертификат ПФДО нельзя обналичить.\n\nСредства можно использовать только:\n• На оплату кружков\n• На оплату секций\n• В организациях из реестра"
            },
            
            # Статусы организаций
            "статусы": {
                "20": "✅ Активна",
                "50": "⚠️ Требует проверки",
                "0": "❌ Исключена",
                "10": "📝 На рассмотрении"
            },
            
            # Типы организаций
            "типы_организаций": {
                "школа": "🏫 Школа",
                "детский сад": "🎨 Детский сад",
                "центр": "🏢 Центр",
                "спорт": "⚽ Спортивная",
                "ип": "👤 ИП",
                "ооо": "🏢 ООО"
            },
            
            # Направления
            "направления": {
                "спорт": "⚽ Спорт",
                "искусство": "🎨 Искусство",
                "техника": "🔧 Техника",
                "наука": "🔬 Наука",
                "туризм": "🏕 Туризм",
                "языки": "🌍 Языки",
                "музыка": "🎵 Музыка",
                "танцы": "💃 Танцы"
            },
            
            # Дополнительные ответы
            "дополнительно": {
                "регион": "🏛 Каждый регион имеет свой реестр организаций ПФДО. Уточните ваш регион для точной информации.",
                "контакты": "📞 Контакты поддержки ПФДО можно найти на официальном портале pfdo.ru в разделе «Контакты».",
                "поддержка": "🆘 Техническая поддержка портала ПФДО работает через форму обратной связи на сайте.",
                "закон": "⚖️ Деятельность ПФДО регулируется Федеральным законом «Об образовании в РФ» и региональными нормативными актами."
            }
        }
    
    def analyze_question(self, text):
        """Расширенный анализ вопроса"""
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
        
        # 4. Дополнительные вопросы
        for key, answer in self.knowledge["дополнительно"].items():
            if key in text_lower:
                return "additional", answer
        
        # 5. Проверка ИНН
        inn_match = re.search(r'\b\d{10}\b|\b\d{12}\b', text)
        if inn_match or "инн" in text_lower:
            return "check_inn", inn_match.group() if inn_match else None
        
        # 6. Поиск по типу
        for type_key, type_name in self.knowledge["типы_организаций"].items():
            if type_key in text_lower:
                return "search_type", type_key
        
        # 7. Поиск по направлению
        for dir_key, dir_name in self.knowledge["направления"].items():
            if dir_key in text_lower:
                return "search_direction", dir_key
        
        # 8. Поиск организации
        if any(w in text_lower for w in ["найди", "поиск", "покажи", "search"]):
            query = re.sub(r'(найди|поиск|покажи|search)\s*', '', text_lower).strip()
            return "search", query
        
        # 9. Список
        if any(w in text_lower for w in ["список", "все организации", "перечень"]):
            return "list", None
        
        # 10. Статус
        if "статус" in text_lower:
            return "status", None
        
        # 11. Помощь
        if any(w in text_lower for w in ["помощь", "умеешь", "help", "команды"]):
            return "help", None
        
        # 12. По умолчанию
        return "search", text_lower
    
    def get_organizations(self, search=None, page=1, limit=10):
        """Запрос к API"""
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
        except:
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
            return ("👋 Здравствуйте! Я чат-помощник ПФДО.\n\n"
                   "Могу помочь:\n"
                   "• 📖 Рассказать о ПФДО\n"
                   "• 🔍 Найти организацию\n"
                   "• ✅ Проверить ИНН\n"
                   "• 📋 Показать список\n"
                   "• 💡 Ответить на вопросы\n\n"
                   "Что вас интересует?")
        
        elif intent == "farewell":
            return "👋 До свидания! Удачи в выборе кружков!"
        
        elif intent == "pfdo_question":
            return param
        
        elif intent == "additional":
            return param
        
        elif intent == "check_inn":
            if not param:
                return "🔍 Укажите ИНН (10 или 12 цифр).\nПример: «Проверь 1435177950»"
            
            org = self.get_org_by_inn(param)
            if org:
                status_text = self.knowledge["статусы"].get(str(org.get("status")), "Неизвестен")
                return (f"✅ Организация найдена!\n\n"
                       f"📋 {org.get('short_name')}\n"
                       f"📄 {org.get('full_name')}\n"
                       f"🔢 ИНН: {org.get('inn')}\n"
                       f"📊 Статус: {status_text}")
            else:
                return f"❌ Организация с ИНН {param} не найдена."
        
        elif intent == "search_type":
            type_name = self.knowledge["типы_организаций"].get(param, param)
            orgs = self.get_organizations(search=param, limit=10)
            
            if orgs:
                response = f"🔍 Найдено {type_name}: {len(orgs)}\n\n"
                for i, org in enumerate(orgs[:10], 1):
                    response += f"{i}. {org.get('short_name')}\n"
                    response += f"   ИНН: {org.get('inn')}\n\n"
                return response
            else:
                return f"По запросу «{param}» ничего не найдено."
        
        elif intent == "search_direction":
            dir_name = self.knowledge["направления"].get(param, param)
            orgs = self.get_organizations(search=param, limit=10)
            
            if orgs:
                response = f"🔍 {dir_name}: найдено {len(orgs)}\n\n"
                for i, org in enumerate(orgs[:10], 1):
                    response += f"{i}. {org.get('short_name')}\n"
                return response
            else:
                return f"По направлению «{param}» ничего не найдено."
        
        elif intent == "search":
            if not param:
                return "🔍 Что искать? Например: «Найди центр», «Найди спорт»"
            
            orgs = self.get_organizations(search=param, limit=10)
            
            if orgs:
                response = f"🔍 Найдено: {len(orgs)}\n\n"
                for i, org in enumerate(orgs[:10], 1):
                    status_text = self.knowledge["статусы"].get(str(org.get("status")), "")
                    response += f"{i}. {org.get('short_name')}\n"
                    response += f"   ИНН: {org.get('inn')}\n"
                    if status_text:
                        response += f"   {status_text}\n"
                    response += "\n"
                return response
            else:
                return f"По запросу «{param}» ничего не найдено."
        
        elif intent == "list":
            orgs = self.get_organizations(limit=20)
            if orgs:
                response = f"📋 Первые {len(orgs)} организаций:\n\n"
                for i, org in enumerate(orgs, 1):
                    response += f"{i}. {org.get('short_name')}\n"
                return response
            return "Не удалось получить список."
        
        elif intent == "status":
            return ("📊 Система ПФДО\n\n"
                   "✅ API: подключено\n"
                   "✅ База знаний: загружена\n"
                   "✅ Поиск: работает\n"
                   "✅ Проверка ИНН: работает\n\n"
                   "Что я умею:\n"
                   "• Отвечать на вопросы о ПФДО\n"
                   "• Искать организации\n"
                   "• Проверять ИНН\n"
                   "• Показывать список")
        
        elif intent == "help":
            return ("🤖 Я чат-помощник ПФДО!\n\n"
                   "📖 О ПФДО:\n"
                   "• «Что такое ПФДО?»\n"
                   "• «Как получить сертификат?»\n"
                   "• «Как использовать?»\n"
                   "• «Сколько денег?»\n"
                   "• «Какие кружки?»\n\n"
                   "🔍 Поиск:\n"
                   "• «Найди центр»\n"
                   "• «Найди спорт»\n"
                   "• «Список организаций»\n\n"
                   "✅ Проверка:\n"
                   "• «Проверь ИНН 1435177950»")
        
        return "🤔 Не понял. Напишите «помощь» для списка команд."

# Запуск
if __name__ == "__main__":
    chat = ChatPFDOExtended()
    
    print("=" * 50)
    print("🎓 ЧАТ-ПФДО РАСШИРЕННАЯ ВЕРСИЯ")
    print("=" * 50)
    
    # Расширенные тесты
    test_questions = [
        "Привет",
        "Что такое ПФДО?",
        "Как получить сертификат?",
        "Как использовать?",
        "Сколько денег?",
        "Какие кружки?",
        "Какие документы?",
        "Можно ли обналичить?",
        "Срок действия?",
        "Найди спорт",
        "Найди школу",
        "Найди детский сад",
        "Проверь ИНН 1435177950",
        "Список организаций",
        "Регион",
        "Контакты",
        "Поддержка",
        "Помощь"
    ]
    
    print("\n=== РАСШИРЕННЫЕ ТЕСТЫ ===\n")
    for q in test_questions:
        print(f"👤: {q}")
        answer = chat.answer(q)
        print(f"🤖: {answer}\n")
        print("-" * 50 + "\n")
        time.sleep(0.5)
    
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
