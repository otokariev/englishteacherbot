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


bot_name = '@whiamibot'

hint1: threading.Timer | None
hint2: threading.Timer | None
hint3: threading.Timer | None
timeout: threading.Timer | None

game = False

BASIC_DICT = 'dictionary/basic_dict.json'
ADVANCED_DICT = 'dictionary/advanced_dict.json'
GROUP_MEETING = 'group/chat_-1002046915616_scores.json'

win_phrases = ['Good job', 'Well done', 'Congrats', 'Hooray', 'Cheers', 'Bravo']
play_phrases = ['Ok!', 'No problem!', 'Great!', "Let's do it!"]
play_again_phrases = ['Another word?', 'Play again?', 'More?', 'Play more?', 'Another round?']

ADMIN = 361816009
MODERATOR_LIST = [517905016]

try:
    with open(BASIC_DICT, 'r') as f:
        basic_dict = json.load(f)
except FileNotFoundError:
    basic_dict = {}

try:
    with open(ADVANCED_DICT, 'r') as f:
        advanced_dict = json.load(f)
except FileNotFoundError:
    advanced_dict = {}


def send_message_and_delete(chat_id, text, delay=60):
    bot_message = bot.send_message(chat_id, text)

    def delete_message():
        time.sleep(delay)
        if bot_message:
            bot.delete_message(chat_id, bot_message.message_id)

    threading.Thread(target=delete_message).start()


def delete_user_command(message, delay=60):

    def delete_message():
        time.sleep(delay)

        # if message and message.text.startswith('/'):
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except Exception as ex:
            bot.send_message(ADMIN, f'Deleting user message error:\n\n{ex}')

    threading.Thread(target=delete_message).start()


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


@app.get('/meeting')
async def view_score():
    try:
        with open(GROUP_MEETING, 'r', encoding='utf-8') as file:
            user_content = json.load(file)
        return Response(
            content=json.dumps(user_content, ensure_ascii=False, indent=4),
            media_type='application/json'
        )

    except FileNotFoundError:
        return Response(content="Score file not found.", status_code=404)


@app.get('/hard')
async def view_dictionary():
    try:
        with open(ADVANCED_DICT, 'r', encoding='utf-8') as file:
            dictionary_content = json.load(file)
        return Response(
            content=json.dumps(dictionary_content, ensure_ascii=False, indent=4),
            media_type='application/json'
        )

    except FileNotFoundError:
        return Response(content="Score file not found.", status_code=404)


@bot.message_handler(commands=['words'])
def view_words(message):
    delete_user_command(message)
    if advanced_dict:
        words_list = "\n".join([f"{word}: {translation}" for word, translation in list(advanced_dict.items())[-50:]])
        send_message_and_delete(message.chat.id,
                                f'List of words with translations:\n\n{words_list}\n\nBack to menu ⭐ /dev ⭐')
    else:
        send_message_and_delete(message.chat.id, "The dictionary is empty!")


# @bot.message_handler(commands=['add'])
# def add_word(message):
#     bot.send_message(message.chat.id, "Please enter the word you want to add (RUSSIAN/UKRAINIAN):")
#     bot.register_next_step_handler(message, check_word)
#
#
# def check_word(message):
#     if message.content_type == 'text' and not message.text.startswith('/'):
#         word = message.text.strip().upper()
#         if word not in dictionary:
#             bot.send_message(message.chat.id, f"Please enter the translation for the word '{word}':")
#             bot.register_next_step_handler(message, get_translation, word)
#         else:
#             bot.send_message(message.chat.id,
#                              f" ❌ The word '{word}' already exists in the dictionary ❌\n"
#                              "Back to dev menu ⭐ /dev ⭐")
#     else:
#         bot.send_message(message.chat.id, 'Enter text only!\nBack to dev menu ⭐ /dev ⭐')
#
#
# def get_translation(message, word):
#     if message.content_type != 'text' or message.text.startswith('/'):
#         bot.send_message(message.chat.id, 'Enter text only!\nBack to dev menu ⭐ /dev ⭐')
#     else:
#         translation = message.text.strip().upper()
#         dictionary[word] = translation
#         bot.send_message(message.chat.id,
#                          f'The word "{word}" with translation "{translation}" has been added successfully!\n'
#                          f'Back to dev menu ⭐ /dev ⭐')
#
#         with open(DICTIONARY, "w", encoding="utf-8") as file:
#             json.dump(dictionary, file, ensure_ascii=False, indent=4)


