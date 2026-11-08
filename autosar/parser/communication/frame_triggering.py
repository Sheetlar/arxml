from typing import TypeVar
from xml.etree.ElementTree import Element

from autosar.model.communication.can import CanFrameTriggering, RxIdentifierRange
from autosar.model.communication.frame import FrameTriggering
from autosar.model.enums import CanAddressingModeType, CanFrameRxBehaviorEnum, CanFrameTxBehaviorEnum
from autosar.parser.identifiable import IdentifiableParser
from autosar.parser.parser_base import (
    handler,
    not_implemented_handler,
    multiple_with_check,
    ref_variation,
    ParserSelector,
    BasicParserWithoutParent,
)

FT = TypeVar('FT', bound=FrameTriggering)


class FrameTriggeringParser(IdentifiableParser[FT]):
    @handler('FRAME-REF', required=True)
    def _parse_frame(self, xml_element: Element) -> str:
        ref = self._parse_text_node(xml_element)
        if ref is None:
            raise ValueError
        return ref

    @handler('FRAME-PORT-REFS')
    @multiple_with_check
    def _parse_port_ref(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('PDU-TRIGGERINGS', param='pdu_triggering_refs')
    @ref_variation
    def _parse_pdu_triggering(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)


class RxIdentifierRangeParser(BasicParserWithoutParent[RxIdentifierRange]):
    _returned_type = RxIdentifierRange

    @handler('LOWER-CAN-ID', required=True)
    def _parse_lower_id(self, xml_element: Element) -> int:
        lower_id = self._parse_int_node(xml_element)
        if lower_id is None:
            raise ValueError
        return lower_id

    @handler('UPPER-CAN-ID', required=True)
    def _parse_upper_id(self, xml_element: Element) -> int:
        upper_id = self._parse_int_node(xml_element)
        if upper_id is None:
            raise ValueError
        return upper_id


class CanFrameTriggeringParser(FrameTriggeringParser[CanFrameTriggering]):
    _returned_type = CanFrameTriggering

    @handler('CAN-ADDRESSING-MODE', required=True)
    def _parse_addressing_mode(self, xml_element: Element) -> CanAddressingModeType:
        mode = self._parse_enum_node(xml_element, CanAddressingModeType)
        if mode is None:
            raise ValueError
        return mode

    @handler('CAN-FRAME-RX-BEHAVIOR', required=True)
    def _parse_rx_behavior(self, xml_element: Element) -> CanFrameRxBehaviorEnum:
        behavior = self._parse_enum_node(xml_element, CanFrameRxBehaviorEnum)
        if behavior is None:
            raise ValueError
        return behavior

    @handler('CAN-FRAME-TX-BEHAVIOR', required=True)
    def _parse_tx_behavior(self, xml_element: Element) -> CanFrameTxBehaviorEnum:
        behavior = self._parse_enum_node(xml_element, CanFrameTxBehaviorEnum)
        if behavior is None:
            raise ValueError
        return behavior

    @handler('IDENTIFIER')
    def _parse_identifier(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('RX-MASK')
    def _parse_rx_mask(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('TX-MASK')
    def _parse_tx_mask(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('RX-IDENTIFIER-RANGE')
    def _parse_rx_id_range(self, xml_element: Element) -> RxIdentifierRange | None:
        parser = RxIdentifierRangeParser()
        return parser.parse_element(xml_element)

    @handler('J-1939-REQUESTABLE')
    def _parse_j1939_req(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)

    @not_implemented_handler('ABSOLUTELY-SCHEDULED-TIMINGS')
    def _parse_abs_scheduled_timing(self, xml_element: Element):
        ...

    @not_implemented_handler('CAN-XL-FRAME-TRIGGERING-PROPS')
    def _parse_xl_triggering_props(self, xml_element: Element):
        ...


class FrameTriggeringParserSelector(ParserSelector[FT]):
    _tag_map = {
        'CAN-FRAME-TRIGGERING': CanFrameTriggeringParser,
    }
