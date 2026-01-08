import json
import logging
from typing import Dict

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from config import settings
from db import ApplicationRepository
from yonote_client import create_document


logging.basicConfig(
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

ASKING = 1
JOB_SELECTION = 2

SURVEY = [
    ("full_name", " Как к Вам обращаться? [пример: Star123] (ник, имя, прозвищe)"),
    ("age", "Сколько Вам полных лет? [пример: 18]"),
    ("job", "На какую должность претендуете? (по нажатию кнопки)"),
    ("experience", "Стаж в направлении. [пример: 2 дня/месяца/года/жизни]"),
    ("portfolio", "Ссылки на ваши работы [пример: мой гит http://github.com/vladmir0512 , мой работы http://example.com/ ]"),
    ("goals", "Цель вступления в проект? Кратко. [пример: я вокалист и хочу научиться работать в команде]"),
]

WELCOME_TEXT = (
    "Привет! Я бот подачи заявок в наше комьюнити. Ответьте, пожалуйста, на несколько вопросов."
)
SUCCESS_TEXT = (
    "Спасибо! Мы получили вашу анкету. Администратор свяжется с вами после проверки."
)
APPROVE_TEMPLATE = (
    "Привет, {name}! Ваша заявка одобрена 🎉\n"
    "Ожидайте, в ближайшее время с Вами свяжутся администраторы.\n"
    "Проверьте, что у Вас не закрыты личные сообщения!\n"
    "До встречи!"
)
DECLINE_TEMPLATE = (
    "Привет, {name}! Спасибо за интерес, но сейчас мы не можем принять Вашу заявку. "
    "Можете подать её повторно позже."
)

MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["/start", "/cancel", "/status"],
        ["/admin"],
    ],
    resize_keyboard=True,
)

repo = ApplicationRepository(settings.database_path)


def is_admin(user_id: int) -> bool:
    return user_id in settings.admin_ids


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    last_application = repo.get_last_for_user(user.id)
    if last_application:
        status = last_application["status"]
        if status == "approved":
            invite = settings.community_invite_link or "Ссылка на вступление уже была отправлена."
            await update.message.reply_text(
                "Ваша предыдущая заявка уже одобрена. Вот актуальная ссылка:\n"
                f"{invite}",
                reply_markup=MAIN_KEYBOARD,
            )
            return ConversationHandler.END
        if status == "pending":
            await update.message.reply_text(
                "Ваша заявка всё ещё рассматривается. Дождитесь решения администратора.",
                reply_markup=MAIN_KEYBOARD,
            )
            return ConversationHandler.END
    context.user_data["survey_step"] = 0
    context.user_data["answers"] = {}
    await update.message.reply_text(WELCOME_TEXT, reply_markup=MAIN_KEYBOARD)
    await update.message.reply_text(SURVEY[0][1])
    logger.info("Начат опрос пользователем %s", user.id)
    return ASKING


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    if text.lower() in ("/cancel", "cancel", "отмена"):
        return await cancel(update, context)
    idx = context.user_data.get("survey_step", 0)
    answers: Dict[str, str] = context.user_data.get("answers", {})
    field, _ = SURVEY[idx]
    answers[field] = text
    context.user_data["answers"] = answers
    idx += 1
    if idx >= len(SURVEY):
        user = update.effective_user
        chat = update.effective_chat
        application_id = repo.save_application(
            user_id=user.id,
            chat_id=chat.id,
            username=user.username,
            full_name=answers.get("full_name") or user.full_name,
            answers=answers,
        )
        await update.message.reply_text(SUCCESS_TEXT)
        logger.info("Сохранена заявка %s от пользователя %s", application_id, user.id)
        return ConversationHandler.END
    context.user_data["survey_step"] = idx
    if idx == 2:  # job selection
        jobs = ["Вокалист", "Переводчик", "Звукарь", "Видер", "Художник", "Программист", "Менеджер"]
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(job, callback_data=f"job:{job}") for job in jobs[i:i+3]]
            for i in range(0, len(jobs), 3)
        ])
        await update.message.reply_text(SURVEY[idx][1], reply_markup=keyboard)
        return JOB_SELECTION
    await update.message.reply_text(SURVEY[idx][1])
    return ASKING


async def handle_job_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    choice = query.data.split(":", 1)[1]
    idx = context.user_data.get("survey_step", 2)
    answers: Dict[str, str] = context.user_data.get("answers", {})
    field, _ = SURVEY[idx]
    answers[field] = choice
    context.user_data["answers"] = answers
    idx += 1
    if idx >= len(SURVEY):
        user = query.from_user
        chat = query.message.chat
        application_id = repo.save_application(
            user_id=user.id,
            chat_id=chat.id,
            username=user.username,
            full_name=answers.get("full_name") or user.full_name,
            answers=answers,
        )
        await query.edit_message_text(SUCCESS_TEXT)
        logger.info("Сохранена заявка %s от пользователя %s", application_id, user.id)
        return ConversationHandler.END
    context.user_data["survey_step"] = idx
    await query.edit_message_text(SURVEY[idx][1])
    return ASKING


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Опрос остановлен. Вы можете начать заново с командой /start.",
        reply_markup=MAIN_KEYBOARD,
    )
    context.user_data.clear()
    return ConversationHandler.END


