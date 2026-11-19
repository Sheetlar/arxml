from typing import Iterable, TypeVar

from autosar.model.ar_object import ArObject
from autosar.model.base import Identifiable, TagWithOptionalValue
from autosar.model.communication.ethernet.some_ip import (
    ConsumedEventGroup,
    EventHandler,
    PduActivationRoutingGroup,
    SomeIpServiceVersion,
)
from autosar.model.element import Element
from autosar.model.enums import ServiceVersionAcceptanceKindEnum


class AbstractServiceInstance(Identifiable):
    def __init__(
            self,
            major_version: int,
            capability_records: Iterable[TagWithOptionalValue] | None = None,
            method_activation_routing_groups: Iterable[PduActivationRoutingGroup] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.major_version = major_version
        self.capability_records = self.eval_children(capability_records)
        self.method_activation_routing_groups = self._set_parent(method_activation_routing_groups)

    @property
    def _findable_children(self) -> Iterable[ArObject]:
        yield from self.method_activation_routing_groups


class ConsumedServiceInstance(AbstractServiceInstance):
    def __init__(
            self,
            minor_version: int | float | None = None,
            service_identifier: int | None = None,
            instance_identifier: int | None = None,
            consumed_event_groups: Iterable[ConsumedEventGroup] | None = None,
            allowed_service_provider_refs: Iterable[str] | None = None,
            event_multicast_subscription_address_refs: Iterable[str] | None = None,
            local_unicast_address_refs: Iterable[str] | None = None,
            remote_unicast_address_refs: Iterable[str] | None = None,
            sd_client_timer_config_refs: Iterable[str] | None = None,
            blocklisted_versions: Iterable[SomeIpServiceVersion] | None = None,
            version_driven_find_behavior: ServiceVersionAcceptanceKindEnum | None = None,
            auto_require: bool | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.minor_version = minor_version
        self.service_identifier = service_identifier
        self.instance_identifier = instance_identifier
        self.consumed_event_groups = self._set_parent(consumed_event_groups)
        self.allowed_service_provider_refs = self.eval_children(allowed_service_provider_refs)
        self.event_multicast_subscription_address_refs = self.eval_children(event_multicast_subscription_address_refs)
        self.local_unicast_address_refs = self.eval_children(local_unicast_address_refs)
        self.remote_unicast_address_refs = self.eval_children(remote_unicast_address_refs)
        self.sd_client_timer_config_refs = self.eval_children(sd_client_timer_config_refs)
        self.blocklisted_versions = self.eval_children(blocklisted_versions)
        self.version_driven_find_behavior = version_driven_find_behavior
        self.auto_require = auto_require

    @property
    def _findable_children(self) -> Iterable[ArObject]:
        yield from super()._findable_children
        yield from self.consumed_event_groups


class ProvidedServiceInstance(AbstractServiceInstance):
    def __init__(
            self,
            minor_version: int | None = None,
            service_identifier: int | None = None,
            instance_identifier: int | None = None,
            event_handlers: Iterable[EventHandler] | None = None,
            allowed_service_consumer_refs: Iterable[str] | None = None,
            local_unicast_address_refs: Iterable[str] | None = None,
            remote_unicast_address_refs: Iterable[str] | None = None,
            remote_multicast_subscription_address_refs: Iterable[str] | None = None,
            sd_server_timer_config_refs: Iterable[str] | None = None,
            load_balancing_priority: int | None = None,
            load_balancing_weight: int | None = None,
            priority: int | None = None,
            auto_available: bool | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.minor_version = minor_version
        self.service_identifier = service_identifier
        self.instance_identifier = instance_identifier
        self.event_handlers = self._set_parent(event_handlers)
        self.allowed_service_consumer_refs = self.eval_children(allowed_service_consumer_refs)
        self.local_unicast_address_refs = self.eval_children(local_unicast_address_refs)
        self.remote_unicast_address_refs = self.eval_children(remote_unicast_address_refs)
        self.remote_multicast_subscription_address_refs = self.eval_children(remote_multicast_subscription_address_refs)
        self.sd_server_timer_config_refs = self.eval_children(sd_server_timer_config_refs)
        self.load_balancing_priority = load_balancing_priority
        self.load_balancing_weight = load_balancing_weight
        self.priority = priority
        self.auto_available = auto_available

    @property
    def _findable_children(self) -> Iterable[ArObject]:
        yield from super()._findable_children
        yield from self.event_handlers


ServiceInstance = TypeVar('ServiceInstance', bound=AbstractServiceInstance)


class ServiceInstanceCollectionSet(Element):
    def __init__(
            self,
            service_instances: Iterable[ServiceInstance] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.service_instances = self._set_parent(service_instances)

    @property
    def _findable_children(self) -> Iterable[ArObject]:
        yield from self.service_instances