# @bot.message_handler(commands=['delete'])
# def delete_word(message):
#     bot.send_message(message.chat.id, "Please enter the word you want to delete:")
#     bot.register_next_step_handler(message, check_delete_word)
#
#
# def check_delete_word(message):
#     if message.content_type == 'text' and not message.text.startswith('/'):
#         word_to_delete = message.text.strip().upper()
#         if word_to_delete in dictionary:
#             del dictionary[word_to_delete]
#             with open(DICTIONARY, "w", encoding="utf-8") as file:
#                 json.dump(dictionary, file, ensure_ascii=False, indent=4)
#             bot.send_message(message.chat.id,
#                              f"The word '{word_to_delete}' has been successfully deleted from the dictionary.\n"
#                              f"Back to dev menu ⭐ /dev ⭐")
#         else:
#             bot.send_message(message.chat.id, f" ❌ The word '{word_to_delete}' doesn't exist in the dictionary ❌\n"
#                                               "Back to dev menu ⭐ /dev ⭐")
#     else:
#         bot.send_message(message.chat.id, 'Enter text only!\nBack to dev menu ⭐ /dev ⭐')


@bot.message_handler(commands=['group_id'])
def get_group_id(message):
    delete_user_command(message)
    send_message_and_delete(message.from_user.id, f'{message.chat.title}\n{message.chat.id}')


def sort_scores(message, scores):
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    score_list = ''

    for user_id_username, score in sorted_scores:
        user_id = user_id_username.split('_')[0]
        user = bot.get_chat_member(message.chat.id, user_id).user

        if user.first_name and user.last_name:
            username = f'{user.first_name} {user.last_name}'
        elif user.first_name or user.last_name:
            last_name = user.last_name if user.last_name else ''
            username = f"{user.first_name} {last_name}"
        else:
            username = f'{user.username}'

        score_list += f"{username}: {score}\n"

    return score_list


@bot.message_handler(commands=['dict'])
def get_top_dict(message):
    delete_user_command(message)
    score_file = get_score_filename(message)
    try:
        with open(score_file, 'r') as file:
            top_list = json.load(file)
    except FileNotFoundError:
        top_list = {}

    sorted_top_dict = dict(sorted(top_list.items(), key=lambda x: x[1], reverse=True))
    delete_user_command(message)

    return sorted_top_dict, score_file


@bot.message_handler(commands=['top'])
def get_score(message):
    delete_user_command(message)
    scores, score_file = get_top_dict(message)

    if scores:
        sorted_scores = sort_scores(message, scores)
        send_message_and_delete(message.chat.id, '⚡ Top Scores ⚡\n\n' + sorted_scores + f'\n↩ Back to menu ⭐ /menu ⭐')
    else:
        send_message_and_delete(message.chat.id, "No scores yet!")


def get_score_filename(message):
    chat_type = message.chat.type
    folder = None
    if chat_type == "private":
        folder = "user"
    elif chat_type in ["supergroup", "group"]:
        folder = "group"
    return f"{folder}/chat_{message.chat.id}_scores.json"


@bot.message_handler(commands=['update'])
def update_user_score(message):
    delete_user_command(message)
    scores, score_file = get_top_dict(message)

    last_scores = scores.copy()

    user_id = message.from_user.id
    username = bot.get_chat_member(message.chat.id, message.from_user.id).user.username
    user = f'{user_id}_{username}'
    scores[user] = scores.get(user, 0) + 1

    from_chat = message.chat.id
    updated_scores = scores
    bot.send_message(ADMIN, f'Updated score from chat:\n\n{from_chat}\n\n{updated_scores}')

    with open(score_file, "w", encoding="utf-8") as file:
        json.dump(scores, file, ensure_ascii=False, indent=4)

    is_champion(message, last_scores, updated_scores)


