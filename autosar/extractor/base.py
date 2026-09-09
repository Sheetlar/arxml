from dataclasses import dataclass
from typing import Self, Iterable

from autosar.misc import NoAttr


class SystemElement:
    _instances: dict[str, 'SystemElement'] = {}
    _repr_attrs: Iterable[str] | None = None

    def __new__(cls, identifier: str, *args, alias: str | None = None, **kwargs):
        if (inst := cls._instances.get(identifier, None)) is not None:
            return inst
        inst = object.__new__(cls)
        cls._instances[identifier] = inst
        if alias is not None and alias not in cls._instances:
            cls._instances[alias] = inst
        return inst

    def __init__(
            self,
            identifier: str,
            name: str,
            *args,
            alias: str | None = None,
            **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._identifier = identifier
        self._alias = alias
        self.name = name

    def __repr__(self):
        return f'{self.__class__.__name__}(name={self.name!r}{self._attrs_str()})'

    def _attrs_str(self) -> str:
        if self._repr_attrs is None:
            return ''
        attrs = ', '.join(
            f'{x}={v!r}' for x in self._repr_attrs
            if (v := getattr(self, x, NoAttr)) is not NoAttr
        )
        if not attrs:
            return ''
        return f', {attrs}'

    @classmethod
    def get(cls, identifier: str) -> 'SystemElement':
        return cls._instances[identifier]


@dataclass
class Interval:
    min: int | float
    max: int | float

    def __contains__(self, item: int | float | Self) -> bool:
        if isinstance(item, Interval):
            return item.min >= self.min and item.max <= self.max
        return self.min <= item <= self.max

    def __lt__(self, other: Self) -> bool:
        return other.min > self.max

    def __le__(self, other: Self) -> bool:
        return self.min <= other.min <= self.max < other.max

    def __eq__(self, other: Self) -> bool:
        return other.min == self.min and other.max == self.max

    def __ne__(self, other: Self) -> bool:
        return not self.__eq__(other)

    def __ge__(self, other: Self) -> bool:
        return other.min < self.min <= other.max <= self.max

    def __gt__(self, other: Self) -> bool:
        return other.max < self.min

    @classmethod
    def union(cls, i1: Self, i2: Self) -> Self:
        if i1 <= i2:
            return cls(i1.min, i2.max)
        elif i1 >= i2:
            return cls(i2.min, i1.max)
        else:
            raise ValueError('Cannot concatenate disjoint intervals')


class DescriptiveInteger(int):
    def __repr__(self):
        return f'{self.__class__.__name__}({self})'
