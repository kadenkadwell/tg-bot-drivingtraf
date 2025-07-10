from aiogram import Bot, Dispatcher, types
from aiogram.utils.executor import start_polling
import logging
import os
import random
from keep_alive import keep_alive

API_TOKEN = '8163482962:AAFpdGrhJdGqTcklXAl93zSglXmK26hDTOg'
CHANNEL_USERNAME = '@drivingtraf'

KEYWORDS = {
    'девушка': {'path': 'mainphoto.webp', 'caption': 'Вот твой файл!'},
    'traffic2025': {
        'path': None,
        'caption': 'Спасибо за промокод, держи "Чек-лист для проверки seo-кейсов"!\nhttps://docs.google.com/spreadsheets/d/15OGc_BBkT-H_f-3Iy4Zccvj2j2rLXgm9hiiGX45CU0A/edit?usp=sharing'
    }
}

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

async def check_subscription(user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ['creator', 'administrator', 'member']
    except Exception as e:
        logging.warning(f"Ошибка проверки подписки: {e}")
        return False

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    text = (
        "Привет! 👋\n\n"
        "Я бот, который помогает получить полезные материалы по ключевым словам.\n"
        "Напиши ключевое слово из видео на нашем YouTube-канале.\n"
        "Если ты не подписан на канал @drivingtraf, я попрошу тебя подписаться.\n"
        "Например, попробуй написать слово: девушка или промокод."
    )
    await message.answer(text)

@dp.message_handler(content_types=types.ContentType.TEXT)
async def keyword_handler(message: types.Message):
    if message.text.startswith('/'):
        return

    keyword = message.text.lower().strip()
    if keyword in KEYWORDS:
        is_subscribed = await check_subscription(message.from_user.id)
        if is_subscribed:
            data = KEYWORDS[keyword]
            if data['path'] and os.path.exists(data['path']):
                try:
                    await message.answer_document(open(data['path'], 'rb'), caption=data['caption'])
                except Exception as e:
                    logging.error(f"Ошибка отправки файла: {e}")
                    await message.answer("Извините, возникла ошибка при отправке файла. Попробуйте позже.")
            else:
                # Для промокода или если файла нет, просто отправляем текст
                await message.answer(data['caption'])
        else:
            await message.answer(
                "Похоже, вы не подписаны на канал @drivingtraf.\n"
                "Пожалуйста, подпишитесь, чтобы получить доступ к файлам:\n"
                "https://t.me/drivingtraf"
            )
    else:
        unknown_responses = [
            "Извините, я не знаю такого ключевого слова 😕",
            "Попробуйте написать ключевое слово из видео на нашем YouTube.",
            "Хмм... такого ключевого слова у меня нет. Напишите /help для подсказки.",
            "Не могу понять, что вы имели в виду. Попробуйте /help."
        ]
        await message.answer(random.choice(unknown_responses))

if __name__ == '__main__':
    keep_alive()
    start_polling(dp, skip_updates=True)
