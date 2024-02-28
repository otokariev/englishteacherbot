import threading

word = 'WATER'

def start(word):


    threading.Timer(2, first_letter, args=[word]).start()
    threading.Timer(4, second_letter, args=[word]).start()
    threading.Timer(6, third_letter, args=[word]).start()


def first_letter(number):
    word_len = len(word)
    starred = '*' * word_len
    hint = word[0] + starred[1:]
    print(hint)

def second_letter(number):
    word_len = len(word)
    starred = '*' * word_len
    hint = word[:2] + starred[2:]
    print(hint)

def third_letter(number):
    word_len = len(word)
    starred = '*' * word_len
    hint = word[:3] + starred[3:]
    print(hint)


start(word)