def format_application(row) -> str:
    answers = json.loads(row["answers_json"])
    details = "\n".join(f"{key}: {value}" for key, value in answers.items())
    return (
        f"Заявка #{row['id']}\n"
        f"User ID: {row['user_id']}\n"
        f"Username: @{row['username'] or '—'}\n"
        f"Имя: {row['full_name'] or '—'}\n"
        f"Статус: {row['status']}\n\n{details}"
    )


def format_history(user_id: int, limit: int = 5) -> str:
    history = repo.list_by_user(user_id)[:limit]
    if not history:
        return "История отсутствует."
    parts = []
    for item in history:
        parts.append(f"#{item['id']} — {item['status']} ({item['created_at']})")
    return "\n".join(parts)


def build_admin_keyboard(app_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Принять ✅", callback_data=f"approve:{app_id}"),
                InlineKeyboardButton("Отклонить ❌", callback_data=f"decline:{app_id}"),
            ]
        ]
    )


async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not is_admin(user.id):
        await update.message.reply_text("У вас нет доступа.")
        return
    pending = repo.list_pending(limit=10)
    if not pending:
        await update.message.reply_text("Нет заявок на рассмотрение.")
        return
    for row in pending:
        history_text = format_history(row["user_id"])
        await update.message.reply_text(
            f"{format_application(row)}\n\nИстория заявок:\n{history_text}",
            reply_markup=build_admin_keyboard(row["id"]),
        )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    row = repo.get_last_for_user(user.id)
    if not row:
        await update.message.reply_text("Заявок не найдено. Используйте /start, чтобы подать её.")
        return
    await update.message.reply_text(f"Текущий статус вашей заявки: {row['status']}.")


async def handle_admin_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        await query.edit_message_text("Нет доступа.")
        return
    try:
        action, raw_id = query.data.split(":")
        app_id = int(raw_id)
    except ValueError:
        await query.edit_message_text("Некорректные данные.")
        return
    row = repo.get_by_id(app_id)
    if not row:
        await query.edit_message_text("Заявка не найдена.")
        return
    if row["status"] != "pending":
        await query.edit_message_text("Заявка уже обработана.")
        return
    if action == "approve":
        await process_approval(row, query, context)
    elif action == "decline":
        await process_decline(row, query, context)
    else:
        await query.edit_message_text("Неизвестное действие.")


async def process_approval(row, query, context: ContextTypes.DEFAULT_TYPE) -> None:
    synced_flag = row["synced_to_yonote"] if "synced_to_yonote" in row.keys() else 0
    if synced_flag:
        await query.edit_message_text(f"{format_application(row)}\n\n✅ Уже выгружено.")
        return

    repo.update_status(row["id"], "approved")
    answers = json.loads(row["answers_json"])
    full_name = row["full_name"] or ""
    telegram_id = row["user_id"]
    age = answers.get("age", "")
    experience = answers.get("experience", "")  # Стаж
    portfolio = answers.get("portfolio", "")  # Ссылки
    goals = answers.get("goals", "")
    job = answers.get("job", "")  # Должность

    title = f"Заявка от {job}а"
    doc = create_document(full_name, age, job, experience, portfolio, goals, title)
    synced = doc is not None
    if synced:
        repo.mark_synced(row["id"])

    text = APPROVE_TEMPLATE.format(name=row["full_name"] or "друг")
    await notify_user(row["chat_id"], text, context)

    status_note = "✅ Одобрено и документ создан." if synced else "✅ Одобрено, но создание документа не удалось."
    history_text = format_history(row["user_id"])
    await query.edit_message_text(
        f"{format_application(row)}\n\n{status_note}\n\nИстория заявок:\n{history_text}"
    )


async def process_decline(row, query, context: ContextTypes.DEFAULT_TYPE) -> None:
    repo.update_status(row["id"], "declined")
    text = DECLINE_TEMPLATE.format(name=row["full_name"] or "друг")
    await notify_user(row["chat_id"], text, context)
    history_text = format_history(row["user_id"])
    await query.edit_message_text(
        f"{format_application(row)}\n\n❌ Отклонено.\n\nИстория заявок:\n{history_text}"
    )


async def notify_user(chat_id: int, text: str, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        await context.bot.send_message(chat_id=chat_id, text=text)
    except Exception as exc:  # pragma: no cover - сетевые ошибки
        logger.error("Не удалось отправить сообщение пользователю %s: %s", chat_id, exc)


def build_application() -> Application:
    settings.validate()
    application = Application.builder().token(settings.bot_token).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASKING: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer),
                CommandHandler("cancel", cancel),
            ],
            JOB_SELECTION: [
                CallbackQueryHandler(handle_job_selection, pattern=r"^job:"),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )
    application.add_handler(conv)
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("admin", admin_panel))
    application.add_handler(CommandHandler("cancel", cancel))
    application.add_handler(CallbackQueryHandler(handle_admin_action, pattern=r"^(approve|decline):"))
    return application


def main() -> None:
    app = build_application()
    logger.info("Бот запущен.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()