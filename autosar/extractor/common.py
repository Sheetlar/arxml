from dataclasses import dataclass
from typing import TypeAlias

from autosar.data_transformation import TransformationTechnology
from autosar.signal import SystemSignal

Event: TypeAlias = tuple[SystemSignal, tuple[TransformationTechnology, ...], int]
SomeIpFeature: TypeAlias = tuple[int, int, int]

dtype_mapper = {
    'BOOL': '>b',
    'FLOAT32': '>f4',
    'FLOAT64': '>f8',
    'INT8': '>i1',
    'INT16': '>i2',
    'INT32': '>i4',
    'INT64': '>i8',
    'UINT8': '>u1',
    'UINT16': '>u2',
    'UINT32': '>u4',
    'UINT64': '>u8',
}
range_mapper = {
    (0, 255): 'UINT8',
    (0, 65535): 'UINT16',
    (0, 4294967295): 'UINT32',
    (0, 18446744073709551615): 'UINT64',
    (-128, 127): 'INT8',
    (-32768, 32767): 'INT16',
    (-2147483648, 2147483647): 'INT32',
    (-9223372036854775808, 9223372036854775807): 'INT64',
}


def get_type_by_range(min_value: int | float, max_value: int | float):
    for (mn, mx), dtype in range_mapper.items():
        if min_value >= mn and max_value <= mx:
            return dtype_mapper[dtype]
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
class DataType:  # IDENTICAL
    name: str
    dtype: str


@dataclass
class ScalableDataType(DataType):
    resolution: int | float


@dataclass
class EnumDataType(DataType):  # TEXTTABLE
    mapping: dict


@dataclass
class BitfieldDataType(DataType):  # BITFIELD_TEXTTABLE
    bit_description: dict[int, tuple[str, str]]
