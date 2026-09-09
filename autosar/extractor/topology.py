from typing import Iterable

from autosar.extractor.base import SystemElement
from autosar.extractor.transport import Pdu


class Ecu(SystemElement):
    pass


class CanFrame(SystemElement):
    def __init__(
            self,
            frame_id: int,
            size: int,
            pdu: Pdu | None,
            providers: Iterable[str],
            consumers: Iterable[str],
            extended_addressing: bool,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.frame_id = frame_id
        self.size = size
        self.pdu = pdu
        self.providers = tuple(map(Ecu.get, providers))
        self.consumers = tuple(map(Ecu.get, consumers))
        self.extended_addressing = extended_addressing

    @property
    def sender(self) -> str:
        match len(self.providers):
            case 0: return 'UnknownECU'
            case 1: return self.providers[0].name
        return '_or_'.join(p.name for p in self.providers)

    @property
    def receiver(self) -> str:
        match len(self.consumers):
            case 0: return 'UnknownECU'
            case 1: return self.consumers[0].name
        return '_or_'.join(c.name for c in self.consumers)


class CanCluster(SystemElement):
    def __init__(
            self,
            frames: Iterable[CanFrame],
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.frames = tuple(frames)
