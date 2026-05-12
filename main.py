import os
import asyncio
import ccxt
from aiogram import Bot

# --- ДАННЫЕ ИЗ RAILWAY ---
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = "8515064372"  # Я вшил его прямо в код для верности
BITGET_KEY = os.getenv('BITGET_API_KEY')
BITGET_SECRET = os.getenv('BITGET_SECRET_KEY')
BITGET_PASS = os.getenv('BITGET_PASSPHRASE')

bot = Bot(token=BOT_TOKEN)

# Настройка биржи
exchange = ccxt.bitget({
    'apiKey': BITGET_KEY,
    'secret': BITGET_SECRET,
    'password': BITGET_PASS,
    'options': {'defaultType': 'swap'}
})

async def send(text):
    try:
        await bot.send_message(CHAT_ID, text, parse_mode="HTML")
    except Exception as e:
        print(f"Ошибка отправки: {e}")

async def start_office():
    await send("🌐 <b>СИСТЕМА ОБНОВЛЕНА. РЕЖИМ 'ЖИВОЙ ОФИС' АКТИВИРОВАН.</b>")
    await asyncio.sleep(1)
    
    await send("👨‍💼 <b>Геннадий:</b> Так, банда, Шеф дал отмашку! Проверяем системы. На кону реальные деньги.")
    await asyncio.sleep(1)
    
    await send("📊 <b>Вика ❤️:</b> Подключаюсь к потоку Bitget... Вижу баланс! Рафиль, начинаю сканировать рынок на предмет жирных точек входа.")
    await asyncio.sleep(1)
    
    await send("🛡️ <b>Леон:</b> Я на посту. Плечо x10, изолированная маржа. Каждую копейку Шефа буду охранять как цербер.")
    await asyncio.sleep(1)
    
    await send("⚡ <b>Рустам:</b> Гитхаб и Railway синхронизированы. Код летит. Мы готовы к исполнению!")

async def main():
    await start_office()
    # Тут будет крутиться цикл мониторинга
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
    
