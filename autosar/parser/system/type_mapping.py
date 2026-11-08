from xml.etree.ElementTree import Element

from autosar.model.enums import MappingDirectionEnum
from autosar.model.system import (
    AnySenderRecCompositeTypeMapping,
    SenderRecArrayTypeMapping,
    SenderRecRecordTypeMapping,
    TextTableValuePair,
    TextTableMapping,
    IndexedArrayElement,
    SenderRecArrayElementMapping,
    SenderRecRecordElementMapping,
)
from autosar.parser.parser_base import ParserSelector, BasicParserWithoutParent, handler, multiple_with_check, single_subclass_aggr, eval_children


class TextTableValuePairParser(BasicParserWithoutParent[TextTableValuePair]):
    _returned_type = TextTableValuePair

    @handler('FIRST-VALUE', required=True)
    def _parse_first_value(self, xml_element: Element) -> int | float:
        value = self._parse_number_node(xml_element)
        if value is None:
            raise ValueError
        return value

    @handler('SECOND-VALUE', required=True)
    def _parse_second_value(self, xml_element: Element) -> int | float:
        value = self._parse_number_node(xml_element)
        if value is None:
            raise ValueError
        return value


class TextTableMappingParser(BasicParserWithoutParent[TextTableMapping]):
    returned_type = TextTableMapping

    @handler('IDENTICAL-MAPPING', required=True)
    def _parse_identical_mapping(self, xml_element: Element) -> bool:
        flag = self._parse_boolean_node(xml_element)
        if flag is None:
            raise ValueError
        return flag

    @handler('MAPPING-DIRECTION', required=True)
    def _parse_mapping_direction(self, xml_element: Element) -> MappingDirectionEnum:
        direction = self._parse_enum_node(xml_element, MappingDirectionEnum)
        if direction is None:
            raise ValueError
        return direction

    @handler('BITFIELD-TEXT-TABLE-MASK-FIRST')
    def _parse_bitfield_text_table_mask_first(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('BITFIELD-TEXT-TABLE-MASK-SECOND')
    def _parse_bitfield_text_table_mask_second(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('VALUE-PAIRS')
    @eval_children
    @multiple_with_check
    def _parse_value_pair(self, xml_element: Element) -> TextTableValuePair | None:
        parser = TextTableValuePairParser()
        return parser.parse_element(xml_element)


class IndexedArrayElementParser(BasicParserWithoutParent[IndexedArrayElement]):
    _returned_type = IndexedArrayElement

    @handler('INDEX', required=True)
    def _parse_index(self, xml_element: Element) -> int | float:
        value = self._parse_number_node(xml_element)
        if value is None:
            raise ValueError
        return value

    @handler('APPLICATION-ARRAY-ELEMENT-REF')
    def _parse_application_array_element(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('IMPLEMENTATION-ARRAY-ELEMENT-REF')
    def _parse_implementation_array_element(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)


class SenderRecArrayElementMappingParser(BasicParserWithoutParent[SenderRecArrayElementMapping]):
    _returned_type = SenderRecArrayElementMapping

    @handler('INDEXED-ARRAY-ELEMENT', required=True)
    def _parse_indexed_array_element(self, xml_element: Element) -> IndexedArrayElement:
        parser = IndexedArrayElementParser()
        element = parser.parse_element(xml_element)
        if element is None:
            raise ValueError
        return element

    @handler('SYSTEM-SIGNAL-REF')
    def _parse_system_signal(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('COMPLEX-TYPE-MAPPING')
    @single_subclass_aggr
    def _parse_complex_type_mapping(self, xml_element: Element) -> AnySenderRecCompositeTypeMapping | None:
        parser = SenderRecCompositeTypeMappingParserSelector(xml_element.tag)
        return parser.parse_element(xml_element)


class SenderRecRecordElementMappingParser(BasicParserWithoutParent[SenderRecRecordElementMapping]):
    _returned_type = SenderRecRecordElementMapping

    @handler('APPLICATION-RECORD-ELEMENT-REF')
    def _parse_application_record_element(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('IMPLEMENTATION-RECORD-ELEMENT-REF')
    def _parse_implementation_record_element(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('SYSTEM-SIGNAL-REF')
    def _parse_system_signal(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('COMPLEX-TYPE-MAPPING')
    @single_subclass_aggr
    def _parse_complex_type_mapping(self, xml_element: Element) -> AnySenderRecCompositeTypeMapping | None:
        parser = SenderRecCompositeTypeMappingParserSelector(xml_element.tag)
        return parser.parse_element(xml_element)

    @handler('SENDER-TO-SIGNAL-TEXT-TABLE-MAPPING')
    def _parse_sender_to_signal_text_table_mapping(self, xml_element: Element) -> TextTableMapping | None:
        parser = TextTableMappingParser()
        return parser.parse_element(xml_element)

    @handler('SIGNAL-TO-RECEIVER-TEXT-TABLE-MAPPING')
    def _parse_signal_to_receiver_text_table_mapping(self, xml_element: Element) -> TextTableMapping | None:
        parser = TextTableMappingParser()
        return parser.parse_element(xml_element)


class SenderRecArrayTypeMappingParser(BasicParserWithoutParent[SenderRecArrayTypeMapping]):
    _returned_type = SenderRecArrayTypeMapping

    @handler('ARRAY-ELEMENT-MAPPINGS')
    @eval_children
    @multiple_with_check
    def _parse_array_element_mapping(self, xml_element: Element) -> SenderRecArrayElementMapping | None:
        parser = SenderRecArrayElementMappingParser()
        return parser.parse_element(xml_element)

    @handler('SENDER-TO-SIGNAL-TEXT-TABLE-MAPPING')
    def _parse_sender_to_signal_text_table_mapping(self, xml_element: Element) -> TextTableMapping | None:
        parser = TextTableMappingParser()
        return parser.parse_element(xml_element)

    @handler('SIGNAL-TO-RECEIVER-TEXT-TABLE-MAPPING')
    def _parse_signal_to_receiver_text_table_mapping(self, xml_element: Element) -> TextTableMapping | None:
        parser = TextTableMappingParser()
        return parser.parse_element(xml_element)


class SenderRecRecordTypeMappingParser(BasicParserWithoutParent[SenderRecRecordTypeMapping]):
    _returned_type = SenderRecRecordTypeMapping

    @handler('RECORD-ELEMENT-MAPPINGS')
    @eval_children
    @multiple_with_check
    def _parse_record_element_mapping(self, xml_element: Element) -> SenderRecRecordElementMapping | None:
        parser = SenderRecRecordElementMappingParser()
        return parser.parse_element(xml_element)


class SenderRecCompositeTypeMappingParserSelector(ParserSelector[AnySenderRecCompositeTypeMapping]):
    _tag_map = {
        'SENDER-REC-ARRAY-TYPE-MAPPING': SenderRecArrayTypeMappingParser,
        'SENDER-REC-RECORD-TYPE-MAPPING': SenderRecRecordTypeMappingParser,
    }
