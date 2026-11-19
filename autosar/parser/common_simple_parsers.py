from xml.etree.ElementTree import Element

from autosar.model.base import DataFilter, TagWithOptionalValue
from autosar.model.enums import DataFilterTypeEnum
from autosar.parser.parser_base import handler, BasicParser


class DataFilterParser(BasicParser[DataFilter]):
    _returned_type = DataFilter

    @handler('DATA-FILTER-TYPE')
    def _parse_data_filter_type(self, xml_element: Element) -> DataFilterTypeEnum | None:
        return self._parse_enum_node(xml_element, DataFilterTypeEnum)

    @handler('MASK')
    def _parse_mask(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('MAX')
    def _parse_max(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('MIN')
    def _parse_min(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('OFFSET')
    def _parse_offset(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('PERIOD')
    def _parse_period(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('X')
    def _parse_x(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)


class TagWithOptionalValueParser(BasicParser[TagWithOptionalValue]):
    _returned_type = TagWithOptionalValue

    @handler('KEY', required=True)
    def _parse_key(self, xml_element: Element) -> str:
        if (key := self._parse_text_node(xml_element)) is None:
            raise ValueError
        return key

    @handler('VALUE')
    def _parse_value(self, xml_element: Element) -> str:
        return self._parse_text_node(xml_element) or ''

    @handler('SEQUENCE-OFFSET')
    def _parse_sequence_offset(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)
