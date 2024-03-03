import telebot
from fastapi import FastAPI, Request, Response
from deep_translator import GoogleTranslator
from config import TOKEN
import time
import threading
import random
import json
import requests

bot = telebot.TeleBot(TOKEN)

app = FastAPI()

URL = ('https://englishteacherbot.onrender.com/' +
       '51b9e4b9cbd872e827c45f9db4a6c002611bd9a2437a4f278066282abc2f3a40')

bot.remove_webhook()
bot.set_webhook(url=URL)


@app.post('/' + '51b9e4b9cbd872e827c45f9db4a6c002611bd9a2437a4f278066282abc2f3a40')
async def webhook(request: Request):
    update = telebot.types.Update.de_json((await request.body()).decode('utf-8'))
    bot.process_new_updates([update])
    return 'ok'


hint1: threading.Timer | None
hint2: threading.Timer | None
hint3: threading.Timer | None
timeout: threading.Timer | None

game = False

DICTIONARY = 'dictionaries/hard.json'
GROUP_MEETING = 'groups/chat_-1002046915616_scores.json'

win_phrases = ['Good job', 'Well done', 'Congrats', 'Hooray', 'Cheers', 'Bravo']
play_phrases = ['Ok!', 'No problem!', 'Great!', "Let's do it!"]
play_again_phrases = ['Another word?', 'PLay again?', 'More?', 'Play more?', 'Another round?']

# try:
#     with open(DICTIONARY, 'r') as f:
#         dictionary = json.load(f)
# except FileNotFoundError:
#     dictionary = {}


