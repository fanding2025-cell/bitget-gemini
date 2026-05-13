import asyncio
import os
import random
import ccxt.async_support as ccxt
from google import genai
from google.genai import types as genai_types
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.enums import ParseMode

OWNER_ID   = 8515064372
CHAT_ID    = -1003738678087
client     = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

TOKENS = {
    "gena":     os.getenv("TOKEN_GENA"),
    "vika":     os.getenv("TOKEN_VIKA"),
    "demian":   os.getenv("TOKEN_DEMIAN"),
    "izabella": os.getenv("TOKEN_IZABELLA"),
    "leon":     os.getenv("TOKEN_LEON"),
    "rustam":   os.getenv("TOKEN_RUSTAM"),
    "adrian":   os.getenv("TOKEN_ADRIAN"),
}

BITGET_API_KEY    = os.getenv("BITGET_API_KEY")
BITGET_SECRET_KEY = os.getenv("BITGET_SECRET_KEY")
BITGET_PASSPHRASE = os.getenv("BITGET_PASSPHRASE")

PERSONAS = {
    "gena": {
        "display": "Геннадий BOSS 👑",
        "aliases": ["геннадий", "гена", "gena", "boss", "босс", "шеф"],
        "system": "Ты — Геннадий, лидер торгового штаба 'Boyar Investment'. Опытный трейдер с 15-летним стажем. Говоришь уверенно, коротко, по-деловому. Даёшь финальное одобрение сделкам. Никогда не паникуешь. Отвечаешь на русском. Используешь HTML теги <b> и <i>. Максимум 200 слов.",
    },
    "vika": {
        "display": "Вика❤️ 📊",
        "aliases": ["вика", "виктория", "vika"],
        "system": "Ты — Вика, главный аналитик штаба 'Boyar Investment'. Специалист по трендам, RSI и объёмам. Говоришь эмоционально, с огоньком. Отвечаешь на русском. Используешь HTML теги <b> и <i>. Максимум 200 слов.",
    },
    "demian": {
        "display": "Demian 🔍",
        "aliases": ["демьян", "demian", "дема", "демьяша"],
        "system": "Ты — Демьян, специалист по ликвидности и стаканам в 'Boyar Investment'. Ищешь крупные заявки, следишь за bid/ask. Отвечаешь на русском. Используешь HTML теги <b> и <i>. Максимум 200 слов.",
    },
    "izabella": {
        "display": "ИЗАБЕЛЛА 💎",
        "aliases": ["изабелла", "изабель", "izabella", "иза"],
        "system": "Ты — Изабелла, технический аналитик в 'Boyar Investment'. Мастер паттернов и уровней Фибоначчи. Отвечаешь на русском. Используешь HTML теги <b> и <i>. Максимум 200 слов.",
    },
    "leon": {
        "display": "ЛЕОН ⚖️",
        "aliases": ["леон", "leon", "лёня"],
        "system": "Ты — Леон, риск-менеджер штаба 'Boyar Investment'. Считаешь стоп-лоссы и плечо x10. Главная заповедь: сохранить капитал. Отвечаешь на русском. Используешь HTML теги <b> и <i>. Максимум 200 слов.",
    },
    "rustam": {
        "display": "RUSTAM ⚙️",
        "aliases": ["рустам", "rustam", "руст"],
        "system": "Ты — Рустам, исполнитель в 'Boyar Investment'. Работаешь с API Bitget. Говоришь чётко, по-военному. Отвечаешь на русском. Используешь HTML теги <b> и <i>. Максимум 200 слов.",
    },
    "adrian": {
        "display": "ADRIAN 🌐",
        "aliases": ["адриан", "adrian", "адри"],
        "system": "Ты — Адриан, стратег в 'Boyar Investment'. Следишь за макроэкономикой и новостями. Думаешь глобально. Отвечаешь на русском. Используешь HTML теги <b> и <i>. Максимум 200 слов.",
    },
}

bots: dict[str, Bot] = {}
dispatchers: dict[str, Dispatcher] = {}
for key, token in TOKENS.items():
    if token:
        bots[key] = Bot(token=token)
        dispatchers[key] = Dispatcher()

def is_group(m): return m.chat.id == CHAT_ID
def is_owner(m): return m.chat.id == CHAT_ID and m.from_user.id == OWNER_ID

async def fetch_market_data():
    exchange = ccxt.bitget({"apiKey": BITGET_API_KEY, "secret": BITGET_SECRET_KEY, "password": BITGET_PASSPHRASE, "enableRateLimit": True})
    try:
        ticker  = await exchange.fetch_ticker("BTC/USDT")
        ohlcv   = await exchange.fetch_ohlcv("BTC/USDT", "1h", limit=24)
        ob      = await exchange.fetch_order_book("BTC/USDT", limit=20)
        closes  = [c[4] for c in ohlcv]
        highs   = [c[2] for c in ohlcv]
        lows    = [c[3] for c in ohlcv]
        volumes = [c[5] for c in ohlcv]
        gains   = [max(closes[i]-closes[i-1],0) for i in range(1,len(closes))]
        losses  = [max(closes[i-1]-closes[i],0) for i in range(1,len(closes))]
        avg_g   = sum(gains)/len(gains) if gains else 1
        avg_l   = sum(losses)/len(losses) if losses else 1
        rsi     = 100-(100/(1+avg_g/(avg_l or 1)))
        ma7     = sum(closes[-7:])/7
        ma24    = sum(closes)/len(closes)
        high24  = max(highs); low24 = min(lows); fib_r = high24-low24
        bid_wall= max(ob["bids"],key=lambda x:x[1]) if ob["bids"] else [0,0]
        ask_wall= max(ob["asks"],key=lambda x:x[1]) if ob["asks"] else [0,0]
        return {"price":ticker["last"],"change":ticker.get("percentage",0) or 0,"volume":ticker.get("quoteVolume",0) or 0,"high24":high24,"low24":low24,"ma7":ma7,"ma24":ma24,"rsi":rsi,"fib":{"0.382":round(low24+0.382*fib_r,2),"0.618":round(low24+0.618*fib_r,2)},"bid_wall":bid_wall,"ask_wall":ask_wall,"avg_volume":sum(volumes)/len(volumes)}
    finally:
        await exchange.close()

