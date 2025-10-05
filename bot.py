# bot.py
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
import os
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import time
import json
from gtts import gTTS
from pydub import AudioSegment

from content import get_daily_content, COURSES

load_dotenv()

API_TOKEN = os.getenv('BOT_TOKEN')

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

user_scores = {}

class QuizCallback(CallbackData, prefix="quiz"):
    answer_index: int

SCORES_FILE = "scores.json"

# Всегда видимая клавиатура
main_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🏠 Начать работу")]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

def load_scores():
    return {}

def save_scores():
    pass  # ничего не делаем

def text_to_speech(text: str, lang: str = 'es') -> str:
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        mp3_file = "temp.mp3"
        ogg_file = "temp.ogg"
        tts.save(mp3_file)
        audio = AudioSegment.from_mp3(mp3_file)
        audio.export(ogg_file, format="ogg")
        os.remove(mp3_file)
        return ogg_file
    except Exception as e:
        print(f"❌ Ошибка при создании аудио: {e}")
        return None

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_scores:
        user_scores[user_id] = {
            "puntos": 0,
            "nivel": "A1",
            "curso": "general",
            "palabras_aprendidas": 0,
            "quiz_resueltos": 0,
            "errores": 0
        }
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📚 Общий курс", callback_data="curso_general")],
            [InlineKeyboardButton(text="✈️ Путешествия", callback_data="curso_viajes")],
            [InlineKeyboardButton(text="💼 Деловой", callback_data="curso_negocios")]
        ])
        await message.answer(
            "¡Hola! 👋 Я MiniEspañolBot — твой мини-помощник в изучении испанского.\n\n"
            "📌 Сначала выбери свой курс:",
            reply_markup=keyboard
        )
    else:
        inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔤 Слово дня", callback_data="menu_palabra")],
            [InlineKeyboardButton(text="🗣 Фраза дня", callback_data="menu_frase")],
            [InlineKeyboardButton(text="❓ Викторина", callback_data="menu_quiz")],
            [InlineKeyboardButton(text="🎓 Выбрать курс", callback_data="menu_curso")],
            [InlineKeyboardButton(text="📊 Мой прогресс", callback_data="menu_progreso")]
        ])
        await message.answer(
            "¡Bienvenido de nuevo! 😊\nВыбери, что хочешь сделать:",
            reply_markup=inline_keyboard
        )
        await message.answer(
            "👇 Нажми «Начать работу», чтобы открыть меню в любое время",
            reply_markup=main_menu_keyboard
        )

@dp.callback_query(lambda c: c.data.startswith("curso_"))
async def set_course(call: types.CallbackQuery):
    user_id = call.from_user.id
    curso = call.data.split("_")[1]
    if user_id not in user_scores:
        user_scores[user_id] = {"puntos": 0, "nivel": "A1"}
    user_scores[user_id]["curso"] = curso
    save_scores()
    curso_names = {
        "general": "Общий курс",
        "viajes": "Испанский для путешествий",
        "negocios": "Деловой испанский"
    }
    await call.message.answer(f"✅ Курс выбран: {curso_names.get(curso, curso)}.")
    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔤 Слово дня", callback_data="menu_palabra")],
        [InlineKeyboardButton(text="🗣 Фраза дня", callback_data="menu_frase")],
        [InlineKeyboardButton(text="❓ Викторина", callback_data="menu_quiz")],
        [InlineKeyboardButton(text="🎓 Выбрать курс", callback_data="menu_curso")],
        [InlineKeyboardButton(text="📊 Мой прогресс", callback_data="menu_progreso")]
    ])
    await call.message.answer("Что будем делать дальше?", reply_markup=inline_keyboard)
    await call.answer()

@dp.message(lambda message: message.text == "🏠 Начать работу")
async def handle_main_menu_button(message: types.Message):
    await send_welcome(message)

# --- Меню обработчики ---
@dp.callback_query(lambda c: c.data == "menu_palabra")
async def menu_palabra(call: types.CallbackQuery):
    await send_word(call.message)
    await call.answer()

@dp.callback_query(lambda c: c.data == "menu_frase")
async def menu_frase(call: types.CallbackQuery):
    await send_phrase(call.message)
    await call.answer()

@dp.callback_query(lambda c: c.data == "menu_quiz")
async def menu_quiz(call: types.CallbackQuery):
    await send_quiz(call.message)
    await call.answer()

