from xml.etree.ElementTree import Element

from autosar.model.enums import (
    IpAddressKeepEnum,
    Ipv4AddressSourceEnum,
    Ipv6AddressSourceEnum,
)
from autosar.model.communication.ethernet import (
    AnyNetworkEndpointAddress,
    IPv4Configuration,
    IPv6Configuration,
    MacMulticastConfiguration,
    NetworkEndpoint,
)
from autosar.parser.identifiable import IdentifiableParser
from autosar.parser.parser_base import (
    handler,
    not_implemented_handler,
    multiple_with_check,
    multiple,
    eval_children,
    BasicParser,
    ParserSelector,
)


class IPv4ConfigurationParser(BasicParser[IPv4Configuration]):
    _returned_type = IPv4Configuration

    @handler('ASSIGNMENT-PRIORITY')
    def _parse_assignment_priority(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('DEFAULT-GATEWAY')
    def _parse_default_gateway(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('DNS-SERVER-ADDRESSES', 'DNS-SERVER-ADDRESSS')
    @eval_children
    @multiple_with_check(expected_name='DNS-SERVER-ADDRESS')
    def _parse_dns_server_address(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('IP-ADDRESS-KEEP-BEHAVIOR')
    def _parse_ip_address_keep_behavior(self, xml_element: Element) -> IpAddressKeepEnum | None:
        return self._parse_enum_node(xml_element, IpAddressKeepEnum)

    @handler('IPV-4-ADDRESS', param='ipv4_address')
    def _parse_ipv4_address(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('IPV-4-ADDRESS-SOURCE', param='ipv4_address_source')
    def _parse_ipv4_address_source(self, xml_element: Element) -> Ipv4AddressSourceEnum | None:
        return self._parse_enum_node(xml_element, Ipv4AddressSourceEnum)

    @handler('NETWORK-MASK')
    def _parse_network_mask(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('TTL')
    def _parse_ttl(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)


class IPv6ConfigurationParser(BasicParser[IPv6Configuration]):
    _returned_type = IPv6Configuration

    @handler('ASSIGNMENT-PRIORITY')
    def _parse_assignment_priority(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('DEFAULT-ROUTER')
    def _parse_default_router(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('DNS-SERVER-ADDRESSES', 'DNS-SERVER-ADDRESSS')
    @eval_children
    @multiple_with_check(expected_name='DNS-SERVER-ADDRESS')
    def _parse_dns_server_address(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('ENABLE-ANYCAST')
    def _parse_enable_anycast(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)

    @handler('HOP-COUNT')
    def _parse_hop_count(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('IP-ADDRESS-KEEP-BEHAVIOR')
    def _parse_ip_address_keep_behavior(self, xml_element: Element) -> IpAddressKeepEnum | None:
        return self._parse_enum_node(xml_element, IpAddressKeepEnum)

    @handler('IP-ADDRESS-PREFIX-LENGTH')
    def _parse_ip_address_prefix_length(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('IPV-6-ADDRESS', param='ipv6_address')
    def _parse_ipv6_address(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('IPV-6-ADDRESS-SOURCE', param='ipv6_address_source')
    def _parse_ipv6_address_source(self, xml_element: Element) -> Ipv6AddressSourceEnum | None:
        return self._parse_enum_node(xml_element, Ipv6AddressSourceEnum)


class MacMulticastConfigurationParser(BasicParser[MacMulticastConfiguration]):
    _returned_type = MacMulticastConfiguration

    @handler('MAC-MULTICAST-GROUP-REF', required=True)
    def _parse_mac_multicast_group(self, xml_element: Element) -> str:
        ref = self._parse_text_node(xml_element)
        if ref is None:
            raise ValueError
        return ref


class NetworkEndpointAddressParserSelector(ParserSelector[AnyNetworkEndpointAddress]):
    _tag_map = {
        'IPV-4-CONFIGURATION': IPv4ConfigurationParser,
        'IPV-6-CONFIGURATION': IPv6ConfigurationParser,
        'MAC-MULTICAST-CONFIGURATION': MacMulticastConfigurationParser,
    }


class NetworkEndpointParser(IdentifiableParser[NetworkEndpoint]):
    _returned_type = NetworkEndpoint

    @handler('NETWORK-ENDPOINT-ADDRESSES', 'NETWORK-ENDPOINT-ADDRESSS')
    @multiple
    def _parse_network_endpoint_address(self, xml_element: Element) -> AnyNetworkEndpointAddress | None:
        parser = NetworkEndpointAddressParserSelector(xml_element.tag)
        return parser.parse_element(xml_element)

    @handler('FULLY-QUALIFIED-DOMAIN-NAME')
    def _parse_fully_qualified_domain_name(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @not_implemented_handler('IP-SEC-CONFIG')
    def _parse_ip_sec_config(self, xml_element: Element):
        ...

    @not_implemented_handler('INFRASTRUCTURE-SERVICES')
    def _parse_infrastructure_services(self, xml_element: Element):
        ...

    @handler('PRIORITY')
    def _parse_priority(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)
