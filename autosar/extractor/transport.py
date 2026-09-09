from typing import Mapping, Iterable, TypeVar, TypeAlias, NamedTuple, Literal

from autosar.extractor.base import SystemElement, DescriptiveInteger
from autosar.extractor.conversion import AnyConversion
from autosar.extractor.data import Signal, DataType


class LongHeaderId(DescriptiveInteger):
    pass


class ShortHeaderId(DescriptiveInteger):
    pass


class OffsetInContainer(DescriptiveInteger):
    pass


ItemId = TypeVar('ItemId', LongHeaderId, ShortHeaderId, OffsetInContainer)
ByteOrder: TypeAlias = Literal['>', '<']
Position: TypeAlias = tuple[int, int]


class PduSignal(NamedTuple):
    name: str
    bit_length: int
    bit_offset: int
    byte_span: tuple[int, int]
    packing: ByteOrder
    data_type: DataType
    conversion: AnyConversion


class PduItem(NamedTuple):
    signal: Signal
    packing: ByteOrder


class Pdu(SystemElement):
    def __init__(
            self,
            length: int,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.length = length


class SignalPdu(Pdu):
    def __init__(
            self,
            signals: Mapping[tuple[int, int], tuple[str, ByteOrder]],
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.signals = {
            pos: self._make_item(s, p, pos)
            for pos, (s, p) in signals.items()
        }

    @staticmethod
    def _make_item(
            signal_ref: str,
            packing: ByteOrder,
            position: Position,
    ) -> PduSignal:
        signal = Signal.get(signal_ref)
        start_byte, start_bit = position
        bits_required = (start_bit + signal.bit_length + 7) & ~7  # Round to multiple of 8
        n_bytes = bits_required // 8
        match packing:
            case '>':
                offset = bits_required - signal.bit_length - start_bit
            case '<':
                offset = start_bit
        item = PduSignal(
            name=signal.name,
            bit_length=signal.bit_length,
            bit_offset=offset,
            byte_span=(start_byte, start_byte + n_bytes),
            packing=packing,
            data_type=signal.dtype,
            conversion=signal.conversion,
        )
        return item


class Container(Pdu):
    def __init__(
            self,
            items: Iterable[tuple[str, type[Pdu], ItemId] | tuple[str, type[Pdu]]],
            header: tuple[int, int] | None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._items = items
        self.header = header
        self.items: dict[ItemId, Pdu] | None = None

    def collect_items(self):
        if self.items is not None:
            return
        self.items = dict(map(self._collect_item, self._items))

    @staticmethod
    def _collect_item(item: tuple[str, type[Pdu], ItemId]) -> tuple[int, Pdu]:
        ref, cls, item_id = item
        return int(item_id), cls.get(ref)
