from typing import Iterable, TypeVar

from autosar.misc import filter_none
from autosar.model.ar_object import ArObject
from autosar.model.base import Identifiable
from autosar.model.transport_protocol import TpConnection, TpConfig


class AbstractDoIpLogicAddressProps(Identifiable):
    """Abstract"""


class DoIpLogicTargetAddressProps(AbstractDoIpLogicAddressProps):
    pass


class DoIpLogicTesterAddressProps(AbstractDoIpLogicAddressProps):
    def __init__(
            self,
            do_ip_tester_routing_activation_refs: Iterable[str] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.do_ip_tester_routing_activation_refs = self.eval_children(do_ip_tester_routing_activation_refs)


DoIpLogicAddressProps = TypeVar('DoIpLogicAddressProps', bound=AbstractDoIpLogicAddressProps)


class DoIpLogicAddress(Identifiable):
    def __init__(
            self,
            address: int | None = None,
            do_ip_logic_address_props: DoIpLogicAddressProps | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.address = address
        self.do_ip_logic_address_props = self._set_parent_single(do_ip_logic_address_props)

    @property
    def _findable_children(self) -> Iterable[ArObject]:
        if self.do_ip_logic_address_props is not None:
            yield self.do_ip_logic_address_props


class DoIpRoutingActivation(Identifiable):
    def __init__(
            self,
            do_ip_target_address_refs: Iterable[str] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.do_ip_target_address_refs = self.eval_children(do_ip_target_address_refs)


class DoIpTpConnection(TpConnection):
    def __init__(
            self,
            do_ip_source_address_ref: str,
            do_ip_target_address_ref: str,
            tp_sdu_ref: str,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.do_ip_source_address_ref = do_ip_source_address_ref
        self.do_ip_target_address_ref = do_ip_target_address_ref
        self.tp_sdu_ref = tp_sdu_ref


class DoIpTpConfig(TpConfig):
    def __init__(
            self,
            tp_connections: Iterable[DoIpTpConnection],
            do_ip_logic_addresses: Iterable[DoIpLogicAddress] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.tp_connections = self._set_parent(tp_connections)
        self.do_ip_logic_addresses = self._set_parent(do_ip_logic_addresses)

    @property
    def _findable_children(self) -> Iterable[ArObject]:
        yield from filter_none(c.ident for c in self.tp_connections)
        yield from self.do_ip_logic_addresses


class DoIpInterface(Identifiable):
    def __init__(
            self,
            alive_check_response_timeout: float | None = None,
            doip_channel_collection_ref: str | None = None,
            do_ip_routing_activations: Iterable[DoIpRoutingActivation] | None = None,
            general_inactivity_time: float | None = None,
            initial_inactivity_time: float | None = None,
            initial_vehicle_announcement_time: float | None = None,
            is_activation_line_dependent: bool | None = None,
            max_tester_connections: int | None = None,
            socket_connection_refs: Iterable[str] | None = None,
            use_mac_address_for_identification: bool | None = None,
            use_vehicle_identification_sync_status: bool | None = None,
            vehicle_announcement_count: int | None = None,
            vehicle_announcement_interval: float | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.alive_check_response_timeout = alive_check_response_timeout
        self.doip_channel_collection_ref = doip_channel_collection_ref
        self.do_ip_routing_activations = self._set_parent(do_ip_routing_activations)
        self.general_inactivity_time = general_inactivity_time
        self.initial_inactivity_time = initial_inactivity_time
        self.initial_vehicle_announcement_time = initial_vehicle_announcement_time
        self.is_activation_line_dependent = is_activation_line_dependent
        self.max_tester_connections = max_tester_connections
        self.socket_connection_refs = self.eval_children(socket_connection_refs)
        self.use_mac_address_for_identification = use_mac_address_for_identification
        self.use_vehicle_identification_sync_status = use_vehicle_identification_sync_status
        self.vehicle_announcement_count = vehicle_announcement_count
        self.vehicle_announcement_interval = vehicle_announcement_interval

    @property
    def _findable_children(self) -> Iterable[ArObject]:
        yield from self.do_ip_routing_activations


class DoIpConfig(ArObject):
    def __init__(
            self,
            doip_interfaces: Iterable[DoIpInterface] | None = None,  # name
            do_ip_protocol_version: int | None = None,
            logic_address: DoIpLogicAddress | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.doip_interfaces = self._set_parent(doip_interfaces)
        self.do_ip_protocol_version = do_ip_protocol_version
        self.logic_address = self._set_parent_single(logic_address)
