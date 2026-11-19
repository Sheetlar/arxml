from xml.etree.ElementTree import Element

from autosar.model.communication.ethernet.some_ip import (
    SoConIPduIdentifier,
    SocketConnectionIPduIdentifierSet,
    SomeIpTpChannel,
    SomeIpTpConnection,
    SomeIpTpConfig,
    SomeIpServiceVersion,
    InitialSdDelayConfig,
    RequestResponseDelay,
    SomeipSdClientServiceInstanceConfig,
    SomeipSdServerServiceInstanceConfig,
    SomeipSdClientEventGroupTimingConfig,
    SomeipSdServerEventGroupTimingConfig,
    PduActivationRoutingGroup,
    ConsumedEventGroup,
    EventHandler,
    ConsumedProvidedServiceInstanceGroup,
)
from autosar.model.enums import (
    PduCollectionSemanticsEnum,
    PduCollectionTriggerEnum,
    EventGroupControlTypeEnum,
)
from autosar.parser.communication.tp_base import TpConfigParser
from autosar.parser.identifiable import IdentifiableParser, ReferrableParser
from autosar.parser.parser_base import (
    handler,
    multiple_with_check,
    ref_variation,
    BasicParser,
)


class SoConIPduIdentifierParser(ReferrableParser[SoConIPduIdentifier]):
    _returned_type = SoConIPduIdentifier

    @handler('HEADER-ID')
    def _parse_header_id(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('PDU-TRIGGERING-REF')
    def _parse_pdu_triggering(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('PDU-COLLECTION-PDU-TIMEOUT')
    def _parse_pdu_collection_pdu_timeout(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('PDU-COLLECTION-SEMANTICS')
    def _parse_pdu_collection_semantics(self, xml_element: Element) -> PduCollectionSemanticsEnum | None:
        return self._parse_enum_node(xml_element, PduCollectionSemanticsEnum)

    @handler('PDU-COLLECTION-TRIGGER')
    def _parse_pdu_collection_trigger(self, xml_element: Element) -> PduCollectionTriggerEnum | None:
        return self._parse_enum_node(xml_element, PduCollectionTriggerEnum)


class SocketConnectionIPduIdentifierSetParser(
    IdentifiableParser[SocketConnectionIPduIdentifierSet]
):
    _returned_type = SocketConnectionIPduIdentifierSet

    @handler('I-PDU-IDENTIFIERS')
    @multiple_with_check(expected_name='SO-CON-I-PDU-IDENTIFIER')
    def _parse_i_pdu_identifier(self, xml_element: Element) -> SoConIPduIdentifier | None:
        parser = SoConIPduIdentifierParser()
        return parser.parse_element(xml_element)


class SomeIpTpChannelParser(IdentifiableParser[SomeIpTpChannel]):
    _returned_type = SomeIpTpChannel

    @handler('BURST-SIZE')
    def _parse_burst_size(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('RX-TIMEOUT-TIME')
    def _parse_rx_timeout_time(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('SEPARATION-TIME')
    def _parse_separation_time(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)


class SomeIpTpConnectionParser(BasicParser[SomeIpTpConnection]):
    _returned_type = SomeIpTpConnection

    @handler('TP-CHANNEL-REF')
    def _parse_tp_channel_ref(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('TP-SDU-REF')
    def _parse_tp_sdu_ref(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('TRANSPORT-PDU-REF')
    def _parse_transport_pdu_ref(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('TP-CONCURRENT-PROCESSING-SDUS', param='tp_concurrent_processing_sdu_refs')
    @ref_variation
    def _parse_tp_concurrent_processing_sdu(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)


class SomeIpTpConfigParser(TpConfigParser[SomeIpTpConfig]):
    _returned_type = SomeIpTpConfig

    @handler('TP-CHANNELS')
    @multiple_with_check(expected_name='SOMEIP-TP-CHANNEL')
    def _parse_tp_channel(self, xml_element: Element) -> SomeIpTpChannel | None:
        parser = SomeIpTpChannelParser()
        return parser.parse_element(xml_element)

    @handler('TP-CONNECTIONS')
    @multiple_with_check(expected_name='SOMEIP-TP-CONNECTION')
    def _parse_tp_connection(self, xml_element: Element) -> SomeIpTpConnection | None:
        parser = SomeIpTpConnectionParser()
        return parser.parse_element(xml_element)


class SomeIpServiceVersionParser(BasicParser[SomeIpServiceVersion]):
    _returned_type = SomeIpServiceVersion

    @handler('MAJOR-VERSION')
    def _parse_major_version(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('MINOR-VERSION')
    def _parse_minor_version(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)


class InitialSdDelayConfigParser(BasicParser[InitialSdDelayConfig]):
    _returned_type = InitialSdDelayConfig

    @handler('INITIAL-DELAY-MAX-VALUE')
    def _parse_initial_delay_max_value(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('INITIAL-DELAY-MIN-VALUE')
    def _parse_initial_delay_min_value(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('INITIAL-REPETITIONS-BASE-DELAY')
    def _parse_initial_repetitions_base_delay(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('INITIAL-REPETITIONS-MAX')
    def _parse_initial_repetitions_max(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)


class RequestResponseDelayParser(BasicParser[RequestResponseDelay]):
    _returned_type = RequestResponseDelay

    @handler('MAX-VALUE')
    def _parse_max_value(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('MIN-VALUE')
    def _parse_min_value(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)


class SomeIpSdClientServiceInstanceConfigParser(
    IdentifiableParser[SomeipSdClientServiceInstanceConfig]
):
    _returned_type = SomeipSdClientServiceInstanceConfig

    @handler('INITIAL-FIND-BEHAVIOR')
    def _parse_initial_find_behavior(self, xml_element: Element) -> InitialSdDelayConfig | None:
        parser = InitialSdDelayConfigParser()
        return parser.parse_element(xml_element)

    @handler('PRIORITY')
    def _parse_priority(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('SERVICE-FIND-TIME-TO-LIVE')
    def _parse_service_find_time_to_live(self, xml_element: Element) -> int:
        return self._parse_int_node(xml_element) or 0xFFFFFF


class SomeIpSdServerServiceInstanceConfigParser(
    IdentifiableParser[SomeipSdServerServiceInstanceConfig]
):
    _returned_type = SomeipSdServerServiceInstanceConfig

    @handler('INITIAL-OFFER-BEHAVIOR')
    def _parse_initial_offer_behavior(self, xml_element: Element) -> InitialSdDelayConfig | None:
        parser = InitialSdDelayConfigParser()
        return parser.parse_element(xml_element)

    @handler('PRIORITY')
    def _parse_priority(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('REQUEST-RESPONSE-DELAY')
    def _parse_request_response_delay(self, xml_element: Element) -> RequestResponseDelay | None:
        parser = RequestResponseDelayParser()
        return parser.parse_element(xml_element)

    @handler('SERVICE-OFFER-TIME-TO-LIVE')
    def _parse_service_offer_time_to_live(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)


class SomeIpSdClientEventGroupTimingConfigParser(
    IdentifiableParser[SomeipSdClientEventGroupTimingConfig]
):
    _returned_type = SomeipSdClientEventGroupTimingConfig

    @handler('REQUEST-RESPONSE-DELAY')
    def _parse_request_response_delay(self, xml_element: Element) -> RequestResponseDelay | None:
        parser = RequestResponseDelayParser()
        return parser.parse_element(xml_element)

    @handler('SUBSCRIBE-EVENTGROUP-RETRY-DELAY')
    def _parse_subscribe_eventgroup_retry_delay(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('SUBSCRIBE-EVENTGROUP-RETRY-MAX')
    def _parse_subscribe_eventgroup_retry_max(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('TIME-TO-LIVE')
    def _parse_time_to_live(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)


class SomeIpSdServerEventGroupTimingConfigParser(
    IdentifiableParser[SomeipSdServerEventGroupTimingConfig]
):
    _returned_type = SomeipSdServerEventGroupTimingConfig

    @handler('REQUEST-RESPONSE-DELAY')
    def _parse_request_response_delay(self, xml_element: Element) -> RequestResponseDelay | None:
        parser = RequestResponseDelayParser()
        return parser.parse_element(xml_element)


class PduActivationRoutingGroupParser(IdentifiableParser[PduActivationRoutingGroup]):
    _returned_type = PduActivationRoutingGroup

    @handler('EVENT-GROUP-CONTROL-TYPE')
    def _parse_event_group_control_type(self, xml_element: Element) -> EventGroupControlTypeEnum | None:
        return self._parse_enum_node(xml_element, EventGroupControlTypeEnum)

    @handler('I-PDU-IDENTIFIER-TCP-REFS')
    @multiple_with_check
    def _parse_i_pdu_identifier_tcp(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('I-PDU-IDENTIFIER-UDP-REFS')
    @multiple_with_check
    def _parse_i_pdu_identifier_udp(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)


class ConsumedEventGroupParser(IdentifiableParser[ConsumedEventGroup]):
    _returned_type = ConsumedEventGroup

    @handler('EVENT-GROUP-IDENTIFIER', required=True)
    def _parse_event_group_identifier(self, xml_element: Element) -> int:
        if (eg := self._parse_int_node(xml_element)) is None:
            raise ValueError
        return eg

    @handler('PDU-ACTIVATION-ROUTING-GROUPS')
    @multiple_with_check
    def _parse_pdu_activation_routing_group(self, xml_element: Element) -> PduActivationRoutingGroup | None:
        parser = PduActivationRoutingGroupParser()
        return parser.parse_element(xml_element)

    @handler('EVENT-MULTICAST-ADDRESSS', param='event_multicast_address_refs')
    @ref_variation(element_name='APPLICATION-ENDPOINT')
    def _parse_event_multicast_address(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('SD-CLIENT-TIMER-CONFIGS', param='sd_client_timer_config_refs')
    @ref_variation(element_name='SOMEIP-SD-CLIENT-EVENT-GROUP-TIMING-CONFIG')
    def _parse_sd_client_timer_config(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('PRIORITY')
    def _parse_priority(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('AUTO-REQUIRE')
    def _parse_auto_require(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)


class EventHandlerParser(IdentifiableParser[EventHandler]):
    _returned_type = EventHandler

    @handler('EVENT-GROUP-IDENTIFIER', required=True)
    def _parse_event_group_identifier(self, xml_element: Element) -> int:
        if (eg := self._parse_int_node(xml_element)) is None:
            raise ValueError
        return eg

    @handler('MULTICAST-THRESHOLD')
    def _parse_multicast_threshold(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('PDU-ACTIVATION-ROUTING-GROUPS')
    @multiple_with_check
    def _parse_pdu_activation_routing_group(self, xml_element: Element) -> PduActivationRoutingGroup | None:
        parser = PduActivationRoutingGroupParser()
        return parser.parse_element(xml_element)

    @handler('EVENT-MULTICAST-ADDRESSS', param='event_multicast_address_refs')
    @ref_variation(element_name='APPLICATION-ENDPOINT')
    def _parse_event_multicast_address(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('SD-SERVER-EG-TIMING-CONFIGS', param='sd_server_eg_timing_config_refs')
    @ref_variation(element_name='SOMEIP-SD-SERVER-EVENT-GROUP-TIMING-CONFIG')
    def _parse_sd_server_eg_timing_config(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)


class ConsumedProvidedServiceInstanceGroupParser(
    IdentifiableParser[ConsumedProvidedServiceInstanceGroup]
):
    _returned_type = ConsumedProvidedServiceInstanceGroup

    @handler('CONSUMED-SERVICE-INSTANCES', param='consumed_service_instance_refs')
    @ref_variation
    def _parse_consumed_service_instance(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('PROVIDED-SERVICE-INSTANCES', param='provided_service_instance_refs')
    @ref_variation
    def _parse_provided_service_instance(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)