def is_champion(message, last_scores, updated_scores):
    last = sort_scores(message, last_scores)
    updated = sort_scores(message, updated_scores)

    last_list = last.split('\n')[0]
    updated_list = updated.split('\n')[0]

    last_champion_score = last_list.split(':', maxsplit=1)[1]
    new_champion_score = updated_list.split(':', maxsplit=1)[1]
    last_champion = last.split(':', maxsplit=1)[0]
    new_champion = updated.split(':', maxsplit=1)[0]

    if (last_champion != new_champion
            and new_champion_score > last_champion_score):
        send_message_and_delete(message.chat.id, f'🎉 Congrats! 🎉\n'
                                                 f'The new champion is:\n'
                                                 f'💥 {new_champion} 💥')


@bot.message_handler(commands=['edit_user'])
def edit_user_score(message):
    delete_user_command(message)
    send_message_and_delete(message.chat.id, "Please enter the username:")
    bot.register_next_step_handler(message, check_user_score)


def check_user_score(message):
    delete_user_command(message)
    if message.content_type == 'text' and not message.text.startswith('/'):
        user = message.text

        # score_file = get_score_filename(message)
        score_file = 'group/chat_-1002046915616_scores.json'
        try:
            with open(score_file, 'r') as file:
                scores = json.load(file)
        except FileNotFoundError:
            scores = {}

        if user in scores:
            send_message_and_delete(message.chat.id, "Please enter the number of points:")
            bot.register_next_step_handler(message, save_user_points, user)

        else:
            send_message_and_delete(message.chat.id, f" ❌ The user '{user}' doesn't exist!❌")
    else:
        send_message_and_delete(message.chat.id, 'Enter text only!')


def save_user_points(message, user):
    delete_user_command(message)
    if message.content_type == 'text' and not message.text.startswith('/'):
        user_points = int(message.text)

        # score_file = get_score_filename(message)
        score_file = 'group/chat_-1002046915616_scores.json'
        try:
            with open(score_file, 'r') as file:
                scores = json.load(file)
        except FileNotFoundError:
            scores = {}

        scores[user] = user_points

        with open(score_file, "w", encoding="utf-8") as file:
            json.dump(scores, file, ensure_ascii=False, indent=4)

        send_message_and_delete(message.chat.id, f" The score of user '{user}' has been successfully changed.")

    else:
        send_message_and_delete(message.chat.id, 'Enter text only!')


@bot.message_handler(commands=['menu'])
def get_menu(message):
    delete_user_command(message)
    if message.chat.type == "private":

        if message.from_user.id == ADMIN:
            send_message_and_delete(message.chat.id,
                                    f'🇺🇸 Welcome to admin menu 🇬🇧\n\n'
                                    '🚀 Start is here 👉 /play 👈\n'
                                    '🥇 Check the score 👉 /top 👈\n'
                                    # '📌 Add new word 👉 /add 👈\n'
                                    # '♻ Delete the word 👉 /delete 👈\n'
                                    '📋 Last 50 words 👉 /words 👈\n'
                                    '✅ Exec check func 👉 /check 👈\n'
                                    '🆔 Check chat id 👉 /chat_id 👈\n'
                                    '📊 To edit score 👉 /edit_score 👈\n'
                                    '🔝 Inc user score by 1 👉 /update 👈\n')

        elif message.from_user.id in MODERATOR_LIST:
            send_message_and_delete(message.chat.id,
                                    f'🇺🇸 Welcome to moderator menu 🇬🇧\n\n'
                                    '🚀 Start is here 👉 /play 👈\n'
                                    '🥇 Check the score 👉 /top 👈\n'
                                    # '📌 Add new word 👉 /add 👈\n'
                                    # '♻ Delete the word 👉 /delete 👈\n'
                                    '📋 Last 50 words 👉 /words 👈\n')

        else:
            send_message_and_delete(message.chat.id,
                                    '🇺🇸 Welcome to bot menu 🇬🇧\n\n'
                                    '🚀 Start is here 👉 /play 👈\n')

    else:
        send_message_and_delete(message.chat.id,
                                f'🇺🇸 Welcome to bot menu 🇬🇧\n\n'
                                '🚀 Start is here 👉 /play 👈\n'
                                '🥇 Check the score 👉 /top 👈\n')


@bot.message_handler(commands=['start'])
def hello(message):
    delete_user_command(message)
    send_message_and_delete(message.chat.id,
                            'Hello! 😎\nI am a English teacher bot 🇬🇧\n'
                            'If you want to learn some new words,\njust press /play and try me 😉\n'
                            'Bot menu: ⭐ /menu ⭐')


