import time
from termcolor import colored
from settings import HIDE
import getpass

logging_path_file = './program_data/log.txt'

def log(text: str):
    ftime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    text_to_save = ftime + ': ' + text
    with open(logging_path_file, 'a') as file:
        file.write(text_to_save + '\n')
    print(ftime + ': ' + text)

def clog(text: str, color: str = 'white'):
    ftime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    text_to_save = ftime + ': ' + text
    with open(logging_path_file, 'a') as file:
        file.write(text_to_save + '\n')
    print(colored(ftime, 'white') + ': ' + colored(text, color))

def seclog(text: str, sercet_data: str, sercet_hidden: bool = HIDE, color = 'white'):
    ftime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    text_to_save = ftime + ': ' + text
    with open(logging_path_file, 'a') as file:
        file.write(text_to_save + '\n')
    if sercet_hidden:
        text = text.replace(sercet_data, '*' * len(sercet_data))
    print(colored(ftime, 'white') + ': ' + colored(text, color))

def openlog():
    print("-" * 50, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), "-" * 50)
    with open(logging_path_file, 'a') as file:
        file.write("-" * 50 + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + "-" * 50 + '\n')

def closelog():
    print("-" * 50, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), "-" * 50)
    with open(logging_path_file, 'a') as file:
        file.write("-" * 50 + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + "-" * 50 + '\n\n\n')

def cinput(text: str) -> str:
    ftime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    text_to_save = ftime + ': ' + text
    with open(logging_path_file, 'a') as file:
        file.write(text_to_save + '\n')
    return input(colored(ftime, 'white') + ': ' + colored(text, 'white'))

def cgetpass(text: str) -> str:
    ftime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    text_to_save = ftime + ': ' + text
    with open(logging_path_file, 'a') as file:
        file.write(text_to_save + '\n')
    return getpass.getpass(colored(ftime, 'white') + ': ' + colored(text, 'white'))