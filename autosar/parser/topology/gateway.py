from xml.etree.ElementTree import Element

from autosar.model.gateway import (
    DefaultValueElement,
    PduMappingDefaultValue,
    TargetIPduRef,
    FrameMapping,
    IPduMapping,
    ISignalMapping,
    Gateway,
)
from autosar.parser.identifiable import IdentifiableParser
from autosar.parser.parser_base import (
    handler,
    not_implemented_handler,
    multiple_with_check,
    eval_children,
    BasicParser,
)


class DefaultValueElementParser(BasicParser[DefaultValueElement]):
    _returned_type = DefaultValueElement

    @handler('ELEMENT-BYTE-VALUE', required=True)
    def _parse_element_byte_value(self, xml_element: Element) -> int:
        if (value := self._parse_int_node(xml_element)) is None:
            raise ValueError
        return value

    @handler('ELEMENT-POSITION', required=True)
    def _parse_element_position(self, xml_element: Element) -> int:
        if (position := self._parse_int_node(xml_element)) is None:
            raise ValueError
        return position


class PduMappingDefaultValueParser(BasicParser[PduMappingDefaultValue]):
    _returned_type = PduMappingDefaultValue

    @handler('DEFAULT-VALUE-ELEMENTS', required=True)
    @eval_children
    @multiple_with_check
    def _parse_default_value_element(self, xml_element: Element) -> DefaultValueElement | None:
        parser = DefaultValueElementParser()
        return parser.parse_element(xml_element)


class TargetIPduRefParser(BasicParser[TargetIPduRef]):
    _returned_type = TargetIPduRef

    @handler('TARGET-I-PDU-REF', required=True)
    def _parse_target_i_pdu(self, xml_element: Element) -> str:
        if (ref := self._parse_text_node(xml_element)) is None:
            raise ValueError
        return ref

    @handler('DEFAULT-VALUE')
    def _parse_default_value(self, xml_element: Element) -> PduMappingDefaultValue | None:
        parser = PduMappingDefaultValueParser()
        return parser.parse_element(xml_element)


class FrameMappingParser(BasicParser[FrameMapping]):
    _returned_type = FrameMapping

    @handler('SOURCE-FRAME-REF', required=True)
    def _parse_source_frame(self, xml_element: Element) -> str:
        if (ref := self._parse_text_node(xml_element)) is None:
            raise ValueError
        return ref

    @handler('TARGET-FRAME-REF', required=True)
    def _parse_target_frame(self, xml_element: Element) -> str:
        if (ref := self._parse_text_node(xml_element)) is None:
            raise ValueError
        return ref

    @not_implemented_handler('INTRODUCTION')
    def _parse_introduction(self, xml_element: Element):
        ...


class IPduMappingParser(BasicParser[IPduMapping]):
    _returned_type = IPduMapping

    @handler('SOURCE-I-PDU-REF', required=True)
    def _parse_source_i_pdu(self, xml_element: Element) -> str:
        if (ref := self._parse_text_node(xml_element)) is None:
            raise ValueError
        return ref

    @handler('TARGET-I-PDU', required=True)
    def _parse_target_i_pdu(self, xml_element: Element) -> TargetIPduRef:
        parser = TargetIPduRefParser()
        if (ref := parser.parse_element(xml_element)) is None:
            raise ValueError
        return ref

    @handler('PDU-MAX-LENGTH')
    def _parse_pdu_max_length(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('PDU-R-TP-CHUNK-SIZE')
    def _parse_pdu_r_tp_chunk_size(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @not_implemented_handler('INTRODUCTION')
    def _parse_introduction(self, xml_element: Element):
        ...


class ISignalMappingParser(BasicParser[ISignalMapping]):
    _returned_type = ISignalMapping

    @handler('SOURCE-SIGNAL-REF', required=True)
    def _parse_source_signal(self, xml_element: Element) -> str:
        if (ref := self._parse_text_node(xml_element)) is None:
            raise ValueError
        return ref

    @handler('TARGET-SIGNAL-REF', required=True)
    def _parse_target_signal(self, xml_element: Element) -> str:
        if (ref := self._parse_text_node(xml_element)) is None:
            raise ValueError
        return ref

    @not_implemented_handler('INTRODUCTION')
    def _parse_introduction(self, xml_element: Element):
        ...


class GatewayParser(IdentifiableParser[Gateway]):
    _returned_type = Gateway

    @handler('ECU-REF')
    def _parse_ecu(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('FRAME-MAPPINGS')
    @multiple_with_check
    def _parse_frame_mapping(self, xml_element: Element) -> FrameMapping | None:
        parser = FrameMappingParser()
        return parser.parse_element(xml_element)

    @handler('I-PDU-MAPPINGS')
    @multiple_with_check
    def _parse_i_pdu_mapping(self, xml_element: Element) -> IPduMapping | None:
        parser = IPduMappingParser()
        return parser.parse_element(xml_element)

    @handler('SIGNAL-MAPPINGS')
    @multiple_with_check
    def _parse_signal_mapping(self, xml_element: Element) -> ISignalMapping | None:
        parser = ISignalMappingParser()
        return parser.parse_element(xml_element)
