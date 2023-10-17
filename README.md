# LHC Telegram bot

This is the bot that is running in the [Telegram channel](https://t.me/lhc_campinas) of
[*Laboratório Hacker de Campinas*](https://lhc.net.br), a hackerspace located in
[Campinas, SP, Brazil](https://www.openstreetmap.org/search?query=Laborat%C3%B3rio%20Hacker%20de%20Campinas#map=19/-22.91780/-47.05245).

## Development

### Local environment

We suggest the use of [pyenv](https://github.com/pyenv/pyenv) to manage your Python version and create an isolated
environment where you can safely develop. After installing it, you can prepare the environment using the following
commands:

```
$ pyenv virtualenv 3.11.5 myvenv
$ pyenv activate myvenv
$ python -m pip install -e .
```

Now you are ready to start development.

### Configuration

To run the bot, we need to provide some configuration info. These need to be defined as environment
variables.

These variables are required to run the bot:

- `LHC_CHAT_ID` - chat/channel ID. Follow [this](https://stackoverflow.com/questions/72640703/telegram-how-to-find-group-chat-id) to know how to get this value
- `TELEGRAM_API_TOKEN` - bot token. Use [this tutorial](https://core.telegram.org/bots/tutorial#obtain-your-bot-token) to obtain a bot token. We suggest you to create a personal token to be used for your development tasks.

These variables are optional, but the lack of them will make some commands not to work:

- `FINANCE_STATUS_URL` - API URL that returns a summary of financial status of hackerspace
- `ICS_LOCATION` - URL of hackerspace ICS calendar

### Running

After configuring the bot, you can run it using the following command:

```
$ python run.py
```