@dp.callback_query(lambda c: c.data == "menu_curso")
async def menu_curso(call: types.CallbackQuery):
    await choose_course(call.message)
    await call.answer()

@dp.callback_query(lambda c: c.data == "menu_progreso")
async def menu_progreso(call: types.CallbackQuery):
    await show_progress(call.message)
    await call.answer()

# --- Команды ---
@dp.message(Command("palabra"))
async def send_word(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_scores:
        user_scores[user_id] = {
            "puntos": 0,
            "nivel": "A1",
            "curso": "general",
            "palabras_aprendidas": 0,
            "quiz_resueltos": 0,
            "errores": 0
        }
    curso = user_scores[user_id].get("curso", "general")
    daily_content = get_daily_content(curso=curso)
    user_scores[user_id]["palabras_aprendidas"] += 1
    save_scores()
    word = daily_content["palabra"]
    await message.answer(
        f"🔤 *Palabra del día ({COURSES[curso]['name']}):*\n"
        f"*{word['es']}* — {word['ru']}\n\n"
        f"💬 Пример: _{word['example']}_",
        parse_mode="Markdown"
    )
    audio_file = text_to_speech(word['es'], lang='es')
    if audio_file:
        voice_file = FSInputFile(audio_file)
        await message.answer_voice(voice_file, caption="🔊 Произношение")
        os.remove(audio_file)

@dp.message(Command("frase"))
async def send_phrase(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_scores:
        user_scores[user_id] = {
            "puntos": 0,
            "nivel": "A1",
            "curso": "general",
            "palabras_aprendidas": 0,
            "quiz_resueltos": 0,
            "errores": 0
        }
    curso = user_scores[user_id].get("curso", "general")
    daily_content = get_daily_content(curso=curso)
    phrase = daily_content["frase"]
    await message.answer(
        f"🗣 *Frase del día ({COURSES[curso]['name']}):*\n"
        f"_{phrase['es']}_\n"
        f"→ {phrase['ru']}\n\n"
        f"📌 Контекст: {phrase['context']}",
        parse_mode="Markdown"
    )
    audio_file = text_to_speech(phrase['es'], lang='es')
    if audio_file:
        voice_file = FSInputFile(audio_file)
        await message.answer_voice(voice_file, caption="🔊 Произношение фразы")
        os.remove(audio_file)

@dp.message(Command("quiz"))
async def send_quiz(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_scores:
        user_scores[user_id] = {
            "puntos": 0,
            "nivel": "A1",
            "curso": "general",
            "palabras_aprendidas": 0,
            "quiz_resueltos": 0,
            "errores": 0
        }
    curso = user_scores[user_id].get("curso", "general")
    daily_content = get_daily_content(curso=curso)
    quiz = daily_content["quiz"]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for i, option in enumerate(quiz["options"]):
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=option,
                callback_data=QuizCallback(answer_index=i).pack()
            )
        ])
    await message.answer(f"❓ *{quiz['question']}*", reply_markup=keyboard, parse_mode="Markdown")

@dp.callback_query(QuizCallback.filter())
async def handle_quiz_answer(call: types.CallbackQuery, callback_data: QuizCallback):
    user_id = call.from_user.id
    if user_id not in user_scores:
        user_scores[user_id] = {
            "puntos": 0,
            "nivel": "A1",
            "curso": "general",
            "palabras_aprendidas": 0,
            "quiz_resueltos": 0,
            "errores": 0
        }
    else:
        user = user_scores[user_id]
        user.setdefault("quiz_resueltos", 0)
        user.setdefault("errores", 0)
        user.setdefault("palabras_aprendidas", 0)
        user.setdefault("curso", "general")
    selected_index = callback_data.answer_index
    curso = user_scores[user_id]["curso"]
    daily_content = get_daily_content(curso=curso)
    correct_index = daily_content["quiz"]["correct"]
    user_scores[user_id]["quiz_resueltos"] += 1
    if selected_index == correct_index:
        user_scores[user_id]["puntos"] += 10
        save_scores()
        await call.message.answer("✅ ¡Correcto! +10 puntos 🎉")
    else:
        user_scores[user_id]["errores"] += 1
        save_scores()
        await call.message.answer(f"❌ No es correcto. Правильный ответ: *{daily_content['quiz']['options'][correct_index]}*", parse_mode="Markdown")
    await call.answer()

