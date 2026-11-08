import weakref
from abc import ABC
from typing import TYPE_CHECKING, TypeVar, TypeAlias, Any, Iterable

from autosar.misc import HasLogger, HasRepr

if TYPE_CHECKING:
    from autosar.workspace import Workspace
    from autosar.top_level import Autosar

T = TypeVar('T')


class ArObject(HasLogger, HasRepr, ABC):
    """Base class for all Autosar objects"""
    _blacklist = ('root', 'parent', 'namespace', 'package_parser', 'package_writer')
    ref: str | None = None
    name: str | None = None
    _parent: weakref.ref['ArObject'] | None = None

    @property
    def parent(self) -> 'AnyArObject':
        if self._parent is None:
            raise TypeError('Parent is not set')
        if (parent := self._parent()) is None:
            raise ReferenceError('Parent is not dead')
        return parent

    @parent.setter
    def parent(self, new_parent: 'MaybeArObject'):
        if new_parent is None:
            self._parent = None
            return
        self._parent = weakref.ref(new_parent)  # type: ignore

    def root_ws(self) -> 'Workspace | Autosar':
        raise NotImplementedError

    @property
    def root(self) -> 'Autosar':
        return self.parent.root

    @property
    def namespace(self) -> str:
        return self.parent.namespace

    def find(self, ref: str | None) -> 'MaybeArObject':
        if ref is None:
            return None
        if ref == '':
            return self
        if ref.startswith('/'):
            return self.root.find(ref)
        top_ref, _, child_ref = ref.partition('/')
        for child in self._findable_children:
            if child.name == top_ref:
                if child_ref == '':
                    return child
                return child.find(child_ref)
        return None

    @property
    def _findable_children(self) -> Iterable['ArObject']:
        yield from ()  # I hate this

    @staticmethod
    def eval_children(children: Iterable[T] | None) -> list[T]:
        if children is None:
            return []
        if not isinstance(children, list):
            children = list(children)
        return children

    def _set_parent(self, children: Iterable[T] | None, parent: 'MaybeArObject' = None) -> list[T]:
        children = self.eval_children(children)
        if parent is None:
            parent = self
        for sub_element in children:
            sub_element.parent = parent
        return children

    def _repr_value_format(self, attr_value: Any) -> str:
        if isinstance(attr_value, (list, dict, tuple)):
            return f'{{{attr_value.__class__.__name__}: {len(attr_value)}}}'
        return super()._repr_value_format(attr_value)


AnyArObject = TypeVar('AnyArObject', bound=ArObject)
MaybeArObject: TypeAlias = AnyArObject | None


class ArObjectWithParent(ArObject):
    def __init__(
            self,
            parent: MaybeArObject = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.parent = parent
