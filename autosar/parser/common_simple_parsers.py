from xml.etree.ElementTree import Element

from autosar.model.base import DataFilter
from autosar.model.enums import DataFilterTypeEnum
from autosar.parser.parser_base import handler, BasicParserWithoutParent


class DataFilterParser(BasicParserWithoutParent[DataFilter]):
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
