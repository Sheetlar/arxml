from typing import TypeVar, Generic, Iterable

from autosar.model.ar_object import ArObject

T = TypeVar('T', bound=ArObject)


class Variants(Generic[T]):
    def __init__(self, variants: Iterable[T], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._variants = tuple(variants)

    def __len__(self):
        return len(self._variants)

    def __iter__(self):
        return iter(self._variants)

    def __getitem__(self, item) -> T:
        return self._variants[item]

    @property
    def variants(self) -> tuple[T, ...]:
        return self._variants

    @property
    def single(self) -> T | None:
        if len(self._variants) != 1:
            return None
        return self._variants[0]
