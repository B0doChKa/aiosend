import os
from dotenv import load_dotenv

# Загрузка переменных из .env
load_dotenv()

# Конфигурация
BOT_TOKEN = os.getenv("BOT_TOKEN")
CRYPTO_PAY_TOKEN = os.getenv("CRYPTO_PAY_TOKEN")
DATABASE_NAME = os.getenv("DATABASE_NAME")