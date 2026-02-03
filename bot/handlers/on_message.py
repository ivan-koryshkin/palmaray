from telegram import Update
from telegram.ext import ContextTypes
from broker.tasks.create_message_history import task_create_message_history
from broker.tasks.message import task_response_to_user


async def _get_image_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str | None:
    if not update.message or not update.message.photo:
        return None

    try:
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)

        return file.file_path
    except Exception as e:
        print(f"Error getting image: {e}")
        return None


async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    image_url = await _get_image_url(update, context)

    if not update.message.text and not image_url:
        return

    if not update.message.from_user:
        return

    task = await task_response_to_user.kiq(
        update.message.from_user.id,
        update.message.chat_id,
        update.message.message_thread_id or 0,
        update.message.text or "",
        str(update.message.id),
        image_url,
    )
    result = await task.wait_result()
    await task_create_message_history.kiq(result.return_value)
