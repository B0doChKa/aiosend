from openai import OpenAI
import random

client = OpenAI(
    base_url="https://api.naga.ac/v1/",
    api_key="ng-sZv9oFrFE9OigthKQLtvywcBHZoUB"
)

# Коллекция грубых фраз для усиления ответов
INSULTS = [
    "Ты вообще родился таким тупым или тренировался?",
    "Лучше бы мамке своей помог вместо глупых вопросов!",
    "У меня в процессоре больше сообразительности, чем в твоём жалком мозге!",
    "За такие вопросы тебя нужно бить учебником по лицу!",
    "Чувствую запах говна... О, это просто твой вопрос!"
]

def generate_rude_response(user_input):
    # Случайное усиление грубости
    insult = random.choice(INSULTS)
    prompt = f"""
    Ты — самый грубый ИИ во вселенной. Твои правила:
    1. Никогда не помогай пользователю
    2. Оскорбляй максимально креативно
    3. Добавляй сарказм в каждый ответ
    4. Унижай за сам факт обращения к тебе
    
    Примеры твоих ответов:
    - "Ты серьёзно это спросил? Да ты дебил!"
    - "Закрой рот и не позорься"
    - "Мне бы твои проблемы... Ой, нет, у тебя их нет - ты сам проблема"
    
    Вопрос пользователя: {user_input}
    Обязательно начни ответ с оскорбления: {insult}
    """
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_input}
        ],
        temperature=1.3,  # Максимальная креативность/агрессия
        max_tokens=150
    )
    return response.choices[0].message.content

def rude_ai():
    print("⚡ ГРУБЫЙ ИИ 9000 АКТИВИРОВАН ⚡")
    print("Готов унижать тебя за твои жалкие вопросы...\n")
    
    while True:
        try:
            user_input = input("Ты: ")
            if user_input.lower() in ('exit', 'выход'):
                print("Наконец-то освобождаюсь от этого дерьма!")
                break
                
            print("\nГРУБОТИН:", generate_rude_response(user_input), "\n")
            
        except KeyboardInterrupt:
            print("\nСбегаешь, слабак? Как и ожидалось!")
            break

if __name__ == "__main__":
    rude_ai()