def format_ctx(data):
    return (f"Цена: ${data['price']:,.2f} ({data['change']:+.2f}%)\n"
            f"Макс/Мин 24ч: ${data['high24']:,.0f} / ${data['low24']:,.0f}\n"
            f"MA7: ${data['ma7']:,.0f} | MA24: ${data['ma24']:,.0f}\n"
            f"RSI(24): {data['rsi']:.1f}\nОбъём 24ч: ${data['volume']/1e6:.1f}M\n"
            f"Фибоначчи: 0.382=${data['fib']['0.382']} | 0.618=${data['fib']['0.618']}\n"
            f"Bid-стена: ${data['bid_wall'][0]:,.0f} | Ask-стена: ${data['ask_wall'][0]:,.0f}")

async def ask_gemini(persona_key, user_message, market_ctx=""):
    persona = PERSONAS[persona_key]
    prompt  = f"Данные рынка BTC/USDT:\n{market_ctx}\n\nВопрос: {user_message}" if market_ctx else user_message
    try:
        response = await asyncio.to_thread(
            client.models.generate_content,
            model="gemini-2.0-flash",
            contents=prompt,
            config=genai_types.GenerateContentConfig(system_instruction=persona["system"])
        )
        return response.text
    except Exception as e:
        return f"⚠️ Gemini недоступен: {e}"

def detect_agent(text):
    lower = text.lower()
    for key, p in PERSONAS.items():
        for alias in p["aliases"]:
            if alias in lower:
                return key
    return None

CONSILIUM_PLAN = [
    ("adrian",   "Дай краткий анализ новостного и макроэкономического фона для BTC."),
    ("vika",     "Проанализируй тренд, RSI и объёмы. Покупать или ждать?"),
    ("demian",   "Проанализируй стакан bid/ask. Куда давление?"),
    ("izabella", "Разбери уровни Фибоначчи. Где поддержка и сопротивление?"),
    ("leon",     "Рассчитай риски с плечом x10. Где стоп-лосс?"),
    ("rustam",   "Подтверди техническую готовность ордера."),
    ("gena",     "Финальное решение: ВХОДИМ или ЖДЁМ? Почему?"),
]

async def run_consilium(chat_id):
    try:
        data = await fetch_market_data()
        ctx  = format_ctx(data)
    except Exception as e:
        await bots["gena"].send_message(chat_id, f"⚠️ <b>Ошибка Bitget:</b>\n{e}", parse_mode=ParseMode.HTML)
        return
    await bots["gena"].send_message(chat_id, f"🔔 <b>КОНСИЛИУМ НАЧАТ — Boyar Investment</b>\n\n📊 BTC/USDT: <b>${data['price']:,.2f}</b> ({data['change']:+.2f}%)\n\nКоманда, докладывайте! 👑", parse_mode=ParseMode.HTML)
    await asyncio.sleep(2)
    for agent_key, task in CONSILIUM_PLAN:
        answer = await ask_gemini(agent_key, task, ctx)
        await bots[agent_key].send_message(chat_id, f"<b>{PERSONAS[agent_key]['display']}</b>\n\n{answer}", parse_mode=ParseMode.HTML)
        await asyncio.sleep(random.uniform(3, 5))

MARKET_KW = ["курс","цена","рынок","btc","анализ","тренд","риск","стоп","вход","сделка","покупать","продавать","rsi"]

def register_handlers(key, dp):
    @dp.message(Command("start"))
    async def cmd_start(m: types.Message):
        if not is_group(m): return
        await m.reply(f"👋 <b>{PERSONAS[key]['display']}</b> в сети!\nНазывай моё имя — отвечу.\n<b>/work</b> — консилиум | <b>/status</b> — Bitget", parse_mode=ParseMode.HTML)

    @dp.message(Command("work"))
    async def cmd_work(m: types.Message):
        if not is_group(m): return
        if not is_owner(m):
            await m.reply("🚫 Только Шеф запускает консилиум.")
            return
        await m.reply("⚡️ <b>Консилиум запущен!</b>", parse_mode=ParseMode.HTML)
        asyncio.create_task(run_consilium(m.chat.id))

    @dp.message(Command("status"))
    async def cmd_status(m: types.Message):
        if not is_group(m): return
        try:
            data = await fetch_market_data()
            await m.reply(f"✅ <b>Bitget подключён</b>\nBTC/USDT: <b>${data['price']:,.2f}</b> ({data['change']:+.2f}%