@dp.message(Command("progreso"))
async def show_progress(message: types.Message):
    user_id = message.from_user.id
    user = user_scores.get(user_id, {})
    puntos = user.get("puntos", 0)
    quiz_resueltos = user.get("quiz_resueltos", 0)
    errores = user.get("errores", 0)
    palabras_aprendidas = user.get("palabras_aprendidas", 0)
    curso = user.get("curso", "general")
    if quiz_resueltos > 0:
        porcentaje = round((quiz_resueltos - errores) / quiz_resueltos * 100)
    else:
        porcentaje = 0
    curso_name = COURSES.get(curso, {}).get("name", "Общий курс")
    mensaje = (
        f"📊 *Твоя статистика:*\n\n"
        f"📚 Курс: {curso_name}\n"
        f"🏆 Очки: *{puntos}*\n"
        f"❓ Всего вопросов: {quiz_resueltos}\n"
        f"✅ Правильных: {quiz_resueltos - errores}\n"
        f"❌ Ошибок: {errores}\n"
        f"📈 Точность: *{porcentaje}%*\n"
        f"📖 Слов выучено: {palabras_aprendidas}"
    )
    await message.answer(mensaje, parse_mode="Markdown")

@dp.message(Command("curso"))
async def choose_course(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 Общий курс", callback_data="curso_general")],
        [InlineKeyboardButton(text="✈️ Путешествия", callback_data="curso_viajes")],
        [InlineKeyboardButton(text="💼 Деловой", callback_data="curso_negocios")]
    ])
    await message.answer("elige un curso:", reply_markup=keyboard)

@dp.message(Command("puntos"))
async def show_points(message: types.Message):
    user_id = message.from_user.id
    points = user_scores.get(user_id, {}).get("puntos", 0)
    await message.answer(f"🏆 Твои очки: *{points}*", parse_mode="Markdown")

@dp.message(Command("reset"))
async def reset_points(message: types.Message):
    user_id = message.from_user.id
    user_scores[user_id] = {"puntos": 0, "nivel": "A1", "curso": "general", "palabras_aprendidas": 0, "quiz_resueltos": 0, "errores": 0}
    save_scores()
    await message.answer("🔄 Очки сброшены.")

async def send_daily_lesson(bot: Bot):
    for user_id in list(user_scores.keys()):
        try:
            curso = user_scores[user_id].get("curso", "general")
            daily_content = get_daily_content(curso=curso)
            await bot.send_message(user_id, "🌅 *¡Buenos días! Aquí está tu lección diaria:*", parse_mode="Markdown")
            # Слово
            word = daily_content["palabra"]
            user_scores[user_id]["palabras_aprendidas"] += 1
            await bot.send_message(
                user_id,
                f"🔤 *Palabra del día ({COURSES[curso]['name']}):*\n*{word['es']}* — {word['ru']}\n💬 Пример: _{word['example']}_",
                parse_mode="Markdown"
            )
            audio_file = text_to_speech(word['es'], lang='es')
            if audio_file:
                voice_file = FSInputFile(audio_file)
                await bot.send_voice(user_id, voice_file, caption="🔊 Произношение")
                os.remove(audio_file)
            # Фраза
            phrase = daily_content["frase"]
            await bot.send_message(
                user_id,
                f"🗣 *Frase del día ({COURSES[curso]['name']}):*\n_{phrase['es']}_\n→ {phrase['ru']}\n📌 Контекст: {phrase['context']}",
                parse_mode="Markdown"
            )
            audio_file = text_to_speech(phrase['es'], lang='es')
            if audio_file:
                voice_file = FSInputFile(audio_file)
                await bot.send_voice(user_id, voice_file, caption="🔊 Произношение фразы")
                os.remove(audio_file)
            # Викторина
            quiz = daily_content["quiz"]
            keyboard = InlineKeyboardMarkup(inline_keyboard=[])
            for i, option in enumerate(quiz["options"]):
                keyboard.inline_keyboard.append([
                    InlineKeyboardButton(
                        text=option,
                        callback_data=QuizCallback(answer_index=i).pack()
                    )
                ])
            await bot.send_message(
                user_id,
                f"❓ *{quiz['question']}*",
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Не удалось отправить урок пользователю {user_id}: {e}")
            user_scores.pop(user_id, None)

# scheduler = AsyncIOScheduler()
# scheduler.add_job(
#     send_daily_lesson,
#     "cron",
#     hour=9,
#     minute=0,
#     args=[bot]
# )

async def main():
    global user_scores
    user_scores = load_scores()
   #scheduler.start()
    await dp.start_polling(bot, allowed_updates=["message", "callback_query"])

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())