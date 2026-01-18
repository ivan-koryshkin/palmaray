import logging

from bot.bot import RunBot
from bot.handlers import on_start_handler
from bot.handlers import on_message_handler
from bot.handlers import on_new_thread_handler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


def main() -> None:
    run_bot = RunBot(
        logger=logger,
        command_handlers=[
            on_start_handler,
            on_new_thread_handler
        ],
        message_handler=on_message_handler
    )
    run_bot()


if __name__ == "__main__":
    main()