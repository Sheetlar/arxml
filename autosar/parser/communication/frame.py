from xml.etree.ElementTree import Element

from autosar.model.communication.can import CanFrame
from autosar.model.communication.ethernet.frame_tp import GenericEthernetFrame, Ieee1722TpFrame, UserDefinedEthernetFrame
from autosar.model.communication.flexray import FlexrayFrame
from autosar.model.communication.frame import AnyFrame, PduToFrameMapping
from autosar.model.communication.lin import LinEventTriggeredFrame, LinSporadicFrame, LinUnconditionalFrame
from autosar.model.enums import ByteOrderEnum
from autosar.parser.identifiable import IdentifiableParser
from autosar.parser.parser_base import handler, multiple_with_check


class PduToFrameMappingParser(IdentifiableParser[PduToFrameMapping]):
    _returned_type = PduToFrameMapping

    @handler('PDU-REF', required=True)
    def _parse_pdu(self, xml_element: Element) -> str:
        if (ref := self._parse_text_node(xml_element)) is None:
            raise ValueError
        return ref

    @handler('PACKING-BYTE-ORDER', required=True)
    def _parse_packing_byte_order(self, xml_element: Element) -> ByteOrderEnum:
        if (pack := self._parse_enum_node(xml_element, ByteOrderEnum)) is None:
            raise ValueError
        return pack

    @handler('START-POSITION', required=True)
    def _parse_start_position(self, xml_element: Element) -> int:
        if (pos := self._parse_int_node(xml_element)) is None:
            raise ValueError
        return pos

    @handler('UPDATE-INDICATION-BIT-POSITION')
    def _parse_update_indication_bit_position(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)


class FrameParser(IdentifiableParser[AnyFrame]):
    @handler('FRAME-LENGTH', required=True)
    def _parse_frame_length(self, xml_element: Element) -> int:
        if (length := self._parse_int_node(xml_element)) is None:
            raise ValueError
        return length

    @handler('PDU-TO-FRAME-MAPPINGS')
    @multiple_with_check
    def _parse_pdu_to_frame_mapping(self, xml_element: Element) -> PduToFrameMapping | None:
        parser = PduToFrameMappingParser()
        return parser.parse_element(xml_element)


class CanFrameParser(FrameParser[CanFrame]):
    _returned_type = CanFrame


class GenericEthernetFrameParser(FrameParser[GenericEthernetFrame]):
    _returned_type = GenericEthernetFrame


class Ieee1722TpFrameParser(FrameParser[Ieee1722TpFrame]):
    _returned_type = Ieee1722TpFrame

    @handler('RELATIVE-REPRESENTATION-TIME')
    def _parse_relative_representation_time(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('STREAM-IDENTIFIER')
    def _parse_stream_identifier(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('SUB-TYPE')
    def _parse_sub_type(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('VERSION')
    def _parse_version(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)


class UserDefinedEthernetFrameParser(FrameParser[UserDefinedEthernetFrame]):
    _returned_type = UserDefinedEthernetFrame


class FlexrayFrameParser(FrameParser[FlexrayFrame]):
    _returned_type = FlexrayFrame


class LinEventTriggeredFrameParser(FrameParser[LinEventTriggeredFrame]):
    _returned_type = LinEventTriggeredFrame

    @handler('COLLISION-RESOLVING-SCHEDULE-REF')
    def _parse_collision_resolving_schedule(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('LIN-UNCONDITIONAL-FRAME-REFS')
    @multiple_with_check
    def _parse_lin_unconditional_frame(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)


class LinSporadicFrameParser(FrameParser[LinSporadicFrame]):
    _returned_type = LinSporadicFrame

    @handler('SUBSTITUTED-FRAME-REFS')
    @multiple_with_check
    def _parse_substituted_frame(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)


class LinUnconditionalFrameParser(FrameParser[LinUnconditionalFrame]):
    _returned_type = LinUnconditionalFrame
