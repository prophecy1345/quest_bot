import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from database import is_user_paid, add_user, remove_user

# Настройки бота
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
ADMIN_CHAT_ID = os.getenv("CHAT_ID")
WELCOME_IMAGE_PATH = "welcome.jpg"

if TOKEN is None:
    raise ValueError("Ошибка: переменная окружения BOT_TOKEN не задана!")

# Логирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Состояния квеста и выбора языка
class QuestState(StatesGroup):
    language = State()  # Выбор языка
    question1 = State()
    question2 = State()
    question3 = State()
    question4 = State()
    question5 = State()
    question6 = State()
    question7 = State()
    question8 = State()
    question9 = State()
    question10 = State()

@dp.message(Command("id"))
async def send_user_id(message: types.Message):
    """Отправляет пользователю его Telegram ID без дополнительных сообщений."""
    user_id = message.from_user.id
    await message.answer(f"`{user_id}`", parse_mode="Markdown")

# Функция для получения клавиатуры выбора языка
def get_language_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")]
    ])

# Команда для смены языка
@dp.message(Command("language"))
async def change_language(message: types.Message, state: FSMContext):
    await message.answer("🌍 Выберите язык / Choose your language:", reply_markup=get_language_keyboard())
    await state.set_state(QuestState.language)

# Обработчик выбора языка
@dp.callback_query(F.data.startswith("lang_"))
async def process_language_selection(callback: types.CallbackQuery, state: FSMContext):
    language = callback.data.split("_")[1]
    await state.update_data(language=language)

    if language == "ru":
        text = "✅ Вы выбрали русский язык!\n\nТеперь можно начинать квест! 🚀"
    else:
        text = "✅ You have chosen English!\n\nNow you can start the quest! 🚀"

    await callback.message.answer(text)
    await send_welcome(callback.message, state)

