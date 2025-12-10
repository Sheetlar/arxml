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


class Signal(SystemElement):
    def __init__(
            self,
            bit_length: int,
            np_dtype: str,
            compu: str | None = None,
            unit: str | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.bit_length = bit_length
        self.np_dtype = np_dtype
        self.compu = compu
        self.unit = unit