def get_or_create_private_dict(message):
    user_id = message.from_user.id
    username = bot.get_chat_member(message.chat.id, message.from_user.id).user.username
    filename = f'dictionary/user/{user_id}_{username}.json'

    try:
        with open(filename, 'r') as file:
            private_dict_file = json.load(file)
    except FileNotFoundError:
        private_dict_file = {}
        with open(filename, 'w') as file:
            json.dump(private_dict_file, file)

    return private_dict_file


@bot.message_handler(commands=['play'])
def choose_dict_category(message):
    delete_user_command(message)
    send_message_and_delete(message.chat.id, '🗂 Choose a category:\n\n'
                                             '🌍 Public(/public)\n'
                                             '🔑 Private(/private)')

    bot.register_next_step_handler(message, valid_dict_category)


def valid_dict_category(message):
    delete_user_command(message)
    if (message.content_type == 'text'
            and message.text in ['/public', '/private',
                                 f'/public{bot_name}', f'/private{bot_name}']):
        if bot_name in message.text:
            category = message.text.split('@')[0]
        else:
            category = message.text

        send_message_and_delete(message.chat.id, f'✅ You have chosen category:\n'
                                                 f'✨ {category.upper()[1:]} ✨')
        time.sleep(0.5)

        if category == '/public':
            choose_dict_level(message, category)

        elif category == '/private':
            level = None
            get_dict_category_and_level(message, category, level)
    else:
        send_message_and_delete(message.chat.id, '⛔ Wrong command.\n'
                                                 'Please, try again.\n\n'
                                                 'Back to menu ⭐ /menu ⭐')


def choose_dict_level(message, category):
    send_message_and_delete(message.chat.id, '📶 Choose a level:\n\n'
                                             '⭐ Basic(/basic)\n'
                                             '💎 Advanced(/advanced)\n'
                                             '🌶 Insane(/insane)')

    bot.register_next_step_handler(message, valid_dict_level, category)


def valid_dict_level(message, category):
    delete_user_command(message)
    if (message.content_type == 'text'
            and message.text in ['/basic', '/advanced', '/insane',
                                 f'/basic{bot_name}', f'/advanced{bot_name}', f'/insane{bot_name}']):

        if bot_name in message.text:
            level = message.text.split('@')[0]
        else:
            level = message.text

        send_message_and_delete(message.chat.id, f'✅ You have chosen level:\n'
                                                 f'✨ {level.upper()[1:]} ✨')
        time.sleep(0.5)
        get_dict_category_and_level(message, category, level)
    else:
        send_message_and_delete(message.chat.id, '⛔ Wrong command.\n'
                                                 'Please, try again.\n\n'
                                                 'Back to menu ⭐ /menu ⭐')


def get_dict_category_and_level(message, category, level):
    if category == '/public':
        if level == '/basic':
            russian = random.choice(list(basic_dict.keys()))

            if len(basic_dict[russian].split(' ')) > 1:
                english_synonyms = basic_dict[russian].split(' ')
                english = random.choice(english_synonyms)
                other_synonyms_list = [synonym for synonym in english_synonyms if synonym != english]
                other_synonyms = ''.join(string + ' \n' for string in other_synonyms_list)
                word = [russian, english, other_synonyms]
                start_game(message, word, category, level)
            else:
                english = basic_dict[russian]
                word = [russian, english]
                start_game(message, word, category, level)

        elif level == '/advanced':
            russian = random.choice(list(advanced_dict.keys()))

            if len(advanced_dict[russian].split(' ')) > 1:
                english_synonyms = advanced_dict[russian].split(' ')
                english = random.choice(english_synonyms)
                other_synonyms_list = [synonym for synonym in english_synonyms if synonym != english]
                other_synonyms = ''.join(string + ' \n' for string in other_synonyms_list)
                word = [russian, english, other_synonyms]
                start_game(message, word, category, level)
            else:
                english = advanced_dict[russian]
                word = [russian, english]
                start_game(message, word, category, level)

        elif level == '/insane':
            english = get_word(word_url).upper()
            russian = GoogleTranslator(source='auto', target='ru').translate(english).upper()
            word = [russian, english]
            start_game(message, word, category, level)

    elif category == '/private':
        private_dict = get_or_create_private_dict(message)

        try:
            russian = random.choice(list(private_dict.keys()))
            english = private_dict[russian]
            word = [russian, english]
            start_game(message, word, category, level)
        except IndexError:
            send_message_and_delete(message.chat.id, '🗑 Your dictionary is empty.\n'
                                                     '✏ Add some words to start learning.\n\n'
                                                     '🕓 "ADD WORD" button will be here\n'
                                                     '↩ Back to menu ⭐ /menu ⭐')


