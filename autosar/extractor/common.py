from dataclasses import dataclass
from typing import TypeAlias

from autosar.data_transformation import TransformationTechnology
from autosar.signal import SystemSignal

Event: TypeAlias = tuple[SystemSignal, tuple[TransformationTechnology, ...], int]
SomeIpFeature: TypeAlias = tuple[int, int, int]


def get_type_by_range(min_value: int | float, max_value: int | float):
    range_mapper = {
        (0, 255): '>u1',
        (0, 65535): '>u2',
        (0, 4294967295): '>u4',
        (0, 18446744073709551615): '>u8',
        (-128, 127): '>i1',
        (-32768, 32767): '>i2',
        (-2147483648, 2147483647): '>i4',
        (-9223372036854775808, 9223372036854775807): '>i8',
    }
    for (mn, mx), dtype in range_mapper.items():
        if min_value >= mn and max_value <= mx:
            return dtype
    raise NotImplementedError


def get_max_value(dtype: str):
    if 'i' in dtype:
        r = 2
    elif 'u' in dtype:
        r = 1
    else:
        raise NotImplementedError
    type_bytes = int(dtype[-1])
    return 2 ** (8 * type_bytes) // r - 1


@dataclass
class DataType:
    name: str
    dtype: str


@dataclass
class ScalableDataType(DataType):  # IDENTICAL, LINEAR
    resolution: int | float


@dataclass
class EnumDataType(DataType):  # TEXTTABLE
    mapping: dict


@dataclass
class BitfieldDataType(DataType):  # BITFIELD_TEXTTABLE
    bit_description: dict[int, tuple[str, str]]


@dataclass
class Array(DataType):  # Special type for arrays
    dtype: DataType | dict[str, DataType]
    length: int | tuple[int, int]
