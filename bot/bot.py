import logging

import attrs
from settings import settings
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler


@attrs.frozen(slots=True, frozen=True)
class RunBot:
    logger: logging.Logger
    message_handler: MessageHandler
    command_handlers: list[CommandHandler]

    def __call__(self):
        application = Application.builder().token(settings.TG_TOKEN).build()
        application.add_handler(self.message_handler)
        for command_handler in self.command_handlers:
            application.add_handler(command_handler)
        application.run_polling(allowed_updates=Update.ALL_TYPES)
