from dataclasses import dataclass
from typing import Any, Sequence, Generator, Iterable, TypeVar

from autosar.extractor.base import Interval
from autosar.misc import HasRepr


class Conversion(HasRepr):
    pass


class ConstantConversion(Conversion):
    def __init__(
            self,
            constant: Any,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.constant = constant


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


@dataclass
class ConversionInterval(Interval):
    convertion: Conversion | None = None


class ScaledConversion(Conversion):
    @staticmethod
    def order_intervals(intervals: Iterable[ConversionInterval]) -> list[ConversionInterval] | None:
        sorted_by_start = sorted(intervals, key=lambda s: s.min)
        if len(sorted_by_start) == 0:
            return None
        current, *other = sorted_by_start
        result = [current]
        for iv in other:
            if iv in current:
                continue
            if iv > current:
                result.append(iv)
                current = iv
            else:
                result.append(ConversionInterval(
                    min=current.max,
                    max=iv.max,
                    convertion=iv.convertion,
                ))
                current = ConversionInterval.union(current, iv)
        return result


class NumericConversion(ScaledConversion):
    def __init__(
            self,
            numeric_intervals: Iterable[ConversionInterval],
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.numeric_intervals = self.order_intervals(numeric_intervals)
        if self.numeric_intervals is not None:
            # Iterate over neighboring intervals and fill gaps
            for iv1, iv2 in zip(self.numeric_intervals, self.numeric_intervals[1:]):
                mid_point = (iv1.max + iv2.min) / 2
                iv1.max = mid_point
                iv2.min - mid_point


class MapConversion(ScaledConversion):
    def __init__(
            self,
            map_intervals: Iterable[ConversionInterval],
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.map_intervals = self.order_intervals(map_intervals)


class NumericAndMapConversion(NumericConversion, MapConversion):
    pass


class BitfieldConversion(Conversion):
    def __init__(
            self,
            intervals: Iterable[tuple[int, ConversionInterval]],
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.mask_intervals: dict[int, list[ConversionInterval]] = {}
        for mask, iv in intervals:
            if mask not in self.mask_intervals:
                self.mask_intervals[mask] = []
            self.mask_intervals[mask].append(iv)


AnyConversion = TypeVar('AnyConversion', bound=Conversion)