def start_game(message, word, category, level):
    delete_user_command(message)
    global hint1, hint2, hint3, timeout, game
    send_message_and_delete(message.chat.id, '⏳ Looking for a new word ⌛')
    time.sleep(0.5)

    game = True

    if game:

        play = random.choice(play_phrases)
        send_message_and_delete(message.chat.id, f"{play} 😎\nTranslate the word, please:\n\n✨ {word[0]} ✨\n"
                                                 f"🔹 {len(word[1])} letters 🔹\n\n"
                                                 f"Skip the word /skip\n"
                                                 f"Stop the game /stop")

        hint1 = threading.Timer(10.0, get_hint1, args=[message, word])
        hint2 = threading.Timer(20.0, get_hint2, args=[message, word])
        hint3 = threading.Timer(30.0, get_hint3, args=[message, word])
        timeout = threading.Timer(40.0, run_timeout, args=[message, word, category, level])

        hint1.start()
        hint2.start()
        hint3.start()
        timeout.start()

        bot.register_next_step_handler(message, check_answer, word, category, level)


def get_hint1(message, word):
    if ' ' in word[1]:  # API
        translation = word[1]  # API
        len_list = [len(item) for item in translation]
        starred_list = ['*' * item for item in len_list]
        hint = (translation[0][:1] + starred_list[0][1:], *starred_list[1:])
        hint_str = ' '.join(map(str, hint))
        send_message_and_delete(message.chat.id, f"✨ {hint_str} ✨")
    else:
        translation = word[1]
        len_list = len(translation)
        starred_list = '*' * len_list
        hint = translation[:1] + starred_list[1:]
        send_message_and_delete(message.chat.id, f"✨ {hint} ✨")


def get_hint2(message, word):
    if ' ' in word[1]:
        translation = word[1]
        len_list = [len(item) for item in translation]
        starred_list = ['*' * item for item in len_list]
        if len_list[0] == 1:
            hint = translation[0], translation[1][:1] + starred_list[1][1:], *starred_list[2:]
            hint_str = ' '.join(map(str, hint))
            send_message_and_delete(message.chat.id, f"✨ {hint_str} ✨")
        else:
            hint = translation[0][:2] + starred_list[0][2:], *starred_list[1:]
            hint_str = ' '.join(map(str, hint))
            send_message_and_delete(message.chat.id, f"✨ {hint_str} ✨")
    else:
        translation = word[1]
        len_list = len(translation)
        starred_list = '*' * len_list
        hint = translation[:2] + starred_list[2:]
        send_message_and_delete(message.chat.id, f"✨ {hint} ✨")


def get_hint3(message, word):
    if ' ' in word[1]:
        translation = word[1]
        len_list = [len(item) for item in translation]
        starred_list = ['*' * item for item in len_list]
        if len_list[0] == 1:
            hint = translation[0], translation[1][:2] + starred_list[1][2:], *starred_list[2:]
            hint_str = ' '.join(map(str, hint))
            send_message_and_delete(message.chat.id, f"✨ {hint_str} ✨")
        elif len_list[0] == 2:
            hint = translation[0], translation[1][:1] + starred_list[1][1:], *starred_list[2:]
            hint_str = ' '.join(map(str, hint))
            send_message_and_delete(message.chat.id, f"✨ {hint_str} ✨")
        else:
            hint = translation[0][:3] + starred_list[0][3:], *starred_list[1:]
            hint_str = ' '.join(map(str, hint))
            send_message_and_delete(message.chat.id, f"✨ {hint_str} ✨")
    else:
        translation = word[1]
        len_list = len(translation)
        starred_list = '*' * len_list
        hint = translation[:3] + starred_list[3:]
        send_message_and_delete(message.chat.id, f"✨ {hint} ✨")


