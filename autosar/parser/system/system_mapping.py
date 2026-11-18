from xml.etree.ElementTree import Element

from autosar.model.system import (
    SystemMapping,
    AnyCryptoServiceMapping,
    AnyDataMapping,
    SwcToEcuMapping,
)
from autosar.model.instance_ref import ComponentInSystemInstanceRef
from autosar.parser.identifiable import IdentifiableParser
from autosar.parser.instance_ref_parser import ComponentInSystemInstRefParser
from autosar.parser.parser_base import handler, not_implemented_handler, multiple, multiple_with_check, eval_children
from autosar.parser.system.crypto_service_mapping import CryptoServiceMappingParserSelector
from autosar.parser.system.data_mapping import DataMappingParserSelector


class SwcToEcuMappingParser(IdentifiableParser[SwcToEcuMapping]):
    _returned_type = SwcToEcuMapping

    @handler('ECU-INSTANCE-REF', required=True)
    def _parse_ecu_instance(self, xml_element: Element) -> str:
        ref = self._parse_text_node(xml_element)
        if ref is None:
            raise ValueError
        return ref

    @handler('COMPONENT-IREFS', param='component_instance_refs', required=True)
    @eval_children
    @multiple_with_check
    def _parse_component(self, xml_element: Element) -> ComponentInSystemInstanceRef:
        parser = ComponentInSystemInstRefParser()
        inst_ref = parser.parse_element(xml_element)
        if inst_ref is None:
            raise ValueError
        return inst_ref

    @handler('CONTROLLED-HW-ELEMENT-REF')
    def _parse_controlled_hw_element(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('PROCESSING-UNIT-REF')
    def _parse_processing_unit(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)


class SystemMappingParser(IdentifiableParser[SystemMapping]):
    _returned_type = SystemMapping
    _not_impl_tags = (
        'APPLICATION-PARTITION-TO-ECU-PARTITION-MAPPING',
        'APP-OS-TASK-PROXY-TO-ECU-TASK-PROXY-MAPPING',
        'COM-MANAGEMENT-MAPPING',
        'CYCLIC-HANDLING-COM-DATA-TO-OS-TASK-PROXY-MAPPING',
        'DDS-I-SIGNAL-TO-TOPIC-MAPPING',
        'ECU-PARTITION-TO-CORE-MAPPING',
        'ECU-RESOURCE-MAPPING',
        'J-1939-CONTROLLER-APPLICATION-TO-J-1939-NM-NODE-MAPPING',
        'J-1939-CONTROLLER-APPLICATION-TO-J-1939-NODE-MAPPING',
        'MAPPING-CONSTRAINT',
        'PNC-MAPPING',
        'PORT-ELEMENT-TO-COM-RESOURCE-MAPPING',
        'RESOURCE-ESTIMATION',
        'RESOURCE-TO-APPLICATION-PARTITION-MAPPING',
        'RTE-EVENT-SEPARATION',
        'RTE-EVENT-TO-OS-TASK-PROXY-MAPPING',
        'SIGNAL-PATH-CONSTRAINT',
        'SOFTWARE-CLUSTER-TO-APPLICATION-PARTITION-MAPPING',
        'SOFTWARE-CLUSTER-TO-RESOURCE-MAPPING',
        'SW-CLUSTER-MAPPING',
        'SWC-TO-APPLICATION-PARTITION-MAPPING',
        'SW-IMPL-MAPPING',
        'SYSTEM-SIGNAL-GROUP-TO-COM-RESOURCE-MAPPING',
        'SYSTEM-SIGNAL-TO-COM-RESOURCE-MAPPING',
    )

    @handler('CRYPTO-SERVICE-MAPPINGS')
    @multiple
    def _parse_crypto_service_mapping(self, xml_element: Element) -> AnyCryptoServiceMapping | None:
        parser = CryptoServiceMappingParserSelector(xml_element.tag)
        return parser.parse_element(xml_element)

    @handler('DATA-MAPPINGS')
    @multiple
    def _parse_data_mapping(self, xml_element: Element) -> AnyDataMapping | None:
        parser = DataMappingParserSelector(xml_element.tag)
        return parser.parse_element(xml_element)

    @handler('SW-MAPPINGS')
    @multiple_with_check(expected_name='SWC-TO-ECU-MAPPING')
    def _parse_sw_mapping(self, xml_element: Element) -> SwcToEcuMapping | None:
        parser = SwcToEcuMappingParser(xml_element.tag)
        return parser.parse_element(xml_element)

    @not_implemented_handler(*_not_impl_tags)
    def _placeholder_mappings_not_impl(self):
        ...
