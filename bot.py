from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, ContentType
import logging
import os
import random
from keep_alive import keep_alive

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Получение токена из переменной окружения
API_TOKEN = os.getenv('API_TOKEN')
CHANNEL_USERNAME = '@drivingtraf'

# Словарь ключевых слов
KEYWORDS = {
    'девушка': {'path': 'mainphoto.webp', 'caption': 'Вот твой файл!'},
    'traffic2025': {
        'path': None,
        'caption': 'Спасибо за промокод, держи "Чек-лист для проверки seo-кейсов"!\nhttps://docs.google.com/spreadsheets/d/15OGc_BBkT-H_f-3Iy4Zccvj2j2rLXgm9hiiGX45CU0A/edit?usp=sharing'
    }
}

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

async def check_subscription(user_id: int) -> bool:
    """Проверка, что пользователь подписан на канал."""
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ('creator', 'administrator', 'member')
    except Exception as e:
        logging.warning(f"Ошибка при проверке подписки: {e}")
        return False

@dp.message(Command(commands=['start', 'help']))
async def start_command(message: types.Message):
    """Обработчик команд /start и /help."""
    text = (
        "Привет! 👋\n\n"
        "Я бот, который помогает получить полезные материалы по ключевым словам.\n"
        "Напиши ключевое слово из видео на нашем YouTube-канале.\n"
        "Если ты не подписан на канал @drivingtraf, я попрошу тебя подписаться.\n"
        "Например, попробуй слово: девушка или промокод."
    )
    await message.answer(text)

@dp.message(ContentType('text'))
async def keyword_handler(message: types.Message):
    """Обработчик текстовых сообщений с ключевыми словами."""
    if message.text.startswith('/'):
        return

    keyword = message.text.lower().strip()
    if keyword in KEYWORDS:
        is_subscribed = await check_subscription(message.from_user.id)
        if is_subscribed:
            data = KEYWORDS[keyword]
            if data['path'] and os.path.exists(data['path']):
                try:
                    with open(data['path'], 'rb') as file:
                        await message.answer_document(file, caption=data['caption'])
                except Exception as e:
                    logging.error(f"Ошибка отправки файла: {e}")
                    await message.answer("Ошибка при отправке файла. Попробуйте позже.")
            else:
                await message.answer(data['caption'])
        else:
            await message.answer(
                "Похоже, вы не подписаны на канал @drivingtraf.\n"
                "Пожалуйста, подпишитесь, чтобы получить доступ к базе:\n"
                "https://t.me/drivingtraf"
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
