from xml.etree.ElementTree import Element

from autosar.model.enums import CouplingPortRatePolicyActionEnum
from autosar.model.topology.ethernet import (
    AnyCouplingPortStructuralElement,
    EthernetPriorityRegeneration,
    CouplingPortTrafficClassAssignment,
    GlobalTimeCouplingPortProps,
    CouplingPortRatePolicy,
    EthernetVlanTranslationTable,
    CouplingPortDetails,
)
from autosar.parser.identifiable import ReferrableParser
from autosar.parser.parser_base import (
    handler,
    multiple_with_check,
    multiple,
    eval_children,
    BasicParser,
)
from autosar.parser.topology.ethernet.coupling_port_structural_element import CouplingPortStructuralElementParserSelector


class EthernetPriorityRegenerationParser(ReferrableParser[EthernetPriorityRegeneration]):
    _returned_type = EthernetPriorityRegeneration

    @handler('INGRESS-PRIORITY', required=True)
    def _parse_ingress_priority(self, xml_element: Element) -> int:
        if (prio := self._parse_int_node(xml_element)) is None:
            raise ValueError
        return prio

    @handler('REGENERATED-PRIORITY', required=True)
    def _parse_regenerated_priority(self, xml_element: Element) -> int:
        if (prio := self._parse_int_node(xml_element)) is None:
            raise ValueError
        return prio


class CouplingPortTrafficClassAssignmentParser(
    ReferrableParser[CouplingPortTrafficClassAssignment]
):
    _returned_type = CouplingPortTrafficClassAssignment

    @handler('TRAFFIC-CLASS', required=True)
    def _parse_traffic_class(self, xml_element: Element) -> int:
        if (cls := self._parse_int_node(xml_element)) is None:
            raise ValueError
        return cls

    @handler('PRIORITIES', 'PRIORITYS')
    @multiple_with_check(expected_name='PRIORITY')
    def _parse_priority(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)


class GlobalTimeCouplingPortPropsParser(BasicParser[GlobalTimeCouplingPortProps]):
    _returned_type = GlobalTimeCouplingPortProps

    @handler('PROPAGATION-DELAY', required=True)
    def _parse_propagation_delay(self, xml_element: Element) -> float:
        if (delay := self._parse_float_node(xml_element)) is None:
            raise ValueError
        return delay


class CouplingPortRatePolicyParser(BasicParser[CouplingPortRatePolicy]):
    _returned_type = CouplingPortRatePolicy

    @handler('DATA-LENGTH')
    def _parse_data_length(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('POLICY-ACTION')
    def _parse_policy_action(self, xml_element: Element) -> CouplingPortRatePolicyActionEnum | None:
        return self._parse_enum_node(xml_element, CouplingPortRatePolicyActionEnum)

    @handler('PRIORITY')
    def _parse_priority(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('TIME-INTERVAL')
    def _parse_time_interval(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('V-LAN-REFS')
    @eval_children
    @multiple_with_check
    def _parse_v_lan(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)


class EthernetVlanTranslationTableParser(
    BasicParser[EthernetVlanTranslationTable]
):
    _returned_type = EthernetVlanTranslationTable

    @handler('TRANSLATED-VLAN-ID', required=True)
    def _parse_translated_vlan_id(self, xml_element: Element) -> int:
        if (vlan := self._parse_int_node(xml_element)) is None:
            raise ValueError
        return vlan

    @handler('INGRESS-VLAN-ID')
    def _parse_ingress_vlan_id(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)


class CouplingPortDetailsParser(BasicParser[CouplingPortDetails]):
    _returned_type = CouplingPortDetails

    @handler('COUPLING-PORT-STRUCTURAL-ELEMENTS')
    @multiple
    def _parse_coupling_port_structural_element(self, xml_element: Element) -> AnyCouplingPortStructuralElement | None:
        parser = CouplingPortStructuralElementParserSelector(xml_element.tag)
        return parser.parse_element(xml_element)

    @handler('DEFAULT-TRAFFIC-CLASS')
    def _parse_default_traffic_class(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('ETHERNET-PRIORITY-REGENERATIONS')
    @multiple_with_check
    def _parse_ethernet_priority_regeneration(self, xml_element: Element) -> EthernetPriorityRegeneration | None:
        parser = EthernetPriorityRegenerationParser()
        return parser.parse_element(xml_element)

    @handler('ETHERNET-TRAFFIC-CLASS-ASSIGNMENTS')
    @multiple_with_check(expected_name='COUPLING-PORT-TRAFFIC-CLASS-ASSIGNMENT')
    def _parse_ethernet_traffic_class_assignment(self, xml_element: Element) -> CouplingPortTrafficClassAssignment | None:
        parser = CouplingPortTrafficClassAssignmentParser()
        return parser.parse_element(xml_element)

    @handler('FRAME-PREEMPTION-SUPPORT')
    def _parse_frame_preemption_support(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)

    @handler('GLOBAL-TIME-PROPS')
    def _parse_global_time_props(self, xml_element: Element) -> GlobalTimeCouplingPortProps | None:
        parser = GlobalTimeCouplingPortPropsParser()
        return parser.parse_element(xml_element)

    @handler('LAST-EGRESS-SCHEDULER-REF')
    def _parse_last_egress_scheduler(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('RATE-POLICIES', 'RATE-POLICYS')
    @multiple_with_check(expected_name='COUPLING-PORT-RATE-POLICY')
    def _parse_rate_policy(self, xml_element: Element) -> CouplingPortRatePolicy | None:
        parser = CouplingPortRatePolicyParser()
        return parser.parse_element(xml_element)

    @handler('VLAN-TRANSLATION-TABLES')
    @multiple_with_check(expected_name='ETHERNET-VLAN-TRANSLATION-TABLE')
    def _parse_vlan_translation_table(self, xml_element: Element) -> EthernetVlanTranslationTable | None:
        parser = EthernetVlanTranslationTableParser()
        return parser.parse_element(xml_element)
