import logging
import sys
from abc import ABC
from typing import Iterable


class HasLogger(ABC):
    def __init__(self, *args, **kwargs):
        self._logger = logging.getLogger(name=self.__class__.__name__)
        super().__init__(*args, **kwargs)


def setup_logger(
        level: int = logging.DEBUG,
        verbose: bool = True,
        whitelist: str | Iterable[str] | None = None,
        blacklist: str | Iterable[str] | None = None,
):
    if not verbose:
        level = logging.CRITICAL
    formatter = logging.Formatter('[%(asctime)s] - [%(name)s] - [%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    stdout_handler.addFilter(
        CustomFilter(
            [
                logging.DEBUG,
                logging.INFO,
            ],
            name_whitelist=whitelist,
            name_blacklist=blacklist,
        )
    )
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(formatter)
    stderr_handler.addFilter(
        CustomFilter(
            [
                logging.WARNING,
                logging.ERROR,
                logging.CRITICAL,
            ],
            name_whitelist=whitelist,
            name_blacklist=blacklist,
        )
    )
    logging.basicConfig(
        handlers=[
            stdout_handler,
            stderr_handler,
        ],
        level=level,
    )


class CustomFilter(logging.Filter):
    def __init__(
            self,
            levels: int | Iterable[int],
            name_whitelist: str | Iterable[str] | None = None,
            name_blacklist: str | Iterable[str] | None = None,
    ):
        super().__init__()
        if isinstance(levels, int):
            levels = [levels]
        if isinstance(name_whitelist, str):
            name_whitelist = [name_whitelist]
        if isinstance(name_blacklist, str):
            name_blacklist = [name_blacklist]
        self.levels = levels
        self.name_whitelist = name_whitelist
        self.name_blacklist = name_blacklist

    def _drop_blacklisted(self, record: logging.LogRecord) -> bool:
        if self.name_blacklist is None:
            return False
        for name in self.name_blacklist:
            if name in record.name:
                return True
        return False

    def _pass_whitelisted(self, record: logging.LogRecord) -> bool:
        if self.name_whitelist is None:
            return True
        for name in self.name_whitelist:
            if name in record.name:
                return True
        return False

    def filter(self, record: logging.LogRecord) -> bool:
        if self._drop_blacklisted(record):
            return False
        if not self._pass_whitelisted(record):
            return False
        return record.levelno in self.levels
