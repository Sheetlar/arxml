from xml.etree.ElementTree import Element

from autosar.model.transformation.tlv import TlvDataIdDefinition, TlvDataIdDefinitionSet
from autosar.parser.identifiable import IdentifiableParser
from autosar.parser.parser_base import handler, multiple_with_check, BasicParser


class TlvDataIdDefinitionParser(BasicParser[TlvDataIdDefinition]):
    _returned_type = TlvDataIdDefinition

    @handler('ID', required=True)
    def _parse_id(self, xml_element: Element) -> int:
        if (id_ := self._parse_int_node(xml_element)) is None:
            raise ValueError
        return id_

    @handler('TLV-ARGUMENT-REF')
    def _parse_tlv_argument(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('TLV-IMPLEMENTATION-DATA-TYPE-ELEMENT-REF')
    def _parse_tlv_implementation_data_type_element(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('TLV-RECORD-ELEMENT-REF')
    def _parse_tlv_record_element(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)


class TlvDataIdDefinitionSetParser(IdentifiableParser[TlvDataIdDefinitionSet]):
    _returned_type = TlvDataIdDefinitionSet

    @handler('TLV-DATA-ID-DEFINITIONS')
    @multiple_with_check
    def _parse_tlv_data_id_definition(self, xml_element: Element) -> TlvDataIdDefinition | None:
        parser = TlvDataIdDefinitionParser()
        return parser.parse_element(xml_element)
