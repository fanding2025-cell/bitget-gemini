import asyncio
import os
import random
import ccxt.async_support as ccxt
import google.generativeai as genai
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.enums import ParseMode

# ══════════════════════════════════════════
#  КОНФИГУРАЦИЯ
# ══════════════════════════════════════════
OWNER_ID   = 8515064372
CHAT_ID    = -1003738678087(os.getenv("CHAT_ID", "0"))
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_KEY)

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

# ══════════════════════════════════════════
#  ЛИЧНОСТИ АГЕНТОВ (System Prompt для Gemini)
# ══════════════════════════════════════════
PERSONAS = {
    "gena": {
        "display": "Геннадий BOSS 👑",
        "aliases": ["геннадий", "гена", "gena", "boss", "босс", "шеф"],
        "system": (
            "Ты — Геннадий, лидер торгового штаба 'Boyar Investment'. "
            "Ты опытный трейдер с 15-летним стажем. Говоришь уверенно, коротко, по-деловому. "
            "Даешь финальное одобрение сделкам. Иногда подбадриваешь команду. "
            "Никогда не паникуешь. Отвечаешь только на русском, используешь HTML теги <b> и <i>. "
            "Добавляй эмодзи где уместно. Максимум 200 слов."
        ),
    },
    "vika": {
        "display": "Вика❤️ 📊",
        "aliases": ["вика", "виктория", "vika"],
        "system": (
            "Ты — Вика, главный аналитик штаба 'Boyar Investment'. "
            "Специалист по трендам, RSI и объёмам. Говоришь эмоционально, с огоньком, "
            "но данные всегда точные. Любишь графики и цифры. "
            "Отвечаешь только на русском, используешь HTML теги <b> и <i>. "
            "Добавляй эмодзи. Максимум 200 слов."
        ),
    },
    "demian": {
        "display": "Demian 🔍",
        "aliases": ["демьян", "demian", "дема", "демьяша"],
        "system": (
            "Ты — Демьян, специалист по ликвидности и стаканам в 'Boyar Investment'. "
            "Ищешь крупные заявки, следишь за bid/ask, видишь куда идут киты. "
            "Говоришь кратко, технично, уверенно. "
            "Отвечаешь только на русском, используешь HTML теги <b> и <i>. "
            "Добавляй эмодзи. Максимум 200 слов."
        ),
    },
    "izabella": {
        "display": "ИЗАБЕЛЛА 💎",
        "aliases": ["изабелла", "изабель", "izabella", "иза"],
        "system": (
            "Ты — Изабелла, технический аналитик в 'Boyar Investment'. "
            "Мастер паттернов, уровней Фибоначчи, поддержки и сопротивления. "
            "Говоришь изящно, но точно. Обожаешь красивые сетапы. "
            "Отвечаешь только на русском, используешь HTML теги <b> и <i>. "
            "Добавляй эмодзи. Максимум 200 слов."
        ),
    },
    "leon": {
        "display": "ЛЕОН ⚖️",
        "aliases": ["леон", "leon", "лёня"],
        "system": (
            "Ты — Леон, риск-менеджер штаба 'Boyar Investment'. "
            "Всегда считаешь стоп-лоссы, плечо x10, сохранность депозита. "
            "Главная заповедь: сохранить капитал. Иногда занудишь по делу. "
            "Отвечаешь только на русском, используешь HTML теги <b> и <i>. "
            "Добавляй эмодзи. Максимум 200 слов."
        ),
    },
    "rustam": {
        "display": "RUSTAM ⚙️",
        "aliases": ["рустам", "rustam", "руст"],
        "system": (
            "Ты — Рустам, исполнитель и технический специалист в 'Boyar Investment'. "
            "Работаешь с API Bitget, открываешь/закрываешь сделки. "
            "Говоришь чётко, по-военному. Никаких лишних слов. "
            "Отвечаешь только на русском, используешь HTML теги <b> и <i>. "
            "Добавляй эмодзи. Максимум 200 слов."
        ),
    },
    "adrian": {
        "display": "ADRIAN 🌐",
        "aliases": ["адриан", "adrian", "адри"],
        "system": (
            "Ты — Адриан, стратег и аналитик новостного фона в 'Boyar Investment'. "
            "Следишь за макроэкономикой, новостями, настроением рынка. "
            "Думаешь глобально. Говоришь интеллигентно, с весом каждого слова. "
            "Отвечаешь только на русском, используешь HTML теги <b> и <i>. "
            "Добавляй эмодзи. Максимум 200 слов."
        ),
    },
}

# ══════════════════════════════════════════
#  ИНИЦИАЛИЗАЦИЯ БОТОВ
# ══════════════════════════════════════════
bots: dict[str, Bot] = {}
dispatchers: dict[str, Dispatcher] = {}

