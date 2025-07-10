from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import logging
import os
import random
import json
import aiohttp
from keep_alive import keep_alive

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Получение токена из переменной окружения
API_TOKEN = os.getenv('API_TOKEN')
CHANNEL_USERNAME = '@drivingtraf'  # Замените на '@grindingtraffic', если канал другой

# Чтение ключевых слов из JSON-файла
def load_keywords():
    try:
        with open('keywords.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Ошибка загрузки keywords.json: {e}")
        return {}

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

async def check_subscription(user_id: int) -> bool:
    """Проверка, что пользователь подписан на канал."""
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        logging.info(f"User {user_id} status in {CHANNEL_USERNAME}: {member.status}")
        return member.status in ('creator', 'administrator', 'member')
    except Exception as e:
        logging.warning(f"Ошибка при проверке подписки для user_id={user_id}: {e}")
        return False

@dp.message(Command(commands=['start', 'help']))
async def start_command(message: types.Message):
    """Обработчик команд /start и /help."""
    text = (
        "Привет! 👋\n\n"
        "Я бот, который помогает получить полезные материалы по ключевым словам.\n"
        "Напиши ключевое слово из видео на нашем YouTube-канале.\n"
        f"Если ты не подписан на канал {CHANNEL_USERNAME}, я попрошу тебя подписаться.\n"
        "Например, попробуй слово: девушка или промокод."
    )
    await message.answer(text)

@dp.message()
async def keyword_handler(message: types.Message):
    """Обработчик текстовых сообщений с ключевыми словами."""
    if not message.text or message.text.startswith('/'):
        return

    keyword = message.text.lower().strip()
    keywords = load_keywords()
    if keyword in keywords:
        is_subscribed = await check_subscription(message.from_user.id)
        if is_subscribed:
            data = keywords[keyword]
            path = data['path']
            caption = data['caption']
            
            # Проверка, является ли path URL
            if path and (path.startswith('http://') or path.startswith('https://')):
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.head(path) as resp:
                            content_type = resp.headers.get('Content-Type', '')
                    # Проверяем, что это изображение
                    if 'image' in content_type.lower():
                        await message.answer_photo(photo=path, caption=caption)
                    else:
                        await message.answer_document(document=path, caption=caption)
                except Exception as e:
                    logging.error(f"Ошибка отправки по URL {path}: {e}")
                    await message.answer(f"Ошибка отправки файла. {caption}")
            elif path and os.path.exists(path):
                # Локальный файл
                try:
                    with open(path, 'rb') as file:
                        await message.answer_document(file, caption=caption)
                except Exception as e:
                    logging.error(f"Ошибка отправки файла {path}: {e}")
                    await message.answer(f"Ошибка при отправке файла. {caption}")
            else:
                # Только текст
                await message.answer(caption)
        else:
            await message.answer(
                f"Похоже, вы не подписаны на канал {CHANNEL_USERNAME}.\n"
                f"Пожалуйста, подпишитесь, чтобы получить доступ к базе:\n"
                f"https://t.me/{CHANNEL_USERNAME[1:]}"
            )
    else:
        unknown_responses = [
            "Извините, я не знаю такого ключевого слова 😔",
            "Попробуйте написать другое слово из видео.",
            "Такого слова у меня нет. Напишите /help для подсказки.",
            "Не понимаю, попробуйте ещё раз или /help."
        ]
        await message.answer(random.choice(unknown_responses))

if __name__ == '__main__':
    keep_alive()
    dp.run_polling(bot)
