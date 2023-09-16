from abc import ABC
from typing import Iterable

from autosar.element import Element


class PDUActivationRoutingGroup(Element):
    def __init__(
            self,
            event_group_control_type: str,
            i_pdu_identifier_udp_refs: list[str] | None,
            i_pdu_identifier_tcp_refs: list[str] | None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if len(i_pdu_identifier_udp_refs) == 0:
            i_pdu_identifier_udp_refs = None
        if len(i_pdu_identifier_tcp_refs) == 0:
            i_pdu_identifier_tcp_refs = None
        self.event_group_control_type = event_group_control_type
        self.i_pdu_identifier_udp_refs = i_pdu_identifier_udp_refs
        self.i_pdu_identifier_tcp_refs = i_pdu_identifier_tcp_refs

    def iter_refs(self):
        if self.i_pdu_identifier_udp_refs is not None:
            for ref in self.i_pdu_identifier_udp_refs:
                yield ref
        if self.i_pdu_identifier_tcp_refs is not None:
            for ref in self.i_pdu_identifier_tcp_refs:
                yield ref


class ConsumedEventGroup(Element):
    def __init__(
            self,
            event_group_identifier: int,
            pdu_activation_routing_groups: Iterable[PDUActivationRoutingGroup] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.event_group_identifier = event_group_identifier
        self.event_multicast_addresses = []
        self.sd_client_timer_configs = []
        self.pdu_activation_routing_groups = self._set_parent(pdu_activation_routing_groups)


class EventHandler(Element):
    def __init__(
            self,
            event_group_identifier: int,
            multicast_threshold: int,
            pdu_activation_routing_groups: Iterable[PDUActivationRoutingGroup] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.event_group_identifier = event_group_identifier
        self.multicast_threshold = multicast_threshold
        self.sd_server_eg_timing_configs = []
        self.pdu_activation_routing_groups = self._set_parent(pdu_activation_routing_groups)


class ApplicationEndpointRefConditional(Element):
    def __init__(self, application_endpoint_ref: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.application_endpoint_ref = application_endpoint_ref


class ServiceInstance(Element, ABC):
    def __init__(
            self,
            major_version: int,
            minor_version: int | str,
            service_identifier: int,
            instance_identifier: int,
            local_unicast_addresses: Iterable[ApplicationEndpointRefConditional] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.major_version = major_version
        if isinstance(minor_version, str):
            minor_version = None
        self.minor_version = minor_version
        self.service_identifier = service_identifier
        self.instance_identifier = instance_identifier
        self.method_activation_routing_groups = []
        self.local_unicast_addresses = self._set_parent(local_unicast_addresses)
        self.version_driven_find_behavior = None


class ConsumedServiceInstance(ServiceInstance):
    def __init__(
            self,
            consumed_event_groups: Iterable[ConsumedEventGroup] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.sd_client_timer_configs = []
        self.consumed_event_groups = self._set_parent(consumed_event_groups)


class ProvidedServiceInstance(ServiceInstance):
    def __init__(
            self,
            event_handlers: Iterable[EventHandler] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.sd_server_timer_configs = []
        self.event_handlers = self._set_parent(event_handlers)


class ServiceInstanceCollectionSet(Element):
    def __init__(
            self,
            service_instances: Iterable[ServiceInstance] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.service_instances = self._set_parent(service_instances)
