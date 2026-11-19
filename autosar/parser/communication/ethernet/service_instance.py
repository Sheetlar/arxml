from xml.etree.ElementTree import Element

from autosar.model.base import TagWithOptionalValue
from autosar.model.communication.ethernet.service_instance import (
    ServiceInstance,
    ConsumedServiceInstance,
    ProvidedServiceInstance,
    ServiceInstanceCollectionSet,
)
from autosar.model.communication.ethernet.some_ip import (
    SomeIpServiceVersion,
    PduActivationRoutingGroup,
    ConsumedEventGroup,
    EventHandler,
)
from autosar.model.enums import ServiceVersionAcceptanceKindEnum
from autosar.parser.common_simple_parsers import TagWithOptionalValueParser
from autosar.parser.communication.ethernet.some_ip import (
    SomeIpServiceVersionParser,
    PduActivationRoutingGroupParser,
    ConsumedEventGroupParser,
    EventHandlerParser,
)
from autosar.parser.identifiable import IdentifiableParser
from autosar.parser.parser_base import (
    handler,
    multiple_with_check,
    multiple,
    ref_variation,
    ParserSelector,
)


class AbstractServiceInstanceParser(IdentifiableParser[ServiceInstance]):
    @handler('MAJOR-VERSION', required=True)
    def _parse_major_version(self, xml_element: Element) -> int:
        if (ver := self._parse_int_node(xml_element)) is None:
            raise ValueError
        return ver

    @handler('CAPABILITY-RECORDS')
    @multiple_with_check
    def _parse_capability_record(self, xml_element: Element) -> TagWithOptionalValue | None:
        parser = TagWithOptionalValueParser()
        return parser.parse_element(xml_element)

    @handler('METHOD-ACTIVATION-ROUTING-GROUPS')
    @multiple_with_check
    def _parse_method_activation_routing_group(self, xml_element: Element) -> PduActivationRoutingGroup | None:
        parser = PduActivationRoutingGroupParser()
        return parser.parse_element(xml_element)


class ConsumedServiceInstanceParser(AbstractServiceInstanceParser[ConsumedServiceInstance]):
    _returned_type = ConsumedServiceInstance

    @handler('MINOR-VERSION')
    def _parse_minor_version(self, xml_element: Element) -> int | float | None:
        return self._parse_number_node(xml_element)

    @handler('SERVICE-IDENTIFIER')
    def _parse_service_identifier(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('INSTANCE-IDENTIFIER')
    def _parse_instance_identifier(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('CONSUMED-EVENT-GROUPS')
    @multiple_with_check
    def _parse_consumed_event_group(self, xml_element: Element) -> ConsumedEventGroup | None:
        parser = ConsumedEventGroupParser()
        return parser.parse_element(xml_element)

    @handler('ALLOWED-SERVICE-PROVIDERS', param='allowed_service_provider_refs')
    @ref_variation(element_name='NETWORK-ENDPOINT')
    def _parse_allowed_service_provider(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('EVENT-MULTICAST-SUBSCRIPTION-ADDRESSS', param='event_multicast_subscription_address_refs')
    @ref_variation(element_name='APPLICATION-ENDPOINT')
    def _parse_event_multicast_subscription_address(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('LOCAL-UNICAST-ADDRESSS', param='local_unicast_address_refs')
    @ref_variation(element_name='APPLICATION-ENDPOINT')
    def _parse_local_unicast_address(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('REMOTE-UNICAST-ADDRESSS', param='remote_unicast_address_refs')
    @ref_variation(element_name='APPLICATION-ENDPOINT')
    def _parse_remote_unicast_address(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('SD-CLIENT-TIMER-CONFIGS', param='sd_client_timer_config_refs')
    @ref_variation(element_name='SOMEIP-SD-CLIENT-SERVICE-INSTANCE-CONFIG')
    def _parse_sd_client_timer_config(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('BLOCKLISTED-VERSIONS')
    @multiple_with_check(expected_name='SOMEIP-SERVICE-VERSION')
    def _parse_blocklisted_version(self, xml_element: Element) -> SomeIpServiceVersion | None:
        parser = SomeIpServiceVersionParser()
        return parser.parse_element(xml_element)

    @handler('VERSION-DRIVEN-FIND-BEHAVIOR')
    def _parse_version_driven_find_behavior(self, xml_element: Element) -> ServiceVersionAcceptanceKindEnum | None:
        return self._parse_enum_node(xml_element, ServiceVersionAcceptanceKindEnum)

    @handler('AUTO-REQUIRE')
    def _parse_auto_require(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)


class ProvidedServiceInstanceParser(AbstractServiceInstanceParser[ProvidedServiceInstance]):
    _returned_type = ProvidedServiceInstance

    @handler('MINOR-VERSION')
    def _parse_minor_version(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('SERVICE-IDENTIFIER')
    def _parse_service_identifier(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('INSTANCE-IDENTIFIER')
    def _parse_instance_identifier(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('EVENT-HANDLERS')
    @multiple_with_check
    def _parse_event_handler(self, xml_element: Element) -> EventHandler | None:
        parser = EventHandlerParser()
        return parser.parse_element(xml_element)

    @handler('ALLOWED-SERVICE-CONSUMERS', param='allowed_service_consumer_refs')
    @ref_variation(element_name='NETWORK-ENDPOINT')
    def _parse_allowed_service_consumer(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('LOCAL-UNICAST-ADDRESSS', param='local_unicast_address_refs')
    @ref_variation(element_name='APPLICATION-ENDPOINT')
    def _parse_local_unicast_address(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('REMOTE-UNICAST-ADDRESSS', param='remote_unicast_address_refs')
    @ref_variation(element_name='APPLICATION-ENDPOINT')
    def _parse_remote_unicast_address(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('REMOTE-MULTICAST-SUBSCRIPTION-ADDRESSS', param='remote_multicast_subscription_address_refs')
    @ref_variation(element_name='APPLICATION-ENDPOINT')
    def _parse_remote_multicast_subscription_address(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('SD-SERVER-TIMER-CONFIGS', param='sd_server_timer_config_refs')
    @ref_variation(element_name='SOMEIP-SD-SERVER-SERVICE-INSTANCE-CONFIG')
    def _parse_sd_server_timer_config(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('LOAD-BALANCING-PRIORITY')
    def _parse_load_balancing_priority(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('LOAD-BALANCING-WEIGHT')
    def _parse_load_balancing_weight(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('PRIORITY')
    def _parse_priority(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('AUTO-AVAILABLE')
    def _parse_auto_available(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)


class ServiceInstanceParserSelector(ParserSelector[ServiceInstance]):
    _not_implemented = {'DDS-CP-SERVICE-INSTANCE'}
    _tag_map = {
        'CONSUMED-SERVICE-INSTANCE': ConsumedServiceInstanceParser,
        'PROVIDED-SERVICE-INSTANCE': ProvidedServiceInstanceParser,
    }


class ServiceInstanceCollectionSetParser(IdentifiableParser[ServiceInstanceCollectionSet]):
    _returned_type = ServiceInstanceCollectionSet

    @handler('SERVICE-INSTANCES')
    @multiple
    def _parse_service_instance(self, xml_element: Element) -> ServiceInstance | None:
        parser = ServiceInstanceParserSelector(xml_element.tag)
        return parser.parse_element(xml_element)
