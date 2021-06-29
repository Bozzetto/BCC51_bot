import telebot, threading, datetime
import mariadb as mdb


class Bot(TeleBot):
    def __init__(self,token):
        self.bot = telebot.TeleBot(token)
