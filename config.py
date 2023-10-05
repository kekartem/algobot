from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
from aiogram import Bot
import os
import sqlite3

TOKEN = '6159575183:AAHyCC2-yaYIi8ykUBhKLe1xw-7Md2QZoEk'
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

conn = sqlite3.connect('main.db')
cur = conn.cursor()

client_manager_password = 'EhvqU2C!xv!VvUq'
god_password = '6r~Rd@boC#SLlX$'


class Manager:
    def __init__(self, id=-1, manager_chat_id=-1, manager_tg_login=-1):
        self.id = id
        self.manager_chat_id = manager_chat_id
        self.manager_tg_login = manager_tg_login

    
    def __str__(self):
        return f'Manager: {self.id}, {self.manager_chat_id}, {self.manager_tg_login}'


class Request:
    def __init__(self, id=-1, name=-1, number=-1, email=-1, user_tg_login=-1):
        self.id = id
        self.name = name
        self.number = number
        self.email = email
        self.user_tg_login = user_tg_login


    def __str__(self):
        return f'Request: {self.id}, {self.name}, {self.number}, {self.email}, {self.user_tg_login}'


class God:
    def __init__(self, id=-1, god_chat_id=-1, god_tg_login=-1):
        self.id = id
        self.god_chat_id = god_chat_id
        self.god_tg_login = god_tg_login


    def __str__(self):
        return f'God: {self.id}, {self.god_chat_id}, {self.god_tg_login}'