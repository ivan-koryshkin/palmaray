import logging

import attrs
from settings import settings
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler

import bot.handlers as handlers


@attrs.frozen(slots=True, frozen=True)
class RunBot:
    logger: logging.Logger
    message_handler: MessageHandler
    command_handlers: list[CommandHandler]
    callback_query_handlers: list[CallbackQueryHandler]

    def __call__(self):
        application = Application.builder().token(settings.TG_TOKEN).build()
        application.add_handler(self.message_handler)
        for command_handler in self.command_handlers:
            application.add_handler(command_handler)
        for cb in self.callback_query_handlers:
            application.add_handler(cb)
        application.run_polling(allowed_updates=Update.ALL_TYPES)
