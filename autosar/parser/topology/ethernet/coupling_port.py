from xml.etree.ElementTree import Element

from autosar.model.enums import (
    MacSecRoleEnum,
    MacSecFailPermissiveModeEnum,
    EthernetConnectionNegotiationEnum,
    CouplingPortRoleEnum,
    EthernetMacLayerTypeEnum,
    EthernetPhysicalLayerTypeEnum,
    EthernetSwitchVlanIngressTagEnum,
)
from autosar.model.topology.ethernet import (
    CouplingPortDetails,
    VlanMembership,
    MacAddressVlanMembership,
    MacSecLocalKayProps,
    MacSecProps,
    PlcaProps,
    CouplingPort,
    CouplingPortConnection,
)
from autosar.parser.identifiable import IdentifiableParser
from autosar.parser.parser_base import (
    handler,
    multiple_with_check,
    ref_variation,
    BasicParser,
)
from autosar.parser.topology.ethernet.coupling_port_details import CouplingPortDetailsParser
from autosar.parser.topology.ethernet.vlan import VlanMembershipParser, MacAddressVlanMembershipParser


class MacSecLocalKayPropsParser(BasicParser[MacSecLocalKayProps]):
    _returned_type = MacSecLocalKayProps

    @handler('DESTINATION-MAC-ADDRESS')
    def _parse_destination_mac_address(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('GLOBAL-KAY-PROPS-REF')
    def _parse_global_kay_props(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('KEY-SERVER-PRIORITY')
    def _parse_key_server_priority(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('MKA-PARTICIPANT-REFS')
    @multiple_with_check
    def _parse_mka_participant(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('ROLE')
    def _parse_role(self, xml_element: Element) -> MacSecRoleEnum | None:
        return self._parse_enum_node(xml_element, MacSecRoleEnum)

    @handler('SOURCE-MAC-ADDRESS')
    def _parse_source_mac_address(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)


class MacSecPropsParser(BasicParser[MacSecProps]):
    _returned_type = MacSecProps

    @handler('AUTO-START')
    def _parse_auto_start(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)

    @handler('MAC-SEC-KAY-CONFIG')
    def _parse_mac_sec_kay_config(self, xml_element: Element) -> MacSecLocalKayProps | None:
        parser = MacSecLocalKayPropsParser()
        return parser.parse_element(xml_element)

    @handler('ON-FAIL-PERMISSIVE-MODE')
    def _parse_on_fail_permissive_mode(self, xml_element: Element) -> MacSecFailPermissiveModeEnum | None:
        return self._parse_enum_node(xml_element, MacSecFailPermissiveModeEnum)

    @handler('ON-FAIL-PERMISSIVE-MODE-TIMEOUT')
    def _parse_on_fail_permissive_mode_timeout(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('SAK-REKEY-TIME-SPAN')
    def _parse_sak_rekey_time_span(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)


class PlcaPropsParser(BasicParser[PlcaProps]):
    _returned_type = PlcaProps

    @handler('PLCA-LOCAL-NODE-ID')
    def _parse_plca_local_node_id(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('PLCA-MAX-BURST-COUNT')
    def _parse_plca_max_burst_count(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('PLCA-MAX-BURST-TIMER')
    def _parse_plca_max_burst_timer(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)


class CouplingPortParser(IdentifiableParser[CouplingPort]):
    _returned_type = CouplingPort

    @handler('CONNECTION-NEGOTIATION-BEHAVIOR')
    def _parse_connection_negotiation_behavior(self, xml_element: Element) -> EthernetConnectionNegotiationEnum | None:
        return self._parse_enum_node(xml_element, EthernetConnectionNegotiationEnum)

    @handler('COUPLING-PORT-ROLE')
    def _parse_coupling_port_role(self, xml_element: Element) -> CouplingPortRoleEnum | None:
        return self._parse_enum_node(xml_element, CouplingPortRoleEnum)

    @handler('COUPLING-PORT-DETAILS')
    def _parse_coupling_port_details(self, xml_element: Element) -> CouplingPortDetails | None:
        parser = CouplingPortDetailsParser()
        return parser.parse_element(xml_element)

    @handler('DEFAULT-VLAN-REF')
    def _parse_default_vlan(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('VLAN-MODIFIER-REF')
    def _parse_vlan_modifier(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('VLAN-MEMBERSHIPS', param='vlan_membership')
    @multiple_with_check
    def _parse_vlan_membership(self, xml_element: Element) -> VlanMembership | None:
        parser = VlanMembershipParser()
        return parser.parse_element(xml_element)

    @handler('MAC-MULTICAST-ADDRESS-REFS')
    @multiple_with_check
    def _parse_mac_multicast_address(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('MAC-ADDRESS-VLAN-ASSIGNMENTS')
    @multiple_with_check(expected_name='MAC-ADDRESS-VLAN-MEMBERSHIP')
    def _parse_mac_address_vlan_assignment(self, xml_element: Element) -> MacAddressVlanMembership | None:
        parser = MacAddressVlanMembershipParser()
        return parser.parse_element(xml_element)

    @handler('MAC-LAYER-TYPE')
    def _parse_mac_layer_type(self, xml_element: Element) -> EthernetMacLayerTypeEnum | None:
        return self._parse_enum_node(xml_element, EthernetMacLayerTypeEnum)

    @handler('PHYSICAL-LAYER-TYPE')
    def _parse_physical_layer_type(self, xml_element: Element) -> EthernetPhysicalLayerTypeEnum | None:
        return self._parse_enum_node(xml_element, EthernetPhysicalLayerTypeEnum)

    @handler('MAC-SEC-PROPSS', param='mac_sec_props')
    @multiple_with_check
    def _parse_mac_sec_props(self, xml_element: Element) -> MacSecProps | None:
        parser = MacSecPropsParser()
        return parser.parse_element(xml_element)

    @handler('PLCA-PROPS')
    def _parse_plca_props(self, xml_element: Element) -> PlcaProps | None:
        parser = PlcaPropsParser()
        return parser.parse_element(xml_element)

    @handler('PNC-MAPPING-REFS')
    @multiple_with_check
    def _parse_pnc_mapping(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('RECEIVE-ACTIVITY')
    def _parse_receive_activity(self, xml_element: Element) -> EthernetSwitchVlanIngressTagEnum | None:
        return self._parse_enum_node(xml_element, EthernetSwitchVlanIngressTagEnum)

    @handler('WAKEUP-SLEEP-ON-DATALINE-CONFIG-REF')
    def _parse_wakeup_sleep_on_dataline_config(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)


class CouplingPortConnectionParser(BasicParser[CouplingPortConnection]):
    _returned_type = CouplingPortConnection

    @handler('FIRST-PORT-REF', required=True)  # TODO: Is this really required?
    def _parse_first_port(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('SECOND-PORT-REF', required=True)  # TODO: Is this really required?
    def _parse_second_port(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('NODE-PORT', param='node_port_refs')
    @ref_variation(element_name='COUPLING-PORT')
    def _parse_node_port(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('PLCA-LOCAL-NODE-COUNT')
    def _parse_plca_local_node_count(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('PLCA-TRANSMIT-OPPORTUNITY-TIMER')
    def _parse_plca_transmit_opportunity_timer(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)
