import logging
from decouple import config

FINANCE_STATUS_URL = config("FINANCE_STATUS_URL")
ICS_LOCATION = config("ICS_LOCATION")
LHC_CHAT_ID = config("LHC_CHAT_ID")
TELEGRAM_API_TOKEN = config("TELEGRAM_API_TOKEN")
MONTASTIC_RSS_URL = config("MONTASTIC_RSS_URL")
STATUS_CHECK_INTERVAL = config("STATUS_CHECK_INTERVAL", default=30, cast=int)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")