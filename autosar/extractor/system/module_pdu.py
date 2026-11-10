from abc import ABC, abstractmethod
from typing import Callable, Generic, TypeVar

from autosar.extractor.system.extractor_base import AbstractExtractor, ArxmlExtractionError
from autosar.extractor.transport import (
    SignalPdu,
    Container,
    LongHeaderId,
    ShortHeaderId,
    OffsetInContainer,
    ItemId,
    Pdu,
    ByteOrder,
    Position,
)
from autosar.misc import not_none, dict_sorted_by_keys
from autosar.model.ar_object import MaybeArObject
from autosar.model.enums import ContainerIPduHeaderTypeEnum, ByteOrderEnum
from autosar.model.communication.pdu import (
    ISignalIPdu,
    ContainerIPdu,
    ContainedIPduProps,
    IPdu,
    ISignalToIPduMapping,
)

T = TypeVar('T')


class PduExtractionModule(AbstractExtractor, ABC):
    def _extract_pdus(self):
        self._build_signal_pdus()
        self._build_container_pdus()
        self._collect_container_items()

    def _collect_container_items(self):
        for container in self._container_pdus:
            container.collect_items()

    def _build_container_pdus(self):
        try:
            pdus: list[ContainerIPdu] = self.fibex_elements[ContainerIPdu]
        except KeyError:
            self._logger.debug('No Container PDUs found')
            return
        self._logger.debug(f'Building {len(pdus)} container PDUs')
        self._container_pdus: list[Container] = list(filter(not_none, map(self._extract_container_pdu, pdus)))

    def _build_signal_pdus(self):
        try:
            pdus: list[ISignalIPdu] = self.fibex_elements[ISignalIPdu]
        except KeyError:
            raise ArxmlExtractionError('No signal PDUs found')
        self._logger.debug(f'Building {len(pdus)} signal PDUs')
        self._signal_pdus: list[SignalPdu] = list(filter(not_none, map(self._extract_signal_pdu, pdus)))

    def _extract_container_pdu(self, container_pdu: ContainerIPdu) -> Container | None:
        if len(container_pdu.contained_i_pdu_triggering_props) > 0:
            items = container_pdu.contained_i_pdu_triggering_props
            processor = PropsBasedProcessor
        elif len(container_pdu.contained_pdu_triggering_refs) > 0:
            items = container_pdu.contained_pdu_triggering_refs
            processor = RefsBasedProcessor
        else:
            return None
        items_processor = processor(container_pdu.header_type, self._find)
        contained = filter(not_none, map(items_processor, items))
        match container_pdu.header_type:
            case ContainerIPduHeaderTypeEnum.LONG_HEADER:
                header = (4, 4)
            case ContainerIPduHeaderTypeEnum.SHORT_HEADER:
                header = (3, 1)
            case ContainerIPduHeaderTypeEnum.NO_HEADER:
                header = None
        container = Container(
            identifier=container_pdu.ref,
            name=container_pdu.name,
            length=container_pdu.length,
            items=contained,
            header=header,
        )
        return container

    def _get_signal_from_mapping(
            self,
            mapping: ISignalToIPduMapping,
    ) -> tuple[Position, tuple[str, ByteOrder]] | None:
        if mapping.i_signal_ref is None:
            return None  # Ignoring groups
        if mapping.packing_byte_order is None:
            raise TypeError  # Incorrect, can be None only for groups
        match mapping.packing_byte_order:
            case ByteOrderEnum.OPAQUE:
                return None  # Not supported (yet)
            case ByteOrderEnum.MOST_SIGNIFICANT_BYTE_FIRST:  # Big endian
                return self._position_big_endian(mapping.start_position), (mapping.i_signal_ref, '>')
            case ByteOrderEnum.MOST_SIGNIFICANT_BYTE_LAST:  # Little endian
                return divmod(mapping.start_position, 8), (mapping.i_signal_ref, '<')

    def _extract_signal_pdu(self, signal_pdu: ISignalIPdu) -> SignalPdu | None:
        sorted_signals = dict_sorted_by_keys(filter(not_none, map(
            self._get_signal_from_mapping,
            signal_pdu.i_signal_to_pdu_mappings,
        )))
        pdu = SignalPdu(
            identifier=signal_pdu.ref,
            name=signal_pdu.name,
            length=signal_pdu.length,
            signals=sorted_signals,
        )
        return pdu

    @staticmethod
    def _position_big_endian(position: int) -> Position:
        byte, bit = divmod(position, 8)
        return byte, 7 - bit


class ContainedItemsProcessor(Generic[T], ABC):
    def __init__(
            self,
            header_t: ContainerIPduHeaderTypeEnum,
            find: Callable[[str], MaybeArObject],
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._id_cls, self._attr_name = self._get_type_and_attr(header_t)
        self._find = find

    @staticmethod
    def _get_type_and_attr(header_t: ContainerIPduHeaderTypeEnum) -> tuple[type[ItemId], str]:
        match header_t:
            case ContainerIPduHeaderTypeEnum.LONG_HEADER:
                return LongHeaderId, 'header_id_long_header'
            case ContainerIPduHeaderTypeEnum.SHORT_HEADER:
                return ShortHeaderId, 'header_id_short_header'
            case ContainerIPduHeaderTypeEnum.NO_HEADER:
                return OffsetInContainer, 'offset'

    @staticmethod
    def _get_pdu_type(pdu: IPdu | None) -> type[Pdu] | None:
        match pdu:
            case ISignalIPdu(): return SignalPdu
            case ContainerIPdu(): return Container
            case _: return None

    def _get_contained_pdu(self, trig_ref: str) -> tuple[IPdu, type[Pdu]]:
        pdu_ref: str = self._find(trig_ref).i_pdu_ref
        pdu: IPdu = self._find(pdu_ref)
        pdu_type = self._get_pdu_type(pdu)
        assert pdu_type is not None
        return pdu, pdu_type

    def _get_item_id(self, contained_pdu_props: ContainedIPduProps) -> ItemId:
        item_id = self._id_cls(getattr(contained_pdu_props, self._attr_name))
        return item_id

    def __call__(self, item: T) -> tuple[str, type[Pdu], ItemId] | None:
        try:
            return self._process_item(item)
        except (AttributeError, AssertionError):
            return None

    @abstractmethod
    def _process_item(self, item: T) -> tuple[str, type[Pdu], ItemId]:
        raise NotImplementedError


class PropsBasedProcessor(ContainedItemsProcessor[ContainedIPduProps]):
    def _process_item(self, item: T) -> tuple[str, type[Pdu], ItemId]:
        trig_ref = item.contained_pdu_triggering_ref
        pdu, pdu_type = self._get_contained_pdu(trig_ref)
        item_id = self._get_item_id(item)
        return pdu.ref, pdu_type, item_id


class RefsBasedProcessor(ContainedItemsProcessor[str]):
    def _process_item(self, item: T) -> tuple[str, type[Pdu], ItemId]:
        pdu, pdu_type = self._get_contained_pdu(item)
        contained_pdu_props = pdu.contained_i_pdu_props
        item_id = self._get_item_id(contained_pdu_props)
        return pdu.ref, pdu_type, item_id
