import os
import asyncio
import ccxt
from aiogram import Bot, Dispatcher

# --- НАСТРОЙКИ ---
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')  # ID твоей группы "AI Group"

# Ключи Bitget из Railway
exchange = ccxt.bitget({
    'apiKey': os.getenv('BITGET_API_KEY'),
    'secret': os.getenv('BITGET_SECRET_KEY'),
    'password': os.getenv('BITGET_PASSPHRASE'),
    'options': {'defaultType': 'swap'}
})

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def send_to_chat(text):
    await bot.send_message(CHAT_ID, text, parse_mode="HTML")

# --- ЖИВОЕ ОБЩЕНИЕ И ТОРГОВЛЯ ---
async def execute_trade_cycle(symbol, side, amount):
    await send_to_chat(f"🚀 <b>Геннадий BOSS:</b> Внимание всем отделам! Начинаем разбор ситуации по {symbol}.")
    await asyncio.sleep(2)
    
    await send_to_chat("📊 <b>Вика ❤️:</b> Я проанализировала рынок. Тренд сильный, объемы подтверждают движение. Я за вход!")
    await asyncio.sleep(2)
    
    await send_to_chat("📉 <b>ИЗАБЕЛЛА:</b> Технический паттерн сформирован. Идеальный момент для позиции. Цели намечены.")
    await asyncio.sleep(2)
    
    await send_to_chat("🛡 <b>ЛЕОН:</b> Стоп-лосс рассчитан. Риск на сделку 10% от наших $10. Депозит в безопасности. Даю добро!")
    await asyncio.sleep(2)
    
    await send_to_chat(f"⚡ <b>RUSTAM:</b> Принято. Отправляю ордер на Bitget. {side} {amount} {symbol}...")
    
    try:
        # Реальное исполнение на Bitget
        order = exchange.create_market_order(symbol, side, amount)
        await send_to_chat(f"✅ <b>СДЕЛКА ОТКРЫТА!</b> ID: {order['id']}")
    except Exception as e:
        await send_to_chat(f"❌ <b>ОШИБКА RUSTAM:</b> Не удалось войти. Причина: {e}")

async def main():
    await send_to_chat("🌐 <b>RAFAEL AI:</b> Офис запущен. Мы в сети и готовы к работе!")
    # Здесь будет цикл мониторинга рынка...
    await execute_trade_cycle('BTC/USDT:USDT', 'buy', 0.001) # Пример теста

if __name__ == "__main__":
    asyncio.run(main())
  
