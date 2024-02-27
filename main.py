import telebot
from config import TOKEN
import time
import threading
# from multiprocessing import Process
import random
import json
from flask import Flask, request

app = Flask(__name__)

URL = ('https://englishteacherbot.pythonanywhere.com/' +
       '51b9e4b9cbd872e827c45f9db4a6c002611bd9a2437a4f278066282abc2f3a40')

bot = telebot.TeleBot(TOKEN, threaded=False)
bot.remove_webhook()
bot.set_webhook(url=URL)


@app.route('/' + '51b9e4b9cbd872e827c45f9db4a6c002611bd9a2437a4f278066282abc2f3a40', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
    bot.process_new_updates([update])
    return 'ok', 200


hint1: threading.Timer | None
hint2: threading.Timer | None
hint3: threading.Timer | None
timeout: threading.Timer | None

game = False

DICTIONARY = 'dictionaries/custom_dictionary.json'

try:
    with open(DICTIONARY, 'r') as f:
        dictionary = json.load(f)
except FileNotFoundError:
    dictionary = {}


# @bot.message_handler(commands=['words'])
# def view_words(message):
#     if dictionary:
#         words_list = "\n".join([f"{word}: {translation}" for word, translation in dictionary.items()])
#         bot.send_message(message.chat.id,
#                          f'List of words with translations:\n\n{words_list}\n\n'
#                          'To get menu press /menu 📋')
#     else:
#         bot.send_message(message.chat.id, "The dictionary is empty!")


@bot.message_handler(commands=['add'])
def add_word(message):
    bot.send_message(message.chat.id, "Please enter the word you want to add (RUSSIAN/UKRAINIAN):")
    bot.register_next_step_handler(message, check_word)


def check_word(message):
    word = message.text.strip().upper()
    if word in dictionary:
        bot.send_message(message.chat.id,
                         f"The word '{word}' already exists in the dictionary\n"
                         "To get menu press /menu 📋")
    else:
        bot.send_message(message.chat.id, f"Please enter the translation for the word '{word}':")
        bot.register_next_step_handler(message, get_translation, word)


def get_translation(message, word):
    translation = message.text.strip().upper()
    dictionary[word] = translation
    bot.send_message(message.chat.id,
                     f'The word "{word}" with translation "{translation}" has been added successfully!\n'
                     f'To get menu press /menu 📋')

    with open(DICTIONARY, "w", encoding="utf-8") as file:
        json.dump(dictionary, file, ensure_ascii=False, indent=4)


@bot.message_handler(commands=['top'])
def get_score(message):
    score_file = get_score_filename(message)
    try:
        with open(score_file, 'r') as file:
            scores = json.load(file)
    except FileNotFoundError:
        scores = {}

    if scores:
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        score_list = ''
        for user_id, score in sorted_scores:
            user = bot.get_chat_member(message.chat.id, user_id).user
            username = user.username if user.username else f"{user.first_name} {user.last_name}"
            score_list += f"{username}: {score}\n"
        bot.send_message(message.chat.id, 'Top Scores:\n\n' + score_list + f'\nTo get menu press /menu 📋')
    else:
        bot.send_message(message.chat.id, "No scores yet!")


def get_score_filename(message):
    chat_type = message.chat.type
    folder = None
    if chat_type == "private":
        folder = "users"
    elif chat_type in ["supergroup", "group"]:
        folder = "groups"
    return f"{folder}/chat_{message.chat.id}_scores.json"


def update_user_score(message):
    score_file = get_score_filename(message)
    try:
        with open(score_file, 'r') as file:
            scores = json.load(file)
    except FileNotFoundError:
        scores = {}

    scores[str(message.from_user.id)] = scores.get(str(message.from_user.id), 0) + 1

    with open(score_file, "w", encoding="utf-8") as file:
        json.dump(scores, file, ensure_ascii=False, indent=4)


@bot.message_handler(commands=['menu'])
def get_menu(message):
    bot.send_message(message.chat.id,
                     f'Welcome to bot menu 🇬🇧\n\n'
                     'If you want to play? press 👉 /play 👈\n'
                     'To check the score press /top 🔝\n'
                     'If you want to add new word press /add 🆕\n')
                     # 'To check all words press /words 🔡')


@bot.message_handler(commands=['start'])
def hello(message):
    bot.send_message(message.chat.id,
                     'Hello! 😎\nI am a English teacher bot 🇬🇧\n'
                     'If you want to learn some new words,\njust press /play and try me 😉\n'
                     'To get menu press /menu 📋')


@bot.message_handler(commands=['play'])
def start_game(message):
    global hint1, hint2, hint3, timeout, game

    game = True

    if game:
        time.sleep(1)
        word = random.choice(list(dictionary.keys()))
        bot.send_message(message.chat.id, f"Ok! 😎\nTranslate this word, please:\n✨ {word} ✨")

        hint1 = threading.Timer(6.0, get_hint1, args=[message, word])
        hint2 = threading.Timer(12.0, get_hint2, args=[message, word])
        hint3 = threading.Timer(18.0, get_hint3, args=[message, word])
        timeout = threading.Timer(24.0, run_timeout, args=[message, word])

        hint1.start()
        hint2.start()
        hint3.start()
        timeout.start()

        bot.register_next_step_handler(message, check_translation, word)


def get_hint1(message, word):
    translation = dictionary[word]
    stars = '*' * len(translation)
    index = random.randint(0, len(translation) - 1)
    stars = stars[:index] + translation[index] + stars[index + 1:]
    bot.send_message(message.chat.id, stars)


def get_hint2(message, word):
    translation = dictionary[word]
    stars = '*' * len(translation)
    indices = random.sample(range(len(translation)), 2)
    for index in indices:
        stars = stars[:index] + translation[index] + stars[index + 1:]
    bot.send_message(message.chat.id, stars)


def get_hint3(message, word):
    translation = dictionary[word]
    stars = '*' * len(translation)
    indices = random.sample(range(len(translation)), 3)
    for index in indices:
        stars = stars[:index] + translation[index] + stars[index + 1:]
    bot.send_message(message.chat.id, stars)


def run_timeout(message, word):
    global game
    bot.send_message(message.chat.id, f"The correct translation is:\n✨ {dictionary[word]} ✨")
    game = False
    time.sleep(1)
    bot.send_message(message.chat.id,
                     "Do you want more? 😎\n"
                     "Enter 'y' if 'Yes ✅\n"
                     "Any other answer for me is 'no' ❌")
    bot.register_next_step_handler(message, continue_game)


def continue_game(message):
    if message.text.lower() == 'y':
        start_game(message)
    else:
        bot.send_message(message.chat.id,
                         f'See you later 😎\n'
                         'To get menu press /menu 📋')


def check_translation(message, word):
    global hint1, hint2, hint3, timeout, game

    if game:
        translation = message.text.strip().lower()
        if translation == dictionary[word].lower():
            bot.send_message(message.chat.id, "🎯 Exactly! 🥇")

            update_user_score(message)

            hint1.cancel()
            hint2.cancel()
            hint3.cancel()
            timeout.cancel()

            game = False
            time.sleep(1)
            bot.send_message(message.chat.id,
                             "Do you want more? 😎\n"
                             "Enter 'y' if 'Yes ✅\n"
                             "Any other answer for me is 'no' ❌"
                             )
            bot.register_next_step_handler(message, continue_game)

        else:
            bot.register_next_step_handler(message, check_translation, word)


if __name__ == "__main__":
    bot.polling(none_stop=True)
