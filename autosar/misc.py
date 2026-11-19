import logging
import sys
from abc import ABC
from enum import StrEnum
from typing import Iterable, Any, Mapping, TypeVar, Sequence, Collection

Tk = TypeVar('Tk')
Tv = TypeVar('Tv')


class HasRepr(ABC):
    _blacklist = ()

    def _repr_name_filter(self, attr_name: str) -> bool:
        """
        :param attr_name: Attribute name
        :return: True if th given attribute should be displayed in repr, False otherwise
        """
        return not attr_name.startswith('_') and attr_name not in self._blacklist

    # noinspection method-may-be-static,unused-parameter
    def _repr_value_filter(self, attr_value: Any) -> bool:
        """
        :param attr_value: Value of the attribute
        :return: True if th given attribute should be displayed in repr, False otherwise
        """
        return True

    def _repr_value_format(self, attr_value: Any) -> str:
        """
        :param attr_value: Value of the attribute
        :return: Value to be displayed
        """
        return repr(attr_value)

    def _repr_params_str(self, params: dict[str, Any]) -> str:
        return ', '.join(f'{name}={self._repr_value_format(value)}' for name, value in params.items())

    def __repr__(self):
        params = self._repr_params_str({
            name: attr
            for name in dir(self)
            if self._repr_name_filter(name)
            if not callable(attr := getattr(self, name))
            if self._repr_value_filter(attr)
        })
        return f'{self.__class__.__name__}({params})'


class HasLogger(ABC):
    def __init__(self, *args, **kwargs):
        self._logger = logging.getLogger(name=self.__class__.__name__)
        super().__init__(*args, **kwargs)


def setup_logger(
        level: int = logging.DEBUG,
        verbose: bool = True,
        whitelist: str | Sequence[str] | None = None,
        blacklist: str | Sequence[str] | None = None,
):
    if not verbose:
        level = logging.CRITICAL
    formatter = logging.Formatter('[%(asctime)s] - [%(name)s] - [%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    stdout_handler.addFilter(
        CustomFilter(
            {
                logging.DEBUG,
                logging.INFO,
            },
            name_whitelist=whitelist,
            name_blacklist=blacklist,
        )
    )
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(formatter)
    stderr_handler.addFilter(
        CustomFilter(
            {
                logging.WARNING,
                logging.ERROR,
                logging.CRITICAL,
            },
            name_whitelist=whitelist,
            name_blacklist=blacklist,
        )
    )
    logging.basicConfig(
        handlers=(
            stdout_handler,
            stderr_handler,
        ),
        level=level,
    )


class CustomFilter(logging.Filter):
    def __init__(
            self,
            levels: int | Collection[int],
            name_whitelist: str | Sequence[str] | None = None,
            name_blacklist: str | Sequence[str] | None = None,
    ):
        super().__init__()
        if isinstance(levels, int):
            levels = {levels}
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


def not_none(value: Any) -> bool:
    return value is not None


def filter_none(vals: Iterable[Any | None]) -> Iterable[Any]:
    return (v for v in vals if v is not None)


def dict_sorted_by_keys(
        mapping: Mapping[Tk, Tv] | Iterable[tuple[Tk, Tv]],
) -> dict[Tk, Tv]:
    if isinstance(mapping, Mapping):
        mapping = mapping.items()
    return dict(sorted(mapping, key=lambda i: i[0]))


class RawStrEnum(StrEnum):
    """
    Same to StrEnum, but auto() values are not lower-cased
    """

    # noinspection PyMethodParameters
    def _generate_next_value_(name, start, count, last_values):
        return name


class NoAttr:
    pass


class Skip:
    pass
