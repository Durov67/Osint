import asyncio
import subprocess
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor

TOKEN = "8614846313:AAHQrA5YpzPfljz4OwGCrf22T_Ui8NTm-7Q"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

menu = ReplyKeyboardMarkup(resize_keyboard=True)
menu.add(
    KeyboardButton("🔎 Username search"),
    KeyboardButton("🌐 Domain info"),
)
menu.add(
    KeyboardButton("📊 Report"),
    KeyboardButton("ℹ Help")
)

user_results = {}

async def search_username(username):
    process = await asyncio.create_subprocess_exec(
        "maigret",
        username,
        "--no-progressbar",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()
    return stdout.decode()

def domain_lookup(domain):
    import requests

    url = f"https://api.hackertarget.com/whois/?q={domain}"

    try:
        r = requests.get(url, timeout=10)
        return r.text
    except:
        return "Error fetching domain info"

@dp.message_handler(commands=["start"])
async def start(message: types.Message):

    text = """
OSINT Bot

Commands:

🔎 Username search
🌐 Domain info
📊 Report
"""

    await message.answer(text, reply_markup=menu)

@dp.message_handler(lambda m: m.text == "ℹ Help")
async def help_command(message: types.Message):

    text = """
This bot searches public data:

• Username profiles
• Domain information

Use responsibly.
"""

    await message.answer(text)

@dp.message_handler(lambda m: m.text == "🔎 Username search")
async def username_request(message: types.Message):

    await message.answer("Send username")

@dp.message_handler(lambda m: m.text == "🌐 Domain info")
async def domain_request(message: types.Message):

    await message.answer("Send domain (example.com)")

@dp.message_handler(lambda m: m.text == "📊 Report")
async def report(message: types.Message):

    user_id = message.from_user.id

    if user_id not in user_results:
        await message.answer("No data yet")
        return

    await message.answer(user_results[user_id][:4000])

@dp.message_handler()
async def handle_text(message: types.Message):

    text = message.text.strip()

    if "." in text and " " not in text:

        await message.answer("Scanning domain...")

        result = domain_lookup(text)

        user_results[message.from_user.id] = result

        await message.answer(result[:4000])

    else:

        await message.answer("Searching username across sites...")

        result = await search_username(text)

        user_results[message.from_user.id] = result

        await message.answer(result[:4000])

if __name__ == "__main__":
    executor.start_polling(dp)