from dataclasses import dataclass, field
from typing import Iterable

from autosar.model.ar_object import ArObject
from autosar.model.base import Referrable, Identifiable
from autosar.model.communication.tp import TpConfig
from autosar.model.element import Element
from autosar.model.enums import PduCollectionSemanticsEnum, PduCollectionTriggerEnum, EventGroupControlTypeEnum


class SoConIPduIdentifier(Referrable):
    def __init__(
            self,
            header_id: int | None = None,
            pdu_triggering_ref: str | None = None,
            pdu_collection_pdu_timeout: float | None = None,
            pdu_collection_semantics: PduCollectionSemanticsEnum | None = None,
            pdu_collection_trigger: PduCollectionTriggerEnum | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.header_id = header_id
        self.pdu_triggering_ref = pdu_triggering_ref
        self.pdu_collection_pdu_timeout = pdu_collection_pdu_timeout
        self.pdu_collection_semantics = pdu_collection_semantics
        self.pdu_collection_trigger = pdu_collection_trigger


class SocketConnectionIPduIdentifierSet(Element):
    def __init__(
            self,
            i_pdu_identifiers: Iterable[SoConIPduIdentifier] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.i_pdu_identifiers = self._set_parent(i_pdu_identifiers)

    @property
    def _findable_children(self) -> Iterable[ArObject]:
        yield from self.i_pdu_identifiers


class SomeIpTpChannel(Identifiable):
    def __init__(
            self,
            burst_size: int | None = None,
            rx_timeout_time: float | None = None,
            separation_time: float | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.burst_size = burst_size
        self.rx_timeout_time = rx_timeout_time
        self.separation_time = separation_time


@dataclass(repr=False)
class SomeIpTpConnection(ArObject):
    tp_channel_ref: str | None = None
    tp_sdu_ref: str | None = None
    transport_pdu_ref: str | None = None
    tp_concurrent_processing_sdu_refs: list[str] = field(default_factory=list)


class SomeIpTpConfig(TpConfig):
    def __init__(
            self,
            tp_channels: Iterable[SomeIpTpChannel] | None = None,
            tp_connections: Iterable[SomeIpTpConnection] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.tp_channels = self._set_parent(tp_channels)
        self.tp_connections = self.eval_children(tp_connections)


@dataclass(repr=False)
class SomeIpServiceVersion(ArObject):
    major_version: int | None = None
    minor_version: int | None = None


@dataclass(repr=False)
class InitialSdDelayConfig(ArObject):
    initial_delay_max_value: float | None = None
    initial_delay_min_value: float | None = None
    initial_repetitions_base_delay: float | None = None
    initial_repetitions_max: int | None = None


@dataclass(repr=False)
class RequestResponseDelay(ArObject):
    max_value: float | None = None
    min_value: float | None = None


class SomeipSdClientServiceInstanceConfig(Element):
    def __init__(
            self,
            initial_find_behavior: InitialSdDelayConfig | None = None,
            priority: int | None = None,
            service_find_time_to_live: int = 0xFFFFFF,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.initial_find_behavior = initial_find_behavior
        self.priority = priority
        self.service_find_time_to_live = service_find_time_to_live


class SomeipSdServerServiceInstanceConfig(Element):
    def __init__(
            self,
            initial_offer_behavior: InitialSdDelayConfig | None = None,
            offer_cyclic_delay: float | None = None,
            priority: int | None = None,
            request_response_delay: RequestResponseDelay | None = None,
            service_offer_time_to_live: int | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.initial_offer_behavior = initial_offer_behavior
        self.offer_cyclic_delay = offer_cyclic_delay
        self.priority = priority
        self.request_response_delay = request_response_delay
        self.service_offer_time_to_live = service_offer_time_to_live


class SomeipSdClientEventGroupTimingConfig(Element):
    def __init__(
            self,
            request_response_delay: RequestResponseDelay | None = None,
            subscribe_eventgroup_retry_delay: float | None = None,
            subscribe_eventgroup_retry_max: int | None = None,
            time_to_live: int | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.request_response_delay = request_response_delay
        self.subscribe_eventgroup_retry_delay = subscribe_eventgroup_retry_delay
        self.subscribe_eventgroup_retry_max = subscribe_eventgroup_retry_max
        self.time_to_live = time_to_live


class SomeipSdServerEventGroupTimingConfig(Element):
    def __init__(
            self,
            request_response_delay: RequestResponseDelay | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.request_response_delay = request_response_delay


class PduActivationRoutingGroup(Identifiable):
    def __init__(
            self,
            event_group_control_type: EventGroupControlTypeEnum | None = None,
            i_pdu_identifier_tcp_refs: Iterable[str] | None = None,
            i_pdu_identifier_udp_refs: Iterable[str] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.event_group_control_type = event_group_control_type
        self.i_pdu_identifier_tcp_refs = self.eval_children(i_pdu_identifier_tcp_refs)
        self.i_pdu_identifier_udp_refs = self.eval_children(i_pdu_identifier_udp_refs)

    def iter_refs(self):
        yield from self.i_pdu_identifier_tcp_refs
        yield from self.i_pdu_identifier_udp_refs


class ConsumedEventGroup(Identifiable):
    def __init__(
            self,
            event_group_identifier: int,
            pdu_activation_routing_groups: Iterable[PduActivationRoutingGroup] | None = None,
            event_multicast_address_refs: Iterable[str] | None = None,
            sd_client_timer_config_refs: Iterable[str] | None = None,
            priority: int | None = None,
            auto_require: bool | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.event_group_identifier = event_group_identifier
        self.pdu_activation_routing_groups = self._set_parent(pdu_activation_routing_groups)
        self.event_multicast_address_refs = self.eval_children(event_multicast_address_refs)
        self.sd_client_timer_config_refs = self.eval_children(sd_client_timer_config_refs)
        self.priority = priority
        self.auto_require = auto_require

    @property
    def _findable_children(self) -> Iterable[ArObject]:
        yield from self.pdu_activation_routing_groups


class EventHandler(Identifiable):
    def __init__(
            self,
            event_group_identifier: int,
            multicast_threshold: int | None = None,
            pdu_activation_routing_groups: Iterable[PduActivationRoutingGroup] | None = None,
            event_multicast_address_refs: Iterable[str] | None = None,
            sd_server_eg_timing_config_refs: Iterable[str] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.event_group_identifier = event_group_identifier
        self.multicast_threshold = multicast_threshold
        self.pdu_activation_routing_groups = self._set_parent(pdu_activation_routing_groups)
        self.event_multicast_address_refs = self.eval_children(event_multicast_address_refs)
        self.sd_server_eg_timing_config_refs = self.eval_children(sd_server_eg_timing_config_refs)

    @property
    def _findable_children(self) -> Iterable[ArObject]:
        yield from self.pdu_activation_routing_groups
