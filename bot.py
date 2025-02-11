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

# Состояния квеста
class QuestState(StatesGroup):
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

# Приветственное сообщение с фото
@dp.message(Command("start"))
async def send_welcome(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    if not is_user_paid(user_id):
        await message.answer(
            "Привет!\n\n"
            "Чтобы получить доступ к боту, сделай следующее:\n\n"
            "1️⃣ Напиши мне (@Hristina_Photo) — расскажу, как оплатить доступ.\n"
            "2️⃣ Оплати доступ по инструкциям.\n"
            "3️⃣ Узнай свой Telegram ID — напиши /id в @QuestForSubotica_bot.\n"
            "4️⃣ Пришли мне свой ID (@Hristina_Photo).\n"
            "5️⃣ Я добавлю тебя в список — после этого бот будет доступен.\n"
            "6️⃣ Запусти бота — напиши /start в @QuestForSubotica_bot.\n\n"

            "Если что-то не получается, пиши мне!"
        )
        return

    photo = FSInputFile(WELCOME_IMAGE_PATH)
    await message.answer_photo(photo, caption=
        "👋 Добро пожаловать в Subotica Quest!\n\n"
        "Этот квест сделает твою прогулку по Суботице увлекательнее."
        "Прояви креативность и главное — наслаждайся процессом!\n\n"
        "Готов начать? Тогда вперед! 🚀"
    )
    await ask_question1(message, state)


@dp.message(Command("id"))
async def send_user_id(message: types.Message):
    """Отправляет пользователю его Telegram ID"""
    user_id = message.from_user.id
    await message.answer(f"📌 Ваш Telegram ID: `{user_id}`", parse_mode="Markdown")


@dp.message(Command("add"))
async def add_user_command(message: types.Message):
    """Добавление пользователя в список оплативших (только для админа)"""
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ У вас нет прав на добавление пользователей.")
        return

    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ Введите ID пользователя после /add")
        return

    try:
        user_id = int(args[1])
        add_user(user_id)
        await message.answer(f"✅ Пользователь {user_id} добавлен в список оплативших.")
    except ValueError:
        await message.answer("❌ ID должен быть числом.")

@dp.message(Command("remove"))
async def remove_user_command(message: types.Message):
    """Удаление пользователя из списка оплативших (только для админа)"""
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ У вас нет прав на удаление пользователей.")
        return

    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ Введите ID пользователя после /remove")
        return

    try:
        user_id = int(args[1])
        remove_user(user_id)
        await message.answer(f"✅ Пользователь {user_id} удалён из списка оплативших.")
    except ValueError:
        await message.answer("❌ ID должен быть числом.")
# Функция для создания клавиатуры викторины
def get_quiz_keyboard(options):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=opt, callback_data=opt)] for opt in options
    ])


# Вопрос 1 (логика исправлена, чтобы правильно учитывать попытки)
async def ask_question1(message: types.Message, state: FSMContext):
    await message.answer(
        "🦇 Задание 1\n"
        "У вокзала, где улица дышит тишиной,\n"
        "Крылатая стража нашла угол свой.\n"
        "Найди её облик на каменной глади —\n"
        "А сколько ступенек ведут к её „зграде“?"
    )
    await state.update_data(attempts=0)
    await state.set_state(QuestState.question1)

@dp.message(QuestState.question1)
async def process_question1(message: types.Message, state: FSMContext):
    if message.photo:
        await message.answer("❌ Это не фото-задание! Пожалуйста, напиши ответ.")
        return

    data = await state.get_data()
    attempts = data.get("attempts", 0)

    if message.text.strip() == "7":
        await message.answer("✅ Правильно! Двигаемся дальше!")
        await ask_question2(message, state)
    else:
        attempts += 1
        await state.update_data(attempts=attempts)
        if attempts < 3:
            await message.answer(f"❌ Не совсем. Посчитай ещё раз! Осталось попыток: {3 - attempts}")
        else:
            await message.answer("❌ К сожалению, неверно! Правильный ответ: 7. Двигаемся дальше!")
            await ask_question2(message, state)

