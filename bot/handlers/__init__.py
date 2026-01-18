from telegram.ext import CommandHandler, MessageHandler, filters

from .on_message import on_message
from .on_start import start
from .on_thread import on_new_thread

on_message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, on_message)
on_start_handler = CommandHandler("start", start)
on_new_thread_handler = CommandHandler("thread", on_new_thread)