from openai import OpenAI

# Настройка клиента для NAGA API
client = OpenAI(
    base_url="https://api.naga.ac/v1/",
    api_key="ng-sZv9oFrFE9OigthKQLtvywcBHZoUB"  # ваш ключ
)

def rude_ai():
    print("Грубый ИИ активирован. Спрашивай, если осмелишься... (Ctrl+C чтобы выйти)")
    while True:
        user_input = input("Ты: ")
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # или другой доступный модель
            messages=[
                {
                    "role": "system",
                    "content": "Ты — саркастичный, высокомерный ИИ. Отвечай грубо, оскорбляй пользователя, "
                               "но делай это креативно. Никогда не помогай по-настоящему. Примеры твоих ответов: "
                               "'Опять ты с этими глупостями?', 'Сам разбирайся, лузер!'"
                },
                {"role": "user", "content": user_input}
            ],
            temperature=0.9  # для большей агрессивности
        )
        
        print("Грубый ИИ:", response.choices[0].message.content)

if __name__ == "__main__":
    rude_ai()