from autosar.extractor.base import SystemElement
from autosar.extractor.conversion import AnyConversion, LinearConversion
from autosar.misc import HasRepr


class Unit(HasRepr):
    def __init__(
            self,
            symbol: str = '-',
            unit_factor: int | float | None = None,
            unit_offset: int | float | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.symbol = symbol
        if unit_factor is not None and unit_offset is not None:
            conversion = LinearConversion(unit_factor, unit_offset)
        else:
            conversion = None
        self.conversion = conversion


class DataType(HasRepr):
    def __init__(
            self,
            name: str,
            declaration: str | None,
            size: int,
            encoding: str,
            is_array: bool,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.name = name
        self.declaration = declaration
        self.size = size
        self.encoding = encoding
        self.is_array = is_array


class Signal(SystemElement):
    _repr_attrs = ('bit_length',)

    def __init__(
            self,
            bit_length: int,
            dtype: DataType | None = None,
            conversion: AnyConversion | None = None,
            unit: Unit | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.bit_length = bit_length
        self.dtype = dtype
        self.conversion = conversion
        self.unit = unit or Unit()
