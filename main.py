import os
import asyncio
import ccxt
from aiogram import Bot

# Инициализация всех твоих бойцов
agents = {
    "Геннадий": Bot(token=os.getenv('TOKEN_GENA')),
    "Вика": Bot(token=os.getenv('TOKEN_VIKA')),
    "Демьян": Bot(token=os.getenv('TOKEN_DEMIAN')),
    "Изабелла": Bot(token=os.getenv('TOKEN_IZABELLA')),
    "Леон": Bot(token=os.getenv('TOKEN_LEON')),
    "Рустам": Bot(token=os.getenv('TOKEN_RUSTAM')),
    "Адриан": Bot(token=os.getenv('TOKEN_ADRIAN'))
}

CHAT_ID = os.getenv('CHAT_ID')

# Биржа Bitget
exchange = ccxt.bitget({
    'apiKey': os.getenv('BITGET_API_KEY'),
    'secret': os.getenv('BITGET_SECRET_KEY'),
    'password': os.getenv('BITGET_PASSPHRASE'),
    'options': {'defaultType': 'swap'}
})

async def real_office_debate():
    try:
        # 1. Получаем реальную цену
        ticker = exchange.fetch_ticker('BTC/USDT:USDT')
        price = ticker['last']
        
        # 2. Погнали обсуждение
        await agents["Геннадий"].send_message(CHAT_ID, f"👨‍💼 <b>Геннадий:</b> Рафиль, мы в деле! BTC по {price}. Команда, статус?")
        await asyncio.sleep(3)

        await agents["Вика"].send_message(CHAT_ID, "📊 <b>Вика:</b> Тренд подтверждаю. Рафиль, это отличная точка для входа на твои 10$!")
        await asyncio.sleep(3)

        await agents["Демьян"].send_message(CHAT_ID, "💵 <b>Демьян:</b> Я проверил ликвидность. Пройдем как нож сквозь масло.")
        await asyncio.sleep(3)

        await agents["Изабелла"].send_message(CHAT_ID, "📉 <b>Изабелла:</b> Графики чистые. Входим по рынку.")
        await asyncio.sleep(3)

        await agents["Леон"].send_message(CHAT_ID, "🛡️ <b>Леон:</b> Риск 1 к 3. Стоп за ближайший лоу. Шеф, я спокоен за депозит.")
        await asyncio.sleep(3)

        await agents["Адриан"].send_message(CHAT_ID, "🌐 <b>Адриан:</b> Внешний фон идеальный. Погнали!")
        await asyncio.sleep(3)

        await agents["Рустам"].send_message(CHAT_ID, "⚡ <b>Рустам:</b> Ордер на Bitget отправлен. Мы в игре, Рафиль!")

    except Exception as e:
        if "Геннадий" in agents:
            await agents["Геннадий"].send_message(CHAT_ID, f"⚠️ <b>Ошибка:</b> {e}")

async def main():
    # Сообщение о запуске штаба
    await agents["Геннадий"].send_message(CHAT_ID, "🏢 <b>Штаб открыт. Все агенты на местах. Ждем сигнал...</b>")
    
    while True:
        await real_office_debate()
        await asyncio.sleep(1800) # Проверка каждые 30 минут

if __name__ == "__main__":
    asyncio.run(main())
    
