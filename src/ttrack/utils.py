from datetime import date
from urllib.parse import quote

from dateutil.parser import parse


def str_date_to_quote(incoming: str) -> str:
    return date_to_quote(parse(incoming))


def date_to_quote(incoming: date):
    return quote(incoming.strftime("%Y-%m-%dT%H:%M:%S+06:00"))
