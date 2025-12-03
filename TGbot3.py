import telebot
from telebot import types

token = "8006780027:AAGnV477CWowaB1ooypxCYyQwbre5urem8c"
bot = telebot.TeleBot(token)

admins = ["7211699666"]

global count_Hello
count_Hello = 0

homeworks_Dictionary = {
    "💕 Алгебра 💕": "Решить чо та нада",
    "🍎 Физика 🍎": "Уравнение Бернулли",
    "🌏 География 🌏": "Где там эти китайцы",
    "📝Русский язык 📝": "Нуу алфавит учи короче",
    "📏 Геометрия 📏": "Бессектриса эта кто такая"
}

admin_state = {}

@bot.message_handler(commands=['start'])

def start(message):
    global count_Hello

    if count_Hello == 0:
        bot.send_message(message.chat.id, "Привет! Опять не записал ДЗ?")

    count_Hello += 1
    show_subject_keyboard(message.chat.id)


def show_subject_keyboard(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [types.KeyboardButton(subject) for subject in homeworks_Dictionary.keys()]
    markup.add(*buttons)
    bot.send_message(chat_id, "Выбери предмет:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text in homeworks_Dictionary.keys())
def send_homework(message):
    user_id = str(message.from_user.id)

    if user_id in admin_state and admin_state[user_id].get("editing", False):
        return

    subject = message.text
    text = f"*{subject}*\n\n{homeworks_Dictionary[subject]}"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🔙Назад🔙"))
    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "🔙Назад🔙")
def go_back(message):
    show_subject_keyboard(message.chat.id)


@bot.message_handler(commands=['sethomework'])
def set_homework(message):
    user_id = str(message.from_user.id)

    if user_id not in admins:
        bot.send_message(message.chat.id, "У вас нет прав!")
        return

    admin_state[user_id] = {"editing": True, "subject": None}

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [types.KeyboardButton(subject) for subject in homeworks_Dictionary.keys()]
    markup.add(*buttons)
    bot.send_message(message.chat.id, "Выбери предмет для изменения:", reply_markup=markup)
    bot.register_next_step_handler(message, choose_subject_for_edit)


def choose_subject_for_edit(message):
    user_id = str(message.from_user.id)
    subject = message.text

    if subject not in homeworks_Dictionary:
        bot.send_message(message.chat.id, f"Предмет *{subject}* не найден.", parse_mode="Markdown")
        admin_state[user_id]["editing"] = False
        return

    admin_state[user_id]["subject"] = subject
    bot.send_message(message.chat.id, f"Введи новое ДЗ для *{subject}*:", parse_mode='Markdown')
    bot.register_next_step_handler(message, save_new_homework)


def save_new_homework(message):
    user_id = str(message.from_user.id)

    if user_id not in admin_state or not admin_state[user_id]["editing"]:
        bot.send_message(message.chat.id, "Ошибка! Начни снова с /sethomework")
        return

    subject = admin_state[user_id]["subject"]
    new_text = message.text

    homeworks_Dictionary[subject] = new_text

    admin_state[user_id]["editing"] = False
    admin_state[user_id]["subject"] = None

    bot.send_message(message.chat.id, f"Новое ДЗ для *{subject}* сохранено!", parse_mode='Markdown')
    show_subject_keyboard(message.chat.id)

@bot.message_handler(commands=['addlesson'])

def new_lesson_is(message):
    user_id = str(message.from_user.id)

    if user_id not in admins:
        bot.send_message(message.chat.id, 'У тебя нет прав для такого!', parse_mode='Markdown')
        return

    admin_state[user_id] = {"adding": True, "lesson": None}
    bot.send_message(message.chat.id, "Введите название нового предмета: ")
    bot.register_next_step_handler(message, add_lesson)


def add_lesson(message):
    user_id = str(message.from_user.id)
    lesson = message.text

    if user_id not in admins:
        bot.send_message(message.chat.id, "Ошибка! Начни опять с /addlesson", parse_mode="Markdown")
        lesson = None
        return
    if lesson in homeworks_Dictionary:
        bot.send_message(message.chat.id, 'Такой предмет уже существует!', parse_mode="Markdown")
        return

    homeworks_Dictionary.update({lesson: None})

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [types.KeyboardButton(lesson) for lesson in homeworks_Dictionary.keys()]
    markup.add(*buttons)

    admin_state[user_id]["adding"] = True
    admin_state[user_id]["lesson"] = lesson

    bot.send_message(message.chat.id, f"Введите домашнее задание для {lesson}", parse_mode="Markdown")
    bot.register_next_step_handler(message, set_lesson_homework)

def set_lesson_homework(message):
    user_id = str(message.from_user.id)

    if user_id not in admins or not admin_state[user_id]["adding"]:
        bot.send_message(message.chat.id, "Прости, но нет", parse_mode="Markdown")
        return
    lesson = admin_state[user_id]["lesson"]

    admin_state[user_id]["adding"] = False
    admin_state[user_id]["lesson"] = None

    homeworks_Dictionary[lesson] = message.text
    bot.send_message(message.chat.id, f"Добавлен новый урок, {lesson}!", parse_mode='Markdown')
    show_subject_keyboard(message.chat.id)

@bot.message_handler(commands=['deletelesson'])

def choose_lesson_to_delete(message):
    user_id = str(message.from_user.id)

    if user_id not in admins:
        bot.send_message(message.chat.id, "Не", parse_mode='Markdown')
        return

    show_subject_keyboard(message.chat.id)
    bot.register_next_step_handler(message, delete_lesson)

@bot.message_handler(func=lambda message: message.text in homeworks_Dictionary.keys())

def delete_lesson(message):
    user_id = str(message.from_user.id)

    if user_id not in admins:
        if admin_state[user_id]["Deleting"]:
            bot.send_message(message.chat.id, "Что-то пошло не так, попробуй ещё раз", parse_mode='Markdown')
        return

    lesson_To_Delete = message.text
    if lesson_To_Delete in homeworks_Dictionary:
        bot.send_message(message.chat.id, "Предмет успешно удалён!")
        homeworks_Dictionary.pop(lesson_To_Delete)
    else:
        bot.send_message(message.chat.id, "Такой предмет уже есть", parse_mode='Markdown')

@bot.message_handler(commands=['help'])

def helpMessage(message):
    user_id = str(message.from_user.id)
    help_Message = f" Базовые комманды: \n\n /help - Просмотреть комманды снова \n /start - Открыть панель уроков"

    adminHelp_Message = f"Админские комманды: \n\n /addlesson - Добавить урок \n /deletelesson - Удалить урок \n /sethomework - Изменить дз к уроку"
    bot.send_message(message.chat.id, help_Message, parse_mode='Markdown')

    if user_id in admins:
            bot.send_message(message.chat.id, adminHelp_Message, parse_mode='Markdown')

print("Бот запущен!")
bot.polling(none_stop=True)

"""
def save_new_homework(message, subject):
    user_id = str(message.from_user.id)
        if user_id not in admin_state or not admin_state[user_id].get("editing"):
        bot.send_message(message.chat.id, f"Чет пошло не так попробуй /sethomework")
        return
    admin_text = message.text # то что написал админ
    homeworks_Dictionary[subject] = admin_text # проверка на то есть ли данный предмет в списке
    bot.send_message(message.chat.id, f"Новое Д\З для *{subject}* было установлено", parse_mode='Markdown') # установка Д\З
    show_subject_keyboard(message.chat.id)

"""

