from dataclasses import dataclass
from typing import Self


class SystemElement:
    _instances: dict[str, 'SystemElement'] = {}

    def __new__(cls, identifier: str, *args, **kwargs):
        if (inst := cls._instances.get(identifier, None)) is not None:
            return inst
        inst = object.__new__(cls)
        cls._instances[identifier] = inst
        return inst

    def __init__(
            self,
            identifier: str,
            name: str,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._identifier = identifier
        self.name = name

    def __repr__(self):
        return f'{self.__class__.__name__}({self.name})'

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
