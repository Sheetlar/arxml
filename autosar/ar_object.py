from abc import ABC
from typing import Iterable, Mapping

from autosar.has_logger import HasLogger


class ArObject(HasLogger, ABC):
    """Base class for all Autosar objects"""
    _repr_exclude = ('parent', 'package_parser', 'package_writer')
    ref = None
    name = None

    def root_ws(self):
        return NotImplementedError

    def find(self, *_):
        raise NotImplementedError

    def __repr__(self):
        params_str = ', '.join(
            f'{n}={v!r}'
            for n, v in vars(self).items()
            if not callable(v)
            and not n.startswith('_')
            and n not in self._repr_exclude
            and not isinstance(v, (list, dict, tuple))
        )
        return f'{self.__class__.__name__}({params_str})'
