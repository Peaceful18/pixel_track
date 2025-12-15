import re
from enum import Enum


class LogPattern(Enum):
    HTTP = (
        "http",
        re.compile(
            r"(?P<method>GET|POST|PUT|DELETE|PATCH)\s+"
            r"(?P<path>\S+)\s+"
            r"(?P<status>\d{3})\s+"
            r"(?P<duration_ms>\d+)ms"
        ),
    )
    SQL = (
        "sql",
        re.compile(
            r"(?P<operation>SELECT|INSERT|UPDATE|DELETE)"
            r".+FROM\s+(?P<table>\S+)"
            r".+took\s+(?P<duration_ms>\d+)ms",
            re.IGNORECASE,
        ),
    )

    def __init__(self, key: str, pattern):
        self.key = key
        self.pattern = pattern

    @classmethod
    def get_pattern(cls, key: str):
        """
        Повертає патерн за ключем
        """
        for item in cls:
            if item.key == key:
                return item.pattern
        return None


def parse_log(log_string: str, event_type: str) -> dict:
    parse_pattern = LogPattern.get_pattern(event_type)
    if parse_pattern:
        match = parse_pattern.search(log_string)
        if match:
            return match.groupdict()
    return {}


# def parse_sql_log(log_string: str) -> dict:
#     match = re.match(SQL_PATTERN, log_string)
#     if match:
#         return match.groupdict()
#     return {}