# Вопрос 2 (фото)
async def ask_question2(message: types.Message, state: FSMContext):
    await message.answer("🩷  Задание 2\n"
        "В фасадах и плитке, в кованых узорах\n"
        "Скрываются сердца в городских просторах.\n"
        "Найди их на зданиях — три отыщи,\n"
        "Выбери снимки и мне отошли!")
    await state.set_state(QuestState.question2)
    await state.update_data(photo_count=0)

@dp.message(QuestState.question2, F.photo)
async def process_question2(message: types.Message, state: FSMContext):
    data = await state.get_data()
    photo_count = data.get("photo_count", 0) + 1

    if photo_count > 3:
        await message.answer("⚠️ Достаточно 3 фото! Но мне приятно видеть, как ты стараешься.")
        return

    await state.update_data(photo_count=photo_count)
    await bot.forward_message(ADMIN_CHAT_ID, message.chat.id, message.message_id)

    if photo_count < 3:
        await message.answer(f"📸 Фото {photo_count}/3 принято! Жду ещё {3 - photo_count}.")
    else:
        await bot.send_message(ADMIN_CHAT_ID, f"📷 Пользователь @{message.from_user.username} отправил 3 фото для задания 2")
        await message.answer("✅ Отличная коллекция вышла! 🩷 Следующее задание!")
        await ask_question3(message, state)
        await state.update_data(photo_count=0)

@dp.message(QuestState.question2)
async def handle_text_in_question2(message: types.Message):
    await message.answer("❌ Ты удивишься, как часто в архитектуре встречаются сердечки! Пришли три разные фотографии")

# Вопрос 3 (текстовый ответ)
async def ask_question3(message: types.Message, state: FSMContext):
    await message.answer(
        "📖 Задание 3\n"
        "В книжный зайди, отыщи без труда\n"
        "Книгу, что в сердце твоём навсегда.\n"
        "Название новое вслух прочитай —\n"
        "Как на сербском звучит, отвечай!"
    )
    await state.set_state(QuestState.question3)

@dp.message(QuestState.question3)
async def process_question3(message: types.Message, state: FSMContext):
    await message.answer("📚 Интересный выбор любимой книги! Идем дальше?")
    await ask_question4(message, state)

# Вопрос 4 (фото двери)
async def ask_question4(message: types.Message, state: FSMContext):
    await message.answer(
        "🚪 Задание 4\n"
        "Найди любую открытую дверь,\n"
        "Внутрь загляни, тишине лишь поверь.\n"
        "Лестницы стройной изгибы узри\n"
        "И фото двери мне скорее пришли!"
    )
    await state.update_data(photo_count=0)
    await state.set_state(QuestState.question4)

@dp.message(QuestState.question4, F.photo)
async def process_question4(message: types.Message, state: FSMContext):
    data = await state.get_data()
    photo_count = data.get("photo_count", 0) + 1

    if photo_count > 1:
        await message.answer("⚠️ Одного фото мне хватит, спасибо!")
        return

    await state.update_data(photo_count=photo_count)
    await bot.forward_message(ADMIN_CHAT_ID, message.chat.id, message.message_id)

    await bot.send_message(ADMIN_CHAT_ID, f"📷 Пользователь @{message.from_user.username} отправил фото для задания 4")
    await message.answer("✅ Отличное фото вышло! Следующее задание!")
    await ask_question5(message, state)
    await state.update_data(photo_count=1)

@dp.message(QuestState.question4)
async def handle_text_in_question4(message: types.Message):
    await message.answer("❌ Мне бы хотелось увидеть твою фотографию двери! Какую удалось найти?")

# Вопрос 5 (логика исправлена, чтобы правильно учитывать попытки)
async def ask_question5(message: types.Message, state: FSMContext):
    await message.answer(
        "🏛 **Задание 5**\n"
        "В центре Суботицы, где жизни быстрый ход,\n"
        "Миниатюра города тихо живёт.\n"
        "Вглядись, рассмотри, все детали узнай,\n"
        "Из чего он создан — скорей отгадай!"
    )
    await state.update_data(attempts=0)
    await state.set_state(QuestState.question5)

