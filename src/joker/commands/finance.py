from importlib import resources

import httpx

from joker import settings


def progress_bar(current, maximum):
    width = 20
    painted = int(width * current / maximum)
    not_painted = width - painted
    bar = "\U00002588" * painted + "\U00002591" * not_painted
    return bar


async def pix(update, context):
    qr_code_pix = resources.files("joker") / "assets/qr-code-pix.jpg"
    with open(qr_code_pix, "rb") as qr_code:
        await context.bot.send_photo(
            update.message.chat_id,
            qr_code,
            caption="Contribua com PIX!\nChave: batman@lhc.net.br",
        )


def _get_grana():
    response = httpx.get(settings.FINANCE_STATUS_URL)
    status = response.json()

    incomes = float(status["actual_incomes"])

    actual_expenses = float(status["actual_expenses"])
    expenses_estimate = float(status["regular_expenses_estimate"])
    expenses = actual_expenses + expenses_estimate

    bar = progress_bar(incomes, expenses)

    if incomes > expenses:
        msg = f"Temos fluxo de caixa positivo esse mês! \U0001F389 Recebemos doações suficientes para pagar os R${expenses:.2f} de despesas previstas para o mês!\n\nMas você pode melhorar ainda mais essa marca para fazermos mais investimentos para melhorar o hackerspace [fazendo uma doação via PayPal](http://bit.ly/doe-para-o-lhc) ou via Pix em batman@lhc.net.br \U0001F4B5."
    else:
        msg = f"Este mês recebemos R${incomes:.2f} de R${expenses:.2f} \U0001F4B8.\n\n{bar}\n\nAjude a fechar as contas do mês [fazendo uma doação via PayPal](http://bit.ly/doe-para-o-lhc) ou via Pix em batman@lhc.net.br \U0001F4B5."

    return msg


async def grana(update, context):
    await context.bot.send_message(
        update.message.chat_id,
        text=_get_grana(),
        parse_mode="Markdown",
    )


async def recurring_grana(context):
    await context.bot.send_message(
        settings.LHC_CHAT_ID,
        text=_get_grana(),
        parse_mode="Markdown",
    )
