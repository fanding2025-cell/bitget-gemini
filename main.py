import os
from aiogram import Bot

# Теперь каждый агент привязан к своему токену из Railway
agents = {
    "Геннадий": Bot(token=os.getenv('TOKEN_GENA')),
    "Вика": Bot(token=os.getenv('TOKEN_VIKA')),
    "Демьян": Bot(token=os.getenv('TOKEN_DEMIAN')),
    "Изабелла": Bot(token=os.getenv('TOKEN_IZABELLA')),
    "Леон": Bot(token=os.getenv('TOKEN_LEON')),
    "Рустам": Bot(token=os.getenv('TOKEN_RUSTAM')),
    "Адриан": Bot(token=os.getenv('TOKEN_ADRIAN'))
}

CHAT_ID = "8515064372"
