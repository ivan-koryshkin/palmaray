from telegram.ext import CommandHandler, MessageHandler, filters

from .on_message import on_message
from .on_start import start
from .on_thread import on_new_thread
from .on_llm_list import on_llm_list
from .on_callback_query import on_callback_query
from .on_info import on_info
from telegram.ext import CallbackQueryHandler


on_message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, on_message)
on_start_handler = CommandHandler("start", start)
on_new_thread_handler = CommandHandler("thread", on_new_thread)
on_llm_list_handler = CommandHandler("llm_list", on_llm_list)
on_llm_set_query_handler = CallbackQueryHandler(on_callback_query)
on_info_handler = CommandHandler("info", on_info)