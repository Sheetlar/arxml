from xml.etree.ElementTree import Element

from autosar.model.enums import EthernetSwitchVlanEgressTaggingEnum
from autosar.model.topology.ethernet import (
    Ipv4DhcpServerConfiguration,
    Ipv6DhcpServerConfiguration,
    DhcpServerConfiguration,
    VlanMembership,
    MacAddressVlanMembership,
    MacMulticastGroup,
    VlanConfig,
)
from autosar.parser.identifiable import IdentifiableParser, DescribableParser
from autosar.parser.parser_base import (
    handler,
    multiple_with_check,
    BasicParserWithoutParent,
)


class Ipv4DhcpServerConfigurationParser(DescribableParser[Ipv4DhcpServerConfiguration]):
    _returned_type = Ipv4DhcpServerConfiguration

    @handler('ADDRESS-RANGE-LOWER-BOUND')
    def _parse_address_range_lower_bound(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('ADDRESS-RANGE-UPPER-BOUND')
    def _parse_address_range_upper_bound(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('DEFAULT-GATEWAY')
    def _parse_default_gateway(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('DNS-SERVER-ADDRESSES', 'DNS-SERVER-ADDRESSS')
    @multiple_with_check(expected_name='DNS-SERVER-ADDRESS')
    def _parse_dns_server_address(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('NETWORK-MASK')
    def _parse_network_mask(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('DEFAULT-LEASE-TIME')
    def _parse_default_lease_time(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)


class Ipv6DhcpServerConfigurationParser(DescribableParser[Ipv6DhcpServerConfiguration]):
    _returned_type = Ipv6DhcpServerConfiguration

    @handler('ADDRESS-RANGE-LOWER-BOUND')
    def _parse_address_range_lower_bound(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('ADDRESS-RANGE-UPPER-BOUND')
    def _parse_address_range_upper_bound(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('DEFAULT-GATEWAY')
    def _parse_default_gateway(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('DNS-SERVER-ADDRESSES', 'DNS-SERVER-ADDRESSS')
    @multiple_with_check(expected_name='DNS-SERVER-ADDRESS')
    def _parse_dns_server_address(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('NETWORK-MASK')
    def _parse_network_mask(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('DEFAULT-LEASE-TIME')
    def _parse_default_lease_time(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)


class DhcpServerConfigurationParser(BasicParserWithoutParent[DhcpServerConfiguration]):
    _returned_type = DhcpServerConfiguration

    @handler('IPV-4-DHCP-SERVER-CONFIGURATION', param='ipv4_dhcp_server_configuration')
    def _parse_ipv4_dhcp_server_configuration(self, xml_element: Element) -> Ipv4DhcpServerConfiguration | None:
        parser = Ipv4DhcpServerConfigurationParser()
        return parser.parse_element(xml_element)

    @handler('IPV-6-DHCP-SERVER-CONFIGURATION', param='ipv6_dhcp_server_configuration')
    def _parse_ipv6_dhcp_server_configuration(self, xml_element: Element) -> Ipv6DhcpServerConfiguration | None:
        parser = Ipv6DhcpServerConfigurationParser()
        return parser.parse_element(xml_element)


class VlanMembershipParser(BasicParserWithoutParent[VlanMembership]):
    _returned_type = VlanMembership

    @handler('VLAN-REF', required=True)
    def _parse_vlan(self, xml_element: Element) -> str:
        if (ref := self._parse_text_node(xml_element)) is None:
            raise ValueError
        return ref

    @handler('DEFAULT-PRIORITY', required=True)
    def _parse_default_priority(self, xml_element: Element) -> int:
        if (v := self._parse_int_node(xml_element)) is None:
            raise ValueError
        return v

    @handler('DHCP-ADDRESS-ASSIGNMENT')
    def _parse_dhcp_address_assignment(self, xml_element: Element) -> DhcpServerConfiguration | None:
        parser = DhcpServerConfigurationParser()
        return parser.parse_element(xml_element)

    @handler('SEND-ACTIVITY')
    def _parse_send_activity(self, xml_element: Element) -> EthernetSwitchVlanEgressTaggingEnum | None:
        return self._parse_enum_node(xml_element, EthernetSwitchVlanEgressTaggingEnum)


class MacAddressVlanMembershipParser(IdentifiableParser[MacAddressVlanMembership]):
    _returned_type = MacAddressVlanMembership

    @handler('MAC-MULTICAST-ADDRESS-REFS')
    def _parse_mac_multicast_address(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('VLAN-REFS')
    def _parse_vlan(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)


class MacMulticastGroupParser(IdentifiableParser[MacMulticastGroup]):
    _returned_type = MacMulticastGroup

    @handler('MAC-MULTICAST-ADDRESS', required=True)
    def _parse_mac_multicast_address(self, xml_element: Element) -> str:
        if (addr := self._parse_text_node(xml_element)) is None:
            raise ValueError
        return addr


class VlanConfigParser(IdentifiableParser[VlanConfig]):
    _returned_type = VlanConfig

    @handler('VLAN-IDENTIFIER', required=True)
    def _parse_vlan_identifier(self, xml_element: Element) -> int:
        if (vlan := self._parse_int_node(xml_element)) is None:
            raise ValueError
        return vlan