def run_timeout(message, word, category, level):
    global game

    game = False
    play_again = random.choice(play_again_phrases)

    if len(word) > 2:
        send_message_and_delete(message.chat.id, f'The correct translation is:\n✨ {word[1]} ✨\n\n'
                                                 f'♾ Synonyms:\n'
                                                 f'{word[2]}\n\n'
                                                 f'😎 {play_again}\n✅ Press /yes')
    else:
        send_message_and_delete(message.chat.id, f'The correct translation is:\n✨ {word[1]} ✨\n\n'
                                                 f'😎 {play_again}\n✅ Press /yes')

    bot.register_next_step_handler(message, continue_game, category, level)


def continue_game(message, category, level):
    delete_user_command(message)
    if message.content_type == 'text' \
            and message.text.lower() in ['/yes', f'/yes{bot_name}']:
        get_dict_category_and_level(message, category, level)
    else:
        send_message_and_delete(message.chat.id,
                                f'See you later 😎\n'
                                'Back to menu ⭐ /menu ⭐')


def check_answer(message, word, category, level):
    delete_user_command(message)
    global hint1, hint2, hint3, timeout, game

    if game:
        answer = message

        if message.content_type == 'text' \
                and message.text.lower() in ['/skip', f'/skip{bot_name}']:
            hint1.cancel()
            hint2.cancel()
            hint3.cancel()
            timeout.cancel()

            get_dict_category_and_level(message, category, level)

        elif message.content_type == 'text' \
                and message.text.lower() in ['/stop', f'/stop{bot_name}']:
            hint1.cancel()
            hint2.cancel()
            hint3.cancel()
            timeout.cancel()

            game = False

            send_message_and_delete(message.chat.id,
                                    f'See you later 😎\n'
                                    'Back to menu ⭐ /menu ⭐')

        elif message.content_type == 'text' \
                and not message.text.startswith('/') \
                and answer.text.strip().lower() == word[1].lower():

            game = False

            hint1.cancel()
            hint2.cancel()
            hint3.cancel()
            timeout.cancel()

            first_name = bot.get_chat_member(message.chat.id, message.from_user.id).user.first_name
            last_name = bot.get_chat_member(message.chat.id, message.from_user.id).user.last_name
            player = f'{first_name} {last_name}'
            win = random.choice(win_phrases)
            play_again = random.choice(play_again_phrases)

            if len(word) > 2:
                send_message_and_delete(message.chat.id, f'🎯 {win}, {player}! 🎯\n\n'
                                                         f'The answer is:\n🔥 "{word[1]}" 🔥\n\n'
                                                         f'♾ Synonyms:\n'
                                                         f'{word[2]}\n\n'
                                                         f'😎 {play_again}\n✅ Press /yes')
            else:
                send_message_and_delete(message.chat.id, f'🎯 {win}, {player}! 🎯\n\n'
                                                         f'The answer is:\n🔥 "{word[1]}" 🔥\n\n'
                                                         f'😎 {play_again}\n✅ Press /yes')

            update_user_score(message)

            bot.register_next_step_handler(message, continue_game, category, level)

        else:
            bot.register_next_step_handler(message, check_answer, word, category, level)


def get_json_data(url):
    try:
        requests.get(url)
        # response = requests.get(url)
        # json_data = response.json()
        # text_data = json.dumps(json_data, indent=4)
        # return text_data
        return None
    except requests.exceptions.RequestException as e:
        send_message_and_delete(ADMIN, f'Request error:\n{e}')
        return None


def check_server():
    score_url = "https://englishteacherbot.onrender.com/meeting"
    # text_data = get_json_data(score_url)
    get_json_data(score_url)

    # bot.send_message(ADMIN, ' 200 ok')

    # if text_data:
    #     bot.send_message(ADMIN, f'JSON data received successfully:\n{text_data}')
    # else:
    #     bot.send_message(ADMIN, 'Failed to get JSON data.')

    threading.Timer(59, check_server).start()


@bot.message_handler(commands=['check'])
def check(message):
    delete_user_command(message)
    try:
        send_message_and_delete(message.chat.id, 'Function check_server has been started successfully.')
        check_server()
    except Exception as e:
        send_message_and_delete(message.chat.id, f"An error occurred:\n{str(e)}")
