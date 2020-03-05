import requests


def progress_bar(current, maximum):
    width = 20
    painted = int(width * current / maximum)
    not_painted = width - painted
    bar = "\U00002588" * painted + "\U00002591" * not_painted
    return bar


def grana(update, context):
    response = requests.get("http://beta.lhc.rennerocha.com/status")
    status = response.json()

    incomes = float(status["actual_incomes"])

    actual_expenses = float(status["actual_expenses"])
    expenses_estimate = float(status["regular_expenses_estimate"])
    expenses = actual_expenses + expenses_estimate

    bar = progress_bar(incomes, expenses)

    if incomes > expenses:
        msg = f"Temos fluxo positivo de caixa esse mês! \U0001F389 Recebemos R${incomes} de R${expenses}"
    else:
        msg = f"Este mês recebemos R${incomes} de R${expenses} \U0001F4B8.\n\n{bar}\n\nAjude a fechar as contas do mês [fazendo uma doação via PayPal](http://bit.ly/doe-para-o-lhc) \U0001F4B5."

    context.bot.send_message(
        update.message.chat_id, text=msg, parse_mode="Markdown",
    )