@dp.message(QuestState.question5)
async def process_question5(message: types.Message, state: FSMContext):
    if message.photo:
        await message.answer("❌ Это не фото-задание! Пожалуйста, напиши свой ответ.")
        return

    data = await state.get_data()
    attempts = data.get("attempts", 0)

    if message.text.strip().lower() == "бронза":
        await message.answer("✅ Ура! Это правильный ответ. Двигаемся дальше!")
        await ask_question6(message, state)
    else:
        attempts += 1
        await state.update_data(attempts=attempts)
        if attempts < 3:
            await message.answer(f"❌ Не совсем. Подумай ещё! Осталось попыток: {3 - attempts}")
        else:
            await message.answer("❌ Неверно! Правильный ответ: Бронза. В следующий раз повезёт!")
            await ask_question6(message, state)

        # Вопрос 6 (прием фото, строго 1 фото)
async def ask_question6(message: types.Message, state: FSMContext):
    await message.answer(
        "⛲️ Задание 6\n"
        "Два архитектора и 'magnum opus' рядом —\n"
        "Полны любовью, вдохновением их взгляды.\n"
        "Когда найдешь их - время не теряй\n"
        "Используй камеру и фото отправляй!"
    )
    await state.update_data(photo_count=0)
    await state.set_state(QuestState.question6)

@dp.message(QuestState.question6, F.photo)
async def process_question6(message: types.Message, state: FSMContext):
    data = await state.get_data()
    photo_count = data.get("photo_count", 0) + 1

    if photo_count > 1:
        await message.answer("⚠️ Одной фотографии достаточно.")
        return

    await state.update_data(photo_count=photo_count)
    await bot.forward_message(ADMIN_CHAT_ID, message.chat.id, message.message_id)

    await bot.send_message(ADMIN_CHAT_ID, f"📷 Пользователь @{message.from_user.username} отправил фото для задания 6")
    await message.answer("✅ Молодец! В следующем задании тебя ждет приятная миссия!")
    await ask_question7(message, state)
    await state.update_data(photo_count=1)

@dp.message(QuestState.question6)
async def handle_text_in_question6(message: types.Message):
    await message.answer("❌ Я бы хотела увидеть фотографию архитекторов! Пожалуйста, отправь один снимок.")

# Вопрос 7 (логика исправлена, чтобы правильно учитывать попытки)
async def ask_question7(message: types.Message, state: FSMContext):
    await message.answer(
        "🧘‍♂️ Задание 7\n"
        "Метание духа оставь позади\n"
        "Единство суеты и тишины в груди\n"
        "Расслабься, где кофе, уют и покой\n"
        "А радость была ведь всегда под рукой\n"
        "Когда все поймешь - ответ ты найдешь!"
    )
    await state.update_data(attempts=0)
    await state.set_state(QuestState.question7)

@dp.message(QuestState.question7)
async def process_question7(message: types.Message, state: FSMContext):
    if message.photo:
        await message.answer("❌ Это не фото-задание! Ощути момент и пришли ответ.")
        return

    data = await state.get_data()
    attempts = data.get("attempts", 0)

    if message.text.strip().lower() == "мерак":
        await message.answer("✅ Именно так! Надеюсь тебе удалось насладиться моментом и отдохнуть!")
        await ask_question8(message, state)
    else:
        attempts += 1
        await state.update_data(attempts=attempts)
        if attempts < 3:
            await message.answer(f"❌ Ты точно пьешь напиток и ощущаешь это состояние? Попробуйте ещё раз посмотреть внимательнее на задание! Осталось попыток: {3 - attempts}")
        else:
            await message.answer("❌ Мне жаль! Правильный ответ: Мерак. Отгадка крылась в первых буквах. Постарайся дальше быть внимательнее!")
            await ask_question8(message, state)

# Вопрос 8 (логика исправлена, чтобы правильно учитывать попытки)
async def ask_question8(message: types.Message, state: FSMContext):
    await message.answer(
        "📍 Задание 8\n"
        "Там, где камень лежит вековой под ногой,\n"
        "Начинает улицу магазин обувной.\n"
        "Мощёная, древняя, манит пройтись\n"
        "Названье пиши и на ней окажись."
    )
    await state.update_data(attempts=0)
    await state.set_state(QuestState.question8)

