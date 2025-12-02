from typing import TypeVar, Sequence, Generator, NamedTuple, Self

from autosar.extractor.base import SystemElement


class DataType(SystemElement):
    def __init__(
            self,
            declaration: str | None,
            size: int,
            encoding: str,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.declaration = declaration
        self.size = size
        self.encoding = encoding


class Conversion:
    pass


class LinearConversion(Conversion):
    def __init__(
            self,
            a: int | float,
            b: int | float,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.a = a
        self.b = b

    def __iter__(self):
        yield self.a
        yield self.b


class RationalConversion(Conversion):
    def __init__(
            self,
            numerator_coeffs: Sequence[int | float],
            denominator_coeffs: Sequence[int | float],
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.numerator_coeffs = tuple(reversed(numerator_coeffs))
        self.denominator_coeffs = tuple(reversed(denominator_coeffs))
        self.numerator_order = len(numerator_coeffs) - 1
        self.denominator_order = len(denominator_coeffs) - 1

    @property
    def numerator(self) -> Generator[tuple[int | float, int], None, None]:
        for n, c in enumerate(self.numerator_coeffs):
            yield c, self.numerator_order - n

    @property
    def denominator(self) -> Generator[tuple[int | float, int], None, None]:
        for n, c in enumerate(self.denominator_coeffs):
            yield c, self.denominator_order - n


class ScaledConversion(Conversion):
    ...


class Interval(NamedTuple):
    min: int | float
    max: int | float
    convertion: Conversion

    def __contains__(self, item: int | float | Self) -> bool:
        if isinstance(item, Interval):
            return item.min >= self.min and item.max <= self.max
        return self.min <= item <= self.max

    def __lt__(self, other: Self) -> bool:
        return other.max < self.min

    def __gt__(self, other: Self) -> bool:
        return other.min > self.max


class NumericConversion(ScaledConversion):
    def __init__(
            self,
            nigger: Sequence[Interval],
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        first_pass_sort = sorted(nigger, key=lambda s: s.min)
        intervals = sorted(first_pass_sort, key=lambda s: s.max - s.min, reverse=True)


class NumericAndTextConversion(ScaledConversion):
    ...


AnyConversion = TypeVar('AnyConversion', bound=Conversion)