# Приветственное сообщение
@dp.message(Command("start"))
async def send_welcome(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()

    # Если язык не выбран, предложить выбрать
    if "language" not in data:
        await message.answer("🌍 Выберите язык / Choose your language:", reply_markup=get_language_keyboard())
        await state.set_state(QuestState.language)
        return

    language = data["language"]

    # Проверяем оплату
    if not is_user_paid(user_id):
        text_ru = (
            "🔒 **Доступ к боту закрыт**\n\n"
            "Чтобы получить доступ, сделай следующее:\n\n"
            "1️⃣ Напиши мне ([Hristina](https://t.me/Hristina_Photo)) — расскажу, как оплатить доступ.\n"
            "2️⃣ Оплати доступ по инструкциям.\n"
            "3️⃣ Узнай свой Telegram ID — напиши /id в этом чате.\n"
            "4️⃣ Пришли мне свой ID ([Hristina](https://t.me/Hristina_Photo)).\n"
            "5️⃣ Я добавлю тебя в список — после этого бот будет доступен.\n"
            "6️⃣ Запусти бота — напиши /start\n\n"
            "❓ Если что-то не получается, напиши мне!"
        )

        text_en = (
            "🔒 **Access to the bot is restricted**\n\n"
            "To get access, follow these steps:\n\n"
            "1️⃣ Message me ([Hristina](https://t.me/Hristina_Photo)) — I'll explain how to pay.\n"
            "2️⃣ Complete the payment following the instructions.\n"
            "3️⃣ Find your Telegram ID — type /id in this chat.\n"
            "4️⃣ Send me your ID ([Hristina](https://t.me/Hristina_Photo)).\n"
            "5️⃣ I'll add you to the list — then the bot will be available.\n"
            "6️⃣ Start the bot — type /start\n\n"
            "❓ If you have any issues, message me!"
        )

        await message.answer(text_ru if language == "ru" else text_en, parse_mode="Markdown", disable_web_page_preview=True)
        return

    # Если доступ оплачен — начинаем квест
    photo = FSInputFile(WELCOME_IMAGE_PATH)

    welcome_text_ru = (
        "👋 **Добро пожаловать в Subotica Quest!**\n\n"
        "Этот квест сделает твою прогулку по Суботице увлекательнее.\n"
        "Прояви креативность и главное — наслаждайся процессом!\n\n"
        "Готов начать? Тогда вперед! 🚀"
    )

    welcome_text_en = (
        "👋 **Welcome to the Subotica Quest!**\n\n"
        "This quest will make your walk through Subotica more exciting.\n"
        "Be creative and, most importantly, enjoy the process!\n\n"
        "Ready to start? Let's go! 🚀"
    )

    await message.answer_photo(photo, caption=welcome_text_ru if language == "ru" else welcome_text_en)
    await ask_question1(message, state)

# Вопрос 1
async def ask_question1(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "ru")

    if language == "ru":
        text = (
            "🦇 **Задание 1**\n"
            "У вокзала, где улица дышит тишиной,\n"
            "Крылатая стража нашла угол свой.\n"
            "Найди её облик на каменной глади —\n"
            "А сколько ступенек ведут к её „зграде“?"
        )
    else:
        text = (
            "🦇 **Task 1**\n"
            "Near the station, where streets are so still,\n"
            "Winged guardians stand, as if time’s at a chill.\n"
            "Find their reflection on stone standing tall —\n"
            "And how many steps lead up to their hall?"
        )

    await message.answer(text)
    await state.update_data(attempts=0)
    await state.set_state(QuestState.question1)

@dp.message(QuestState.question1)
async def process_question1(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "ru")
    attempts = data.get("attempts", 0)

    correct_answer = "7"
    response_correct = "✅ Правильно! Двигаемся дальше!" if language == "ru" else "✅ Correct! Moving on!"
    response_wrong = "❌ Не совсем. Посчитай ещё раз!" if language == "ru" else "❌ Not quite. Count again!"

    if message.text.strip() == correct_answer:
        await message.answer(response_correct)
        await ask_question2(message, state)
    else:
        attempts += 1
        await state.update_data(attempts=attempts)
        if attempts < 3:
            await message.answer(f"{response_wrong} Осталось попыток: {3 - attempts}")
        else:
            correct_text = "Правильный ответ: 7. Двигаемся дальше!" if language == "ru" else "Correct answer: 7. Moving on!"
            await message.answer(f"❌ {correct_text}")
            await ask_question2(message, state)

# Вопрос 2 (фото)
async def ask_question2(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "ru")

    if language == "ru":
        text = (
            "🩷 **Задание 2**\n"
            "В фасадах и плитке, в кованых узорах\n"
            "Скрываются сердца в городских просторах.\n"
            "Найди их на зданиях — три отыщи,\n"
            "Выбери снимки и мне отошли!"
        )
    else:
        text = (
            "🩷 **Task 2**\n"
            "In facades and tiles, in ironwork’s grace,\n"
            "Hearts hide away in the city’s embrace.\n"
            "Find them on buildings—three is the key,\n"
            "Capture their images, then send them to me!"
        )

    await message.answer(text)
    await state.update_data(photo_count=0)
    await state.set_state(QuestState.question2)

@dp.message(QuestState.question2, F.photo)
async def process_question2(message: types.Message, state: FSMContext):
    data = await state.get_data()
    photo_count = data.get("photo_count", 0) + 1
    language = data.get("language", "ru")

    response_accept = f"📸 Фото {photo_count}/3 принято! Жду ещё {3 - photo_count}." if language == "ru" else f"📸 Photo {photo_count}/3 received! Waiting for {3 - photo_count} more."
    response_complete = "✅ Отличная коллекция! Следующее задание!" if language == "ru" else "✅ Great collection! Next task!"

    if photo_count > 3:
        await message.answer("⚠️ Достаточно 3 фото!" if language == "ru" else "⚠️ Three photos are enough!")
        return

    await state.update_data(photo_count=photo_count)
    await bot.forward_message(ADMIN_CHAT_ID, message.chat.id, message.message_id)

    if photo_count < 3:
        await message.answer(response_accept)
    else:
        await bot.send_message(ADMIN_CHAT_ID, f"📷 @{message.from_user.username} отправил 3 фото для задания 2")
        await message.answer(response_complete)
        await ask_question3(message, state)
        await state.update_data(photo_count=0)

@dp.message(QuestState.question2)
async def handle_text_in_question2(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "ru")
    await message.answer("❌ Это фото-задание! Пожалуйста, отправь 3 снимка." if language == "ru" else "❌ This is a photo task! Please send 3 pictures.")

# Вопрос 3 (текст)
async def ask_question3(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "ru")

    text = (
        "📖 **Задание 3**\n"
        "В книжный зайди, отыщи без труда\n"
        "Книгу, что в сердце твоём навсегда.\n"
        "Название новое вслух прочитай —\n"
        "Как на английском звучит, отвечай!"
    ) if language == "ru" else (
        "📖 **Task 3**\n"
        "Step into a bookstore, go take a glance,\n"
        "Find a dear book that has you entranced.\n"
        "Read out its title, fresh and anew —\n"
        "Now, tell me in Serbian, how does it sound to you?"
    )

    await message.answer(text)
    await state.set_state(QuestState.question3)

@dp.message(QuestState.question3)
async def process_question3(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "ru")
    response = "📚 Интересный выбор! Идем дальше!" if language == "ru" else "📚 Interesting choice! Let's continue!"

    await message.answer(response)
    await ask_question4(message, state)

# Вопрос 4 (фото двери)
async def ask_question4(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "ru")

    text = (
        "🚪 **Задание 4**\n"
        "Найди любую открытую дверь,\n"
        "Внутрь загляни, тишине лишь поверь.\n"
        "Лестницы стройной изгибы узри\n"
        "И фото двери мне скорее пришли!"
    ) if language == "ru" else (
        "🚪 **Task 4**\n"
        "Find any doorway that stands open wide,\n"
        "Peek in and trust in the silence inside.\n"
        "See how the staircase so gracefully bends,\n"
        "And send me a photo—I'll wait, my friend!"
    )

    await message.answer(text)
    await state.update_data(photo_count=0)
    await state.set_state(QuestState.question4)

@dp.message(QuestState.question4, F.photo)
async def process_question4(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "ru")

    response = "✅ Отличное фото! Следующее задание!" if language == "ru" else "✅ Great photo! Next task!"

    await state.update_data(photo_count=1)
    await bot.forward_message(ADMIN_CHAT_ID, message.chat.id, message.message_id)

    await bot.send_message(ADMIN_CHAT_ID, f"📷 @{message.from_user.username} отправил фото для задания 4")
    await message.answer(response)
    await ask_question5(message, state)

@dp.message(QuestState.question4)
async def handle_text_in_question4(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "ru")
    await message.answer("❌ Пожалуйста, пришли фото двери!" if language == "ru" else "❌ Please send a photo of the door!")

# Вопрос 5 (текст)
async def ask_question5(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "ru")

    text = (
        "🏛 **Задание 5**\n"
        "В центре Суботицы, где жизни быстрый ход,\n"
        "Миниатюра города тихо живёт.\n"
        "Вглядись, рассмотри, все детали узнай,\n"
        "Из чего он создан — скорей отгадай!"
    ) if language == "ru" else (
        "🏛 **Task 5**\n"
        "In the heart of Subotica, where life rushes by,\n"
        "A miniature city stands quiet and shy.\n"
        "Look closely, observe, every detail explore —\n"
        "Guess what it's made of, and tell me once more!"
    )

    await message.answer(text)
    await state.update_data(attempts=0)
    await state.set_state(QuestState.question5)

@dp.message(QuestState.question5)
async def process_question5(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "ru")

    correct_answer = "бронза" if language == "ru" else "bronze"
    response_correct = "✅ Ура! Это правильный ответ." if language == "ru" else "✅ Hooray! That's the correct answer!"
    response_wrong = "❌ Не совсем. Подумай ещё!" if language == "ru" else "❌ Not quite. Think again!"

    if message.text.strip().lower() == correct_answer:
        await message.answer(response_correct)
        await ask_question6(message, state)
    else:
        await message.answer(response_wrong)

# Вопрос 6 (фото)
async def ask_question6(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "ru")

    text = (
        "⛲️ **Задание 6**\n"
        "Два архитектора и 'magnum opus' рядом —\n"
        "Полны любовью, вдохновением их взгляды.\n"
        "Когда найдешь их - время не теряй\n"
        "Используй камеру и фото отправляй!"
    ) if language == "ru" else (
        "⛲️ **Task 6**\n"
        "Two architects stand with their magnum opus near,\n"
        "Their eyes full of love and inspiration sincere.\n"
        "Once you have found them, don’t waste any time —\n"
        "Capture the moment and send me the sign!"
    )

    await message.answer(text)
    await state.update_data(photo_count=0)
    await state.set_state(QuestState.question6)

@dp.message(QuestState.question6, F.photo)
async def process_question6(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "ru")

    response = "✅ Отлично! Теперь следующее задание!" if language == "ru" else "✅ Great! Now, the next task!"

    await bot.forward_message(ADMIN_CHAT_ID, message.chat.id, message.message_id)
    await bot.send_message(ADMIN_CHAT_ID, f"📷 @{message.from_user.username} отправил фото для задания 6")

    await message.answer(response)
    await ask_question7(message, state)

@dp.message(QuestState.question6)
async def handle_text_in_question6(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "ru")
    await message.answer("❌ Пожалуйста, отправь фото архитекторов!" if language == "ru" else "❌ Please send a photo of the architects!")

# Вопрос 7 (текст)
async def ask_question7(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "ru")

    text = (
        "🧘‍♂️ **Задание 7**\n"
        "Метание духа оставь позади,\n"
        "Единство суеты и тишины в груди.\n"
        "Расслабься, где кофе, уют и покой,\n"
        "А радость была ведь всегда под рукой.\n"
        "Когда все поймешь - ответ ты найдешь!"
    ) if language == "ru" else (
        "🧘‍♂️ **Task 7**\n"
        "Mindful, let go of the chaos inside,\n"
        "Embrace both the rush and the calm side by side.\n"
        "Relax where the coffee brings warmth to your soul,\n"
        "And joy was right there, always whole.\n"
        "Know it at last—your answer is cast!"
    )

    await message.answer(text)
    await state.update_data(attempts=0)
    await state.set_state(QuestState.question7)

@dp.message(QuestState.question7)
async def process_question7(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "ru")

    correct_answer = "мерак" if language == "ru" else "merak"
    response_correct = "✅ Верно! Надеюсь, ты смог насладиться моментом!" if language == "ru" else "✅ Correct! I hope you enjoyed the moment!"
    response_wrong = "❌ Подумай ещё! Это связано с приятными моментами." if language == "ru" else "❌ Think again! It's connected to pleasant moments."

    if message.text.strip().lower() == correct_answer:
        await message.answer(response_correct)
        await ask_question8(message, state)
    else:
        await message.answer(response_wrong)

# Вопрос 8 (текст)
async def ask_question8(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "ru")

    text = (
        "📍 **Задание 8**\n"
        "Там, где камень лежит вековой под ногой,\n"
        "Начинает улицу магазин обувной.\n"
        "Мощёная, древняя, манит пройтись\n"
        "Названье пиши и на ней окажись."
    ) if language == "ru" else (
        "📍 **Task 8**\n"
        "Where ancient stone lies beneath your feet,\n"
        "A shoe shop stands where the street does meet.\n"
        "Cobblestones whisper, inviting your pace —\n"
        "Write down its name and go find the place!"
    )

    await message.answer(text)
    await state.update_data(attempts=0)
    await state.set_state(QuestState.question8)

@dp.message(QuestState.question8)
async def process_question8(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "ru")

    correct_answer = "петра драпшина" if language == "ru" else "petra drapšina"
    response_correct = "✅ Правильно! Приятной прогулки!" if language == "ru" else "✅ Correct! Enjoy your walk!"
    response_wrong = "❌ Подумай ещё! Это узкая, мощёная улица в центре." if language == "ru" else "❌ Think again! It's a narrow, cobbled street in the center."

    if message.text.strip().lower() == correct_answer:
        await message.answer(response_correct)
        await ask_question9(message, state)
    else:
        await message.answer(response_wrong)

# Вопрос 9 (текст)
async def ask_question9(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "ru")

    text = (
        "🥞 **Задание 9**\n"
        "В Суботице, где вкусно и тепло,\n"
        "Лепешка жарится, пахнет — просто волшебство.\n"
        "Венгерская, с хрустящей корочкой, она,\n"
        "Назови её имя — и загадка решена."
    ) if language == "ru" else (
        "🥞 **Task 9**\n"
        "In Subotica, where it’s warm and bright,\n"
        "A flatbread sizzles—oh, what a delight!\n"
        "Hungarian, crispy, golden to see,\n"
        "Say its name, and the riddle’s set free!"
    )

    await message.answer(text)
    await state.update_data(attempts=0)
    await state.set_state(QuestState.question9)

@dp.message(QuestState.question9)
async def process_question9(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "ru")

    correct_answer = "лангош" if language == "ru" else "langos"
    response_correct = "✅ Верно! Надеюсь, ты попробуешь его!" if language == "ru" else "✅ Correct! Hope you try it!"
    response_wrong = "❌ Подумай ещё! Это популярная венгерская уличная еда." if language == "ru" else "❌ Think again! It's a popular Hungarian street food."

    if message.text.strip().lower() == correct_answer:
        await message.answer(response_correct)
        await ask_question10(message, state)
    else:
        await message.answer(response_wrong)

# Вопрос 10 (фото)
async def ask_question10(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "ru")

    text = (
        "📸 **Задание 10**\n"
        "Сними тот миг, что в сердце отзовётся,\n"
        "Где город нежно дарит свой привет.\n"
        "Пусть в кадре атмосфера остаётся,\n"
        "Такой, какой запомнишь ты навек."
    ) if language == "ru" else (
        "📸 **Task 10**\n"
        "Capture the moment that touches your heart,\n"
        "Where the city greets you with warmth from the start.\n"
        "Let the atmosphere stay in your frame,\n"
        "Just as you’ll cherish it, always the same."
    )

    await message.answer(text)
    await state.set_state(QuestState.question10)

@dp.message(QuestState.question10, F.photo)
async def process_question10(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "ru")

    completion_text = (
        "✅ Замечательный снимок Суботицы!\n\n"
        "✨ Буду рада, если ты подпишешься на меня в Instagram: [@hristy_life](https://www.instagram.com/hristy_life)\n"
        "📸 Если захочешь, поделись этим фото в сторис и отметь меня — с удовольствием сделаю репост!\n\n"
        "🎁 А если отметишь меня в сторис, жди маленький сюрприз! 😉\n\n"
        "💖 Спасибо за участие в квесте! Надеюсь, тебе понравилось. До новых встреч!"
    ) if language == "ru" else (
        "✅ A wonderful photo of Subotica!\n\n"
        "✨ I'd be happy if you follow me on Instagram: [@hristy_life](https://www.instagram.com/hristy_life)\n"
        "📸 If you want, share this photo in your story and tag me — I'll gladly repost it!\n\n"
        "🎁 And if you tag me in your story, expect a little surprise! 😉\n\n"
        "💖 Thank you for participating in the quest! Hope you enjoyed it. See you next time!"
    )

    # Отправляем фото админу
    await bot.forward_message(ADMIN_CHAT_ID, message.chat.id, message.message_id)
    await bot.send_message(ADMIN_CHAT_ID, f"📷 @{message.from_user.username} завершил квест и отправил фото для задания 10")

    await message.answer(completion_text, parse_mode="Markdown")
    await state.clear()  # Очищаем состояние, так как квест завершён

@dp.message(QuestState.question10)
async def handle_text_in_question10(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "ru")
    await message.answer(
        "❌ Это фото-задание! Пожалуйста, отправь снимок." if language == "ru" else
        "❌ This is a photo task! Please send a picture."
    )

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())