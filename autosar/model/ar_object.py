from abc import ABC
from typing import TYPE_CHECKING, TypeVar, TypeAlias, Any

from autosar.misc import HasLogger, HasRepr

if TYPE_CHECKING:
    from autosar.workspace import Workspace


class ArObject(HasLogger, HasRepr, ABC):
    """Base class for all Autosar objects"""
    _blacklist = ('parent', 'package_parser', 'package_writer')
    ref = None
    name = None

    def root_ws(self) -> 'Workspace':
        raise NotImplementedError

    def find(self, *_) -> 'MaybeArObject':
        raise NotImplementedError

    def _repr_filter(self, attr_name: str, attr_value: Any) -> bool:
        return super()._repr_filter(attr_name, attr_value) and not isinstance(attr_value, (list, dict, tuple))


AnyArObject = TypeVar('AnyArObject', bound=ArObject)
MaybeArObject: TypeAlias = AnyArObject | None