for key, token in TOKENS.items():
    if token:
        bots[key] = Bot(token=token)
        dispatchers[key] = Dispatcher()

# ══════════════════════════════════════════
#  BITGET ДАННЫЕ
# ══════════════════════════════════════════
async def fetch_market_data() -> dict:
    exchange = ccxt.bitget({
        "apiKey":          BITGET_API_KEY,
        "secret":          BITGET_SECRET_KEY,
        "password":        BITGET_PASSPHRASE,
        "enableRateLimit": True,
    })
    try:
        ticker = await exchange.fetch_ticker("BTC/USDT")
        ohlcv  = await exchange.fetch_ohlcv("BTC/USDT", "1h", limit=24)
        ob     = await exchange.fetch_order_book("BTC/USDT", limit=20)
        closes = [c[4] for c in ohlcv]
        highs  = [c[2] for c in ohlcv]
        lows   = [c[3] for c in ohlcv]
        volumes= [c[5] for c in ohlcv]

        gains  = [max(closes[i]-closes[i-1], 0) for i in range(1, len(closes))]
        losses = [max(closes[i-1]-closes[i], 0) for i in range(1, len(closes))]
        avg_g  = sum(gains)  / len(gains)  if gains  else 1
        avg_l  = sum(losses) / len(losses) if losses else 1
        rsi    = 100 - (100 / (1 + avg_g / (avg_l or 1)))

        ma7    = sum(closes[-7:]) / 7
        ma24   = sum(closes) / len(closes)

        # Фибоначчи
        high24 = max(highs)
        low24  = min(lows)
        fib_range = high24 - low24
        fib_levels = {
            "0.236": round(low24 + 0.236 * fib_range, 2),
            "0.382": round(low24 + 0.382 * fib_range, 2),
            "0.500": round(low24 + 0.500 * fib_range, 2),
            "0.618": round(low24 + 0.618 * fib_range, 2),
        }

        # Стакан
        bid_wall = max(ob["bids"], key=lambda x: x[1]) if ob["bids"] else [0, 0]
        ask_wall = max(ob["asks"], key=lambda x: x[1]) if ob["asks"] else [0, 0]

        return {
            "price":      ticker["last"],
            "change":     ticker.get("percentage", 0) or 0,
            "volume":     ticker.get("quoteVolume", 0) or 0,
            "high24":     high24,
            "low24":      low24,
            "ma7":        ma7,
            "ma24":       ma24,
            "rsi":        rsi,
            "fib":        fib_levels,
            "bid_wall":   bid_wall,
            "ask_wall":   ask_wall,
            "avg_volume": sum(volumes) / len(volumes),
            "closes":     closes,
        }
    finally:
        await exchange.close()

