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

