import datetime

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from joker.commands import calendar, finance, misc, pizza, status


def Joker(settings):
    app = ApplicationBuilder().token(settings.TELEGRAM_API_TOKEN).build()

    # Status
    app.add_handler(CommandHandler("quem", status.quem))
    app.add_handler(CommandHandler("status", status.status))
    app.add_handler(CommandHandler("status_infra", status.status_infra))
    app.job_queue.run_daily(status.recurring_status_infra, datetime.time(12, 0))

    # Finance commands
    app.add_handler(CommandHandler("grana", finance.grana))
    app.add_handler(CommandHandler("pix", finance.pix))
    app.job_queue.run_daily(
        finance.grana,
        datetime.time(15, 0),
        days=(
            1,
            3,
            5,
        ),
    )

    # Calendar commands
    app.job_queue.run_daily(calendar.pin_today_event, datetime.time(5, 0))
    app.add_handler(CommandHandler("quando", calendar.quando))

    # Miscellaneous commands
    app.add_handler(CommandHandler("batima", misc.batima))
    app.add_handler(CommandHandler("boom", misc.boom))
    app.add_handler(CommandHandler("quemsou", misc.quemsou))

    # Pizza
    app.add_handler(pizza.pizza_conversation_handler)

    # This handler must be the last included that catches all other commands
    app.add_handler(MessageHandler(filters.TEXT, misc.non_commands))

    return app