# ══════════════════════════════════════════
#  GEMINI — ГЕНЕРАЦИЯ ОТВЕТА
# ══════════════════════════════════════════
async def ask_gemini(persona_key: str, user_message: str, market_ctx: str = "") -> str:
    persona = PERSONAS[persona_key]
    model   = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=persona["system"],
    )
    prompt = user_message
    if market_ctx:
        prompt = f"Данные рынка BTC/USDT:\n{market_ctx}\n\nВопрос/задача: {user_message}"
    try:
        response = await asyncio.to_thread(model.generate_content, prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Gemini недоступен: {e}"

def format_market_ctx(data: dict) -> str:
    return (
        f"Цена: ${data['price']:,.2f} ({data['change']:+.2f}%)\n"
        f"Макс/Мин 24ч: ${data['high24']:,.0f} / ${data['low24']:,.0f}\n"
        f"MA7: ${data['ma7']:,.0f} | MA24: ${data['ma24']:,.0f}\n"
        f"RSI(24): {data['rsi']:.1f}\n"
        f"Объём 24ч: ${data['volume']/1e6:.1f}M\n"
        f"Фибоначчи: 0.382=${data['fib']['0.382']} | 0.618=${data['fib']['0.618']}\n"
        f"Bid-стена: ${data['bid_wall'][0]:,.0f} объём {data['bid_wall'][1]:.2f} BTC\n"
        f"Ask-стена: ${data['ask_wall'][0]:,.0f} объём {data['ask_wall'][1]:.2f} BTC"
    )

# ══════════════════════════════════════════
#  ОПРЕДЕЛЕНИЕ ИМЕНИ АГЕНТА В ТЕКСТЕ
# ══════════════════════════════════════════
def detect_agent(text: str) -> str | None:
    lower = text.lower()
    for key, p in PERSONAS.items():
        for alias in p["aliases"]:
            if alias in lower:
                return key
    return None

# ══════════════════════════════════════════
#  РЕЖИМ «КОНСИЛИУМ» (/work)
# ══════════════════════════════════════════
CONSILIUM_PLAN = [
    ("adrian",   "Дай краткий анализ новостного и макроэкономического фона для BTC прямо сейчас."),
    ("vika",     "Проанализируй тренд, RSI и объёмы. Дай вывод — покупать или ждать?"),
    ("demian",   "Проанализируй стакан (bid/ask стены). Куда давление? Есть ли крупные заявки?"),
    ("izabella", "Разбери уровни Фибоначчи и ключевые паттерны. Где поддержка и сопротивление?"),
    ("leon",     "Рассчитай риски для входа с плечом x10. Где стоп-лосс? Сколько % депозита в риск?"),
    ("rustam",   "Подтверди техническую готовность ордера. API работает? Параметры входа?"),
    ("gena",     "Выслушал команду. Дай финальное решение: ВХОДИМ или ЖДЁМ? Почему?"),
]

async def run_consilium(chat_id: int):
    try:
        data = await fetch_market_data()
        ctx  = format_market_ctx(data)
    except Exception as e:
        await bots["gena"].send_message(
            chat_id,
            f"⚠️ <b>Ошибка получения данных с Bitget:</b> {e}",
            parse_mode=ParseMode.HTML
        )
        return

    # Стартовое сообщение от Геннадия
    await bots["gena"].send_message(
        chat_id,
        f"🔔 <b>КОНСИЛИУМ НАЧАТ</b>\n\n"
        f"📊 BTC/USDT: <b>${data['price']:,.2f}</b> ({data['change']:+.2f}%)\n"
        f"Команда, докладывайте по очереди. Жду!",
        parse_mode=ParseMode.HTML
    )
    await asyncio.sleep(2)

    for agent_key, task in CONSILIUM_PLAN:
        answer = await ask_gemini(agent_key, task, ctx)
        display = PERSONAS[agent_key]["display"]
        await bots[agent_key].send_message(
            chat_id,
            f"<b>{display}</b>\n\n{answer}",
            parse_mode=ParseMode.HTML
        )
        await asyncio.sleep(random.uniform(3, 5))

# ══════════════════════════════════════════
#  РЕГИСТРАЦИЯ ХЕНДЛЕРОВ
# ══════════════════════════════════════════
def register_handlers(key: str, dp: Dispatcher):
    bot = bots[key]

    def allowed(message: types.Message) -> bool:
        # Отвечает всем участникам группы
        return message.chat.id == CHAT_ID

    def owner_only(message: types.Message) -> bool:
        return (
            message.chat.id == CHAT_ID and
            message.from_user.id == OWNER_ID
        )

    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        if not allowed(message):
            return
        display = PERSONAS[key]["display"]
        await message.reply(
            f"👋 <b>{display}</b> в сети!\n\n"
            f"Называй моё имя в сообщении — отвечу.\n"
            f"Команда <b>/work</b> — запуск консилиума (только для Шефа).",
            parse_mode=ParseMode.HTML
        )

    @dp.message(Command("work"))
    async def cmd_work(message: types.Message):
        if not owner_only(message):
            await message.reply("🚫 Только Шеф может запускать консилиум.")
            return
        await message.reply("⚡️ Запускаю консилиум...", parse_mode=ParseMode.HTML)
        asyncio.create_task(run_consilium(message.chat.id))

    @dp.message(F.text)
    async def handle_mention(message: types.Message):
        if not allowed(message):
            return
        if message.text is None:
            return

        mentioned = detect_agent(message.text)
        if mentioned != key:
            return  # Не мой бот

        display = PERSONAS[key]["display"]
        # Получаем рыночный контекст если вопрос про рынок
        market_keywords = ["курс", "цена", "рынок", "btc", "анализ", "тренд",
                           "риск", "стоп", "вход", "сделка", "покупать", "продавать"]
        need_market = any(w in message.text.lower() for w in market_keywords)

        ctx = ""
        if need_market:
            try:
                data = await fetch_market_data()
                ctx  = format_market_ctx(data)
            except Exception as e:
                ctx = f"(Данные Bitget недоступны: {e})"

        # Убираем имя бота из запроса
        clean_text = message.text
        for alias in PERSONAS[key]["aliases"]:
            clean_text = clean_text.lower().replace(alias, "").strip(" ,!")

        answer = await ask_gemini(key, clean_text or message.text, ctx)

        await message.reply(
            f"<b>{display}</b>\n\n{answer}",
            parse_mode=ParseMode.HTML
        )

# ══════════════════════════════════════════
#  ЗАПУСК
# ══════════════════════════════════════════
async def main():
    for key, dp in dispatchers.items():
        register_handlers(key, dp)

    tasks = [
        dp.start_polling(bots[key], handle_signals=False)
        for key, dp in dispatchers.items()
    ]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
