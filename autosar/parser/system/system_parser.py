from xml.etree.ElementTree import Element

from autosar.model.enums import ByteOrderEnum
from autosar.model.system import (
    System,
    SystemMapping,
    RootSwCompositionPrototype,
)
from autosar.parser.identifiable import IdentifiableParser
from autosar.parser.parser_base import (
    handler,
    not_implemented_handler,
    multiple_with_check,
    ref_variation,
)
from autosar.parser.system.system_mapping import SystemMappingParser


class RootSwCompositionPrototypeParser(IdentifiableParser[RootSwCompositionPrototype]):
    _returned_type = RootSwCompositionPrototype

    @handler('SOFTWARE-COMPOSITION-TREF', param='software_composition_type_ref', required=True)
    def _parse_software_composition_type(self, xml_element: Element) -> str:
        ref = self._parse_text_node(xml_element)
        if ref is None:
            raise ValueError
        return ref

    @handler('CALIBRATION-PARAMETER-VALUE-SET-REFS')
    @multiple_with_check
    def _parse_calibration_parameter_value_set(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('FLAT-MAP-REF')
    def _parse_flat_map(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)


class SystemParser(IdentifiableParser[System]):
    _returned_type = System

    @handler('CLIENT-ID-DEFINITION-SET-REFS')
    @multiple_with_check
    def _parse_client_id_set(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('CONTAINER-I-PDU-HEADER-BYTE-ORDER')
    def _parse_header_byte_order(self, xml_element: Element) -> ByteOrderEnum | None:
        return self._parse_enum_node(xml_element, ByteOrderEnum)

    @handler('ECU-EXTRACT-VERSION')
    def _parse_ecu_extract_version(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('FIBEX-ELEMENTS', param='fibex_element_refs')
    @ref_variation
    def _parse_fibex_element(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('INTERPOLATION-ROUTINE-MAPPING-SET-REFS')
    @multiple_with_check
    def _parse_interp_routine_mapping(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('MAPPINGS')
    @multiple_with_check(expected_name='SYSTEM-MAPPING')
    def _parse_mapping(self, xml_element: Element) -> SystemMapping | None:
        parser = SystemMappingParser()
        return parser.parse_element(xml_element)

    @handler('PNC-VECTOR-LENGTH')
    def _parse_vector_length(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('PNC-VECTOR-OFFSET')
    def _parse_vector_offset(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('ROOT-SOFTWARE-COMPOSITIONS', param='root_sw_compositions')
    @multiple_with_check(expected_name='ROOT-SW-COMPOSITION-PROTOTYPE')
    def _parse_sw_comp(self, xml_element: Element) -> RootSwCompositionPrototype | None:
        parser = RootSwCompositionPrototypeParser()
        return parser.parse_element(xml_element)

    @handler('SW-CLUSTERS', param='sw_cluster_refs')
    @ref_variation(element_name='CP-SOFTWARE-CLUSTER')
    def _parse_sw_cluster(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('SYSTEM-COM-SPEC-DEFINITION-REFS')
    @multiple_with_check
    def _parse_com_spec(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('SYSTEM-VERSION')
    def _parse_system_version(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @not_implemented_handler('J-1939-SHARED-ADDRESS-CLUSTER')
    def _parse_j1939_cluster(self, xml_element: Element):
        ...

    @not_implemented_handler('SYSTEM-DOCUMENTATIONS')
    def _parse_system_doc(self, xml_element: Element):
        ...