def get_word(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            json_data = json.loads(response.text)
            str_data = json_data[0]
            if str_data:
                return str_data
            else:
                print("Word not found in JSON data")
                return None
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None


word_url = 'https://random-word-api.herokuapp.com/word'


@app.get('/')
async def root():
    return {"message": "Welcome to English Teacher Bot"}


@app.get('/hard')
async def view_dictionary():
    try:
        with open(DICTIONARY, 'r', encoding='utf-8') as file:
            dictionary_content = json.load(file)
        return Response(
            content=json.dumps(dictionary_content, ensure_ascii=False, indent=4),
            media_type="application/json"
        )

    except FileNotFoundError:
        return Response(content="Dictionary file not found.", status_code=404)


@app.get('/meeting')
async def view_dictionary():
    try:
        with open(GROUP_MEETING, 'r', encoding='utf-8') as file:
            user_content = json.load(file)
        return Response(
            content=json.dumps(user_content, ensure_ascii=False, indent=4),
            media_type='application/json'
        )

    except FileNotFoundError:
        return Response(content="Dictionary file not found.", status_code=404)


@bot.message_handler(commands=['words'])
def view_words(message):
    if dictionary:
        words_list = "\n".join([f"{word}: {translation}" for word, translation in list(dictionary.items())[-50:]])
        bot.send_message(message.chat.id,
                         f'List of words with translations:\n\n{words_list}\n\nBack to dev menu ⭐ /dev ⭐')
    else:
        bot.send_message(message.chat.id, "The dictionary is empty!")


@bot.message_handler(commands=['add'])
def add_word(message):
    bot.send_message(message.chat.id, "Please enter the word you want to add (RUSSIAN/UKRAINIAN):")
    bot.register_next_step_handler(message, check_word)


def check_word(message):
    if message.content_type == 'text' and not message.text.startswith('/'):
        word = message.text.strip().upper()
        if word not in dictionary:
            bot.send_message(message.chat.id, f"Please enter the translation for the word '{word}':")
            bot.register_next_step_handler(message, get_translation, word)
        else:
            bot.send_message(message.chat.id,
                             f" ❌ The word '{word}' already exists in the dictionary ❌\n"
                             "Back to dev menu ⭐ /dev ⭐")
    else:
        bot.send_message(message.chat.id, 'Enter text only!\nBack to dev menu ⭐ /dev ⭐')


def get_translation(message, word):
    if message.content_type != 'text' or message.text.startswith('/'):
        bot.send_message(message.chat.id, 'Enter text only!\nBack to dev menu ⭐ /dev ⭐')
    else:
        translation = message.text.strip().upper()
        dictionary[word] = translation
        bot.send_message(message.chat.id,
                         f'The word "{word}" with translation "{translation}" has been added successfully!\n'
                         f'Back to dev menu ⭐ /dev ⭐')

        with open(DICTIONARY, "w", encoding="utf-8") as file:
            json.dump(dictionary, file, ensure_ascii=False, indent=4)


@bot.message_handler(commands=['delete'])
def delete_word(message):
    bot.send_message(message.chat.id, "Please enter the word you want to delete:")
    bot.register_next_step_handler(message, check_delete_word)


def check_delete_word(message):
    if message.content_type == 'text' and not message.text.startswith('/'):
        word_to_delete = message.text.strip().upper()
        if word_to_delete in dictionary:
            del dictionary[word_to_delete]
            with open(DICTIONARY, "w", encoding="utf-8") as file:
                json.dump(dictionary, file, ensure_ascii=False, indent=4)
            bot.send_message(message.chat.id,
                             f"The word '{word_to_delete}' has been successfully deleted from the dictionary.\n"
                             f"Back to dev menu ⭐ /dev ⭐")
        else:
            bot.send_message(message.chat.id, f" ❌ The word '{word_to_delete}' doesn't exist in the dictionary ❌\n"
                                              "Back to dev menu ⭐ /dev ⭐")
    else:
        bot.send_message(message.chat.id, 'Enter text only!\nBack to dev menu ⭐ /dev ⭐')


@bot.message_handler(commands=['group_id'])
def get_group_id(message):
    bot.send_message(message.from_user.id, f'{message.chat.title}\n{message.chat.id}')


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

        for user_id_name, score in sorted_scores:
            user_id = user_id_name.split('_')[0]
            user = bot.get_chat_member(message.chat.id, user_id).user
            username = f"{user.first_name} {user.last_name}"
            score_list += f"{username}: {score}\n"

        bot.send_message(message.chat.id, '⚡ Top Scores ⚡\n\n' + score_list + f'\nBack to menu ⭐ /menu ⭐')
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

    user_id = message.from_user.id
    username = bot.get_chat_member(message.chat.id, message.from_user.id).user.username
    user = f'{user_id}_{username}'
    scores[user] = scores.get(user, 0) + 1

    with open(score_file, "w", encoding="utf-8") as file:
        json.dump(scores, file, ensure_ascii=False, indent=4)


@bot.message_handler(commands=['edit_user'])
def edit_user_score(message):
    bot.send_message(message.chat.id, "Please enter the username:")
    bot.register_next_step_handler(message, check_user_score)


def check_user_score(message):
    if message.content_type == 'text' and not message.text.startswith('/'):
        user = message.text

        # score_file = get_score_filename(message)
        score_file = 'groups/chat_-1002046915616_scores.json'
        try:
            with open(score_file, 'r') as file:
                scores = json.load(file)
        except FileNotFoundError:
            scores = {}

        if user in scores:
            bot.send_message(message.chat.id, "Please enter the number of points:")
            bot.register_next_step_handler(message, save_user_points, user)

        else:
            bot.send_message(message.chat.id, f" ❌ The user '{user}' doesn't exist!❌")
    else:
        bot.send_message(message.chat.id, 'Enter text only!')


def save_user_points(message, user):
    if message.content_type == 'text' and not message.text.startswith('/'):
        user_points = int(message.text)

        # score_file = get_score_filename(message)
        score_file = 'groups/chat_-1002046915616_scores.json'
        try:
            with open(score_file, 'r') as file:
                scores = json.load(file)
        except FileNotFoundError:
            scores = {}

        scores[user] = user_points

        with open(score_file, "w", encoding="utf-8") as file:
            json.dump(scores, file, ensure_ascii=False, indent=4)

        bot.send_message(message.chat.id, f" The score of user '{user}' has been successfully changed.")

    else:
        bot.send_message(message.chat.id, 'Enter text only!')


@bot.message_handler(commands=['menu'])
def get_menu(message):
    bot.send_message(message.chat.id,
                     f'Welcome to bot menu 🇬🇧\n\n'
                     '🚀 Start is here 👉 /play 👈\n'
                     '🥇 Check the score 👉 /top 👈\n')


@bot.message_handler(commands=['dev'])
def get_menu(message):
    bot.send_message(message.chat.id,
                     f'Welcome to dev menu 🛠\n\n'
                     '📌 Add new word 👉 /add 👈\n'
                     '♻ Delete the word 👉 /delete 👈\n'
                     '📋 Last 50 words 👉 /words 👈\n')


@bot.message_handler(commands=['start'])
def hello(message):
    bot.send_message(message.chat.id,
                     'Hello! 😎\nI am a English teacher bot 🇬🇧\n'
                     'If you want to learn some new words,\njust press /play and try me 😉\n'
                     'Bot menu: ⭐ /menu ⭐')


@bot.message_handler(commands=['play'])
def start_game(message):
    global hint1, hint2, hint3, timeout, game, dictionary
    bot.send_message(message.chat.id, '⏳ Already looking for a new word ⌛')

    game = True

    if game:
        time.sleep(1)
        # word = random.choice(list(dictionary.keys()))

        ######################################################################

        english = get_word(word_url)
        russian = GoogleTranslator(source='auto', target='ru').translate(english)
        dictionary = {russian.upper(): english.upper()}
        word = list(dictionary.keys())[0]

        ######################################################################

        play = random.choice(play_phrases)
        bot.send_message(message.chat.id, f"{play} 😎\nTranslate this word, please:\n✨ {word} ✨")

        hint1 = threading.Timer(10.0, get_hint1, args=[message, word])
        hint2 = threading.Timer(20.0, get_hint2, args=[message, word])
        hint3 = threading.Timer(30.0, get_hint3, args=[message, word])
        timeout = threading.Timer(40.0, run_timeout, args=[message, word])

        # hint1 = threading.Timer(2.0, get_hint1, args=[message, word])
        # hint2 = threading.Timer(4.0, get_hint2, args=[message, word])
        # hint3 = threading.Timer(6.0, get_hint3, args=[message, word])
        # timeout = threading.Timer(8.0, run_timeout, args=[message, word])

        hint1.start()
        hint2.start()
        hint3.start()
        timeout.start()

        bot.register_next_step_handler(message, check_translation, word)


def get_hint1(message, word):
    if ' ' in dictionary[word]:
        translation = dictionary[word].split(' ')
        len_list = [len(item) for item in translation]
        starred_list = ['*' * item for item in len_list]
        hint = (translation[0][:1] + starred_list[0][1:], *starred_list[1:])
        hint_str = ' '.join(map(str, hint))
        bot.send_message(message.chat.id, hint_str)
    else:
        translation = dictionary[word]
        len_list = len(translation)
        starred_list = '*' * len_list
        hint = translation[:1] + starred_list[1:]
        bot.send_message(message.chat.id, hint)


def get_hint2(message, word):
    if ' ' in dictionary[word]:
        translation = dictionary[word].split(' ')
        len_list = [len(item) for item in translation]
        starred_list = ['*' * item for item in len_list]
        if len_list[0] == 1:
            hint = translation[0], translation[1][:1] + starred_list[1][1:], *starred_list[2:]
            hint_str = ' '.join(map(str, hint))
            bot.send_message(message.chat.id, hint_str)
        else:
            hint = translation[0][:2] + starred_list[0][2:], *starred_list[1:]
            hint_str = ' '.join(map(str, hint))
            bot.send_message(message.chat.id, hint_str)
    else:
        translation = dictionary[word]
        len_list = len(translation)
        starred_list = '*' * len_list
        hint = translation[:2] + starred_list[2:]
        bot.send_message(message.chat.id, hint)


def get_hint3(message, word):
    if ' ' in dictionary[word]:
        translation = dictionary[word].split(' ')
        len_list = [len(item) for item in translation]
        starred_list = ['*' * item for item in len_list]
        if len_list[0] == 1:
            hint = translation[0], translation[1][:2] + starred_list[1][2:], *starred_list[2:]
            hint_str = ' '.join(map(str, hint))
            bot.send_message(message.chat.id, hint_str)
        elif len_list[0] == 2:
            hint = translation[0], translation[1][:1] + starred_list[1][1:], *starred_list[2:]
            hint_str = ' '.join(map(str, hint))
            bot.send_message(message.chat.id, hint_str)
        else:
            hint = translation[0][:3] + starred_list[0][3:], *starred_list[1:]
            hint_str = ' '.join(map(str, hint))
            bot.send_message(message.chat.id, hint_str)
    else:
        translation = dictionary[word]
        len_list = len(translation)
        starred_list = '*' * len_list
        hint = translation[:3] + starred_list[3:]
        bot.send_message(message.chat.id, hint)


def run_timeout(message, word):
    global game
    bot.send_message(message.chat.id, f"The correct translation is:\n✨ {dictionary[word]} ✨")
    game = False
    time.sleep(1)
    play_again = random.choice(play_again_phrases)
    bot.send_message(message.chat.id,
                     f"😎 {play_again}\n"
                     "✅ Enter 'y'\n")
    bot.register_next_step_handler(message, continue_game)


def continue_game(message):
    if message.content_type == 'text' \
            and not message.text.startswith('/') \
            and message.text.lower() == 'y':
        start_game(message)
    else:
        bot.send_message(message.chat.id,
                         f'See you later 😎\n'
                         'Back to menu ⭐ /menu ⭐')


def check_translation(message, word):
    global hint1, hint2, hint3, timeout, game

    if game:
        translation = message

        if message.content_type == 'text' \
                and not message.text.startswith('/') \
                and message.text.lower() == '!skip':
            hint1.cancel()
            hint2.cancel()
            hint3.cancel()
            timeout.cancel()

            start_game(message)
        
        elif message.content_type == 'text' \
                and not message.text.startswith('/') \
                and translation.text.strip().lower() == dictionary[word].lower():
            first_name = bot.get_chat_member(message.chat.id, message.from_user.id).user.first_name
            last_name = bot.get_chat_member(message.chat.id, message.from_user.id).user.last_name
            player = f'{first_name} {last_name}'
            win = random.choice(win_phrases)
            bot.send_message(message.chat.id, f'🎯 {win}, {player}! 🎯/\n'
                                              f'🔥 Answer: "{dictionary[word]}" 🔥')

            update_user_score(message)

            hint1.cancel()
            hint2.cancel()
            hint3.cancel()
            timeout.cancel()

            game = False
            time.sleep(3)
            play_again = random.choice(play_again_phrases)
            bot.send_message(message.chat.id,
                             f"😎 {play_again}\n"
                             "✅ Enter 'y'\n")
            bot.register_next_step_handler(message, continue_game)

        else:
            bot.register_next_step_handler(message, check_translation, word)


def get_json_data(url):
    try:
        response = requests.get(url)
        json_data = response.json()
        text_data = json.dumps(json_data, indent=4)
        return text_data
    except requests.exceptions.RequestException as e:
        bot.send_message(361816009, f'Request error: {e}')
        return None


def check_score():
    score_url = "https://englishteacherbot.onrender.com/meeting"
    text_data = get_json_data(score_url)

    if text_data:
        bot.send_message(361816009, f'JSON data received successfully:\n{text_data}')
    else:
        bot.send_message(361816009, 'Failed to get JSON data.')

    threading.Timer(600, check_score).start()


@bot.message_handler(commands=['start_check'])
def start_check(message):
    try:
        bot.send_message(message.chat.id, 'Function check_score has been started successfully.')
        check_score()
    except Exception as e:
        bot.send_message(message.chat.id, f"An error occurred: {str(e)}")