@dp.message(QuestState.question8)
async def process_question8(message: types.Message, state: FSMContext):
    if message.photo:
        await message.answer("❌ Это не фото-задание! Угадай название улицы.")
        return

    data = await state.get_data()
    attempts = data.get("attempts", 0)

    if message.text.strip().lower() == "петра драпшина":
        await message.answer("✅ Совершенно верно! Понравилась улочка?")
        await ask_question9(message, state)
    else:
        attempts += 1
        await state.update_data(attempts=attempts)
        if attempts < 3:
            await message.answer(f"❌ Не правильно.  Найди мощёную улицу рядом с круговым перекрестком! Осталось попыток: {3 - attempts}")
        else:
            await message.answer("❌ Неверно! Правильный ответ: Петра Драпшина. Советую найти эту улочку и прогуляться по ней!")
            await ask_question9(message, state)

# Вопрос 9 (логика исправлена, чтобы правильно учитывать попытки)
async def ask_question9(message: types.Message, state: FSMContext):
    await message.answer(
        "🥞 Задание 9\n"
        "В Суботице, где вкусно и тепло,\n"
        "Лепешка жарится, пахнет — просто волшебство.\n"
        "Венгерская, с хрустящей корочкой, она,\n"
        "Назови её имя — и загадка решена."
    )
    await state.update_data(attempts=0)
    await state.set_state(QuestState.question9)

@dp.message(QuestState.question9)
async def process_question9(message: types.Message, state: FSMContext):
    if message.photo:
        await message.answer("❌ Это не фото-задание! Пожалуйста, напиши название лепёшки.")
        return

    data = await state.get_data()
    attempts = data.get("attempts", 0)

    if message.text.strip().lower() == "лангош":
        await message.answer("✅ Совершенно верно! Думаю, стоит попробовать, пока ты здесь!")
        await ask_question10(message, state)
    else:
        attempts += 1
        await state.update_data(attempts=attempts)
        if attempts < 3:
            await message.answer(f"❌ Пока не угадал. Про нее я писала в путеводите. Можешь поискать подсказку там. Осталось попыток: {3 - attempts}")
        else:
            await message.answer("❌ К сожалению, неверно! Правильный ответ: Лангош. Не переживай. Впереди последнее задание, оно творческое и проигравших не будет!")
            await ask_question10(message, state)

# Вопрос 10 (фото + Instagram)
async def ask_question10(message: types.Message, state: FSMContext):
    await message.answer(
        "📸 Задание 10\n"
        "Сними тот миг, что в сердце отзовётся,\n"
        "Где город нежно дарит свой привет.\n"
        "Пусть в кадре атмосфера остаётся,\n"
        "Такой, какой запомнишь ты навек."
    )
    await state.update_data(photo_received=False)
    await state.set_state(QuestState.question10)

@dp.message(QuestState.question10, F.photo)
async def process_question10(message: types.Message, state: FSMContext):
    # Принимаем фото
    await bot.send_message(ADMIN_CHAT_ID, f"📷 Пользователь @{message.from_user.username} отправил фото для задания 10")
    await bot.forward_message(ADMIN_CHAT_ID, message.chat.id, message.message_id)

    await message.answer(
        "✅ Замечательный снимок Суботицы!\n"
        "\n"
        "✨ Буду рада, если ты подпишешься на меня в Instagram: https://www.instagram.com/hristy_life\n"
        "📸 Если захочешь, поделись этим фото в сторис и отметь меня — с удовольствием сделаю репост,\n"
        "\n"
        "и расскажу про маленький сюрприз для тех, кто дошёл до конца. 🎁\n"
        "\n"
        "💖 Спасибо за участие в квесте! Надеюсь, тебе понравилось. До новых встреч!"
    )
    await state.clear()

@dp.message(QuestState.question10)
async def handle_text_in_question10(message: types.Message):
    await message.answer("❌ Сделай фото, которое, по твоему мнению, передаёт атмосферу Суботицы.")


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())