from typing import Iterable

from autosar.extractor.base import SystemElement


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


class Ecu(SystemElement):
    pass


class CanFrame(SystemElement):
    def __init__(
            self,
            frame_id: int,
            pdu: str | None,
            providers: Iterable[str],
            consumers: Iterable[str],
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.frame_id = frame_id
        self.providers = tuple(map(Ecu.get, providers))
        self.consumers = tuple(map(Ecu.get, consumers))

    @property
    def sender(self) -> str:
        match self.providers:
            case 0: return 'UnknownECU'
            case 1: return self.providers[0].name
        return '_or_'.join(p.name for p in self.providers)

    @property
    def receiver(self) -> str:
        match self.consumers:
            case 0: return 'UnknownECU'
            case 1: return self.consumers[0].name
        return '_or_'.join(c.name for c in self.consumers)


class CanChannel(SystemElement):
    def __init__(
            self,
            frames: Iterable[str],
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.frames = tuple(map(CanFrame.get, frames))


class CanCluster(SystemElement):
    def __init__(
            self,
            channels: Iterable[str],
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.channels = tuple(map(..., channels))
