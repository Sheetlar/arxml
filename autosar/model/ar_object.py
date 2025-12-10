from abc import ABC
from typing import TYPE_CHECKING, TypeVar, TypeAlias

from autosar.misc import HasLogger

if TYPE_CHECKING:
    from autosar.workspace import Workspace


class ArObject(HasLogger, ABC):
    """Base class for all Autosar objects"""
    _repr_exclude = ('parent', 'package_parser', 'package_writer')
    ref = None
    name = None

    def root_ws(self) -> 'Workspace':
        raise NotImplementedError

    def find(self, *_) -> 'MaybeArObject':
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


AnyArObject = TypeVar('AnyArObject', bound=ArObject)
MaybeArObject: TypeAlias = AnyArObject | None
