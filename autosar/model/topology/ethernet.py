from dataclasses import dataclass
from typing import TypeVar, Iterable

from autosar.model.ar_object import ArObject, ArObjectWithParent
from autosar.model.base import Identifiable, Referrable, Describable
from autosar.model.enums import (
    CouplingPortRoleEnum,
    CouplingPortRatePolicyActionEnum,
    EthernetConnectionNegotiationEnum,
    EthernetMacLayerTypeEnum,
    EthernetPhysicalLayerTypeEnum,
    MacSecRoleEnum,
    MacSecFailPermissiveModeEnum,
    EthernetSwitchVlanEgressTaggingEnum,
    EthernetSwitchVlanIngressTagEnum,
    EthernetCouplingPortPreemptionEnum,
    EthernetCouplingPortSchedulerEnum,
)
from autosar.model.communication.ethernet.endpoint import NetworkEndpoint
from autosar.model.communication.ethernet.socket import SoAdConfig
from autosar.model.topology.abstract import (
    CommunicationControllerContent,
    CommunicationController,
    CommunicationConnector,
    PhysicalChannel,
    CommunicationClusterContent,
    CommunicationCluster,
)


class CouplingPortAbstractShaper(Identifiable):
    """Abstract"""


class CouplingPortAsynchronousTrafficShaper(CouplingPortAbstractShaper):
    def __init__(
            self,
            committed_burst_size: int | None = None,
            committed_information_rate: int | None = None,
            traffic_shaper_group_ref: str | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.committed_burst_size = committed_burst_size
        self.committed_information_rate = committed_information_rate
        self.traffic_shaper_group_ref = traffic_shaper_group_ref


class CouplingPortCreditBasedShaper(CouplingPortAbstractShaper):
    def __init__(
            self,
            idle_slope: int | None = None,
            lower_boundary: int | None = None,
            upper_boundary: int | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.idle_slope = idle_slope
        self.lower_boundary = lower_boundary
        self.upper_boundary = upper_boundary


class CouplingPortEnhancedTrafficShaper(CouplingPortAbstractShaper):
    def __init__(
            self,
            ets_available_bandwidth_in_percent: int | None = None,
            ets_available_bandwidth_in_weight_value: int | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.ets_available_bandwidth_in_percent = ets_available_bandwidth_in_percent
        self.ets_available_bandwidth_in_weight_value = ets_available_bandwidth_in_weight_value


CouplingPortShaper = TypeVar('CouplingPortShaper', bound=CouplingPortAbstractShaper)


class CouplingPortStructuralElement(Identifiable):
    """Abstract"""


class CouplingPortFifo(CouplingPortStructuralElement):
    def __init__(
            self,
            assigned_traffic_classes: Iterable[int] | None = None,
            minimum_fifo_length: int | None = None,
            shaper: CouplingPortShaper | None = None,
            traffic_class_preemption_support: EthernetCouplingPortPreemptionEnum | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.assigned_traffic_classes = self.eval_children(assigned_traffic_classes)
        self.minimum_fifo_length = minimum_fifo_length
        self.shaper = shaper
        self.traffic_class_preemption_support = traffic_class_preemption_support

    @property
    def _findable_children(self) -> Iterable[ArObject]:
        if self.shaper is not None:
            yield self.shaper


class CouplingPortScheduler(CouplingPortStructuralElement):
    def __init__(
            self,
            port_scheduler: EthernetCouplingPortSchedulerEnum | None = None,
            predecessor_refs: Iterable[str] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.port_scheduler = port_scheduler
        self.predecessor_refs = self.eval_children(predecessor_refs)


AnyCouplingPortStructuralElement = TypeVar('AnyCouplingPortStructuralElement', bound=CouplingPortStructuralElement)


class EthernetPriorityRegeneration(Referrable):
    def __init__(
            self,
            ingress_priority: int,
            regenerated_priority: int,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.ingress_priority = ingress_priority
        self.regenerated_priority = regenerated_priority


class CouplingPortTrafficClassAssignment(Referrable):
    def __init__(
            self,
            traffic_class: int,
            priorities: Iterable[int] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.traffic_class = traffic_class
        self.priorities = self.eval_children(priorities)


@dataclass(repr=False)
class GlobalTimeCouplingPortProps(ArObject):
    propagation_delay: float


@dataclass(repr=False)
class CouplingPortRatePolicy(ArObject):
    data_length: int | None = None
    policy_action: CouplingPortRatePolicyActionEnum | None = None
    priority: int | None = None
    time_interval: float | None = None
    v_lan_refs: list[str] | None = None


@dataclass(repr=False)
class EthernetVlanTranslationTable(ArObject):
    translated_vlan_id: int
    ingress_vlan_id: int | None = None


class CouplingPortDetails(ArObjectWithParent):
    def __init__(
            self,
            coupling_port_structural_elements: Iterable[AnyCouplingPortStructuralElement] | None = None,
            default_traffic_class: int | None = None,
            ethernet_priority_regenerations: Iterable[EthernetPriorityRegeneration] | None = None,
            ethernet_traffic_class_assignments: Iterable[CouplingPortTrafficClassAssignment] | None = None,
            frame_preemption_support: bool | None = None,
            global_time_props: GlobalTimeCouplingPortProps | None = None,
            last_egress_scheduler_ref: str | None = None,
            rate_policies: Iterable[CouplingPortRatePolicy] | None = None,
            vlan_translation_tables: Iterable[EthernetVlanTranslationTable] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.coupling_port_structural_elements = self._set_parent(coupling_port_structural_elements)
        self.default_traffic_class = default_traffic_class
        self.ethernet_priority_regenerations = self._set_parent(ethernet_priority_regenerations)
        self.ethernet_traffic_class_assignments = self._set_parent(ethernet_traffic_class_assignments)
        self.frame_preemption_support = frame_preemption_support
        self.global_time_props = global_time_props
        self.last_egress_scheduler_ref = last_egress_scheduler_ref
        self.rate_policies = self.eval_children(rate_policies)
        self.vlan_translation_tables = self.eval_children(vlan_translation_tables)

    @property
    def _findable_children(self) -> Iterable[ArObject]:
        yield from self.coupling_port_structural_elements
        yield from self.ethernet_priority_regenerations
        yield from self.ethernet_traffic_class_assignments


class Ipv4DhcpServerConfiguration(Describable):
    def __init__(
            self,
            address_range_lower_bound: str | None = None,
            address_range_upper_bound: str | None = None,
            default_gateway: str | None = None,
            dns_server_addresses: Iterable[str] | None = None,
            network_mask: str | None = None,
            default_lease_time: float | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.address_range_lower_bound = address_range_lower_bound
        self.address_range_upper_bound = address_range_upper_bound
        self.default_gateway = default_gateway
        self.dns_server_addresses = self.eval_children(dns_server_addresses)
        self.network_mask = network_mask
        self.default_lease_time = default_lease_time


class Ipv6DhcpServerConfiguration(Describable):
    def __init__(
            self,
            address_range_lower_bound: str | None = None,
            address_range_upper_bound: str | None = None,
            default_gateway: str | None = None,
            dns_server_addresses: Iterable[str] | None = None,
            network_mask: str | None = None,
            default_lease_time: float | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.address_range_lower_bound = address_range_lower_bound
        self.address_range_upper_bound = address_range_upper_bound
        self.default_gateway = default_gateway
        self.dns_server_addresses = self.eval_children(dns_server_addresses)
        self.network_mask = network_mask
        self.default_lease_time = default_lease_time


@dataclass(repr=False)
class DhcpServerConfiguration(ArObject):
    ipv4_dhcp_server_configuration: Ipv4DhcpServerConfiguration | None = None
    ipv6_dhcp_server_configuration: Ipv6DhcpServerConfiguration | None = None


@dataclass(repr=False)
class VlanMembership(ArObject):
    vlan_ref: str
    default_priority: int
    dhcp_address_assignment: DhcpServerConfiguration | None = None
    send_activity: EthernetSwitchVlanEgressTaggingEnum | None = None


@dataclass(repr=False)
class MacSecLocalKayProps(ArObject):
    destination_mac_address: str | None = None
    global_kay_props_ref: str | None = None
    key_server_priority: int | None = None
    mka_participant_refs: list[str] | None = None
    role: MacSecRoleEnum | None = None
    source_mac_address: str | None = None


@dataclass(repr=False)
class MacSecProps(ArObject):
    auto_start: bool | None = None
    mac_sec_kay_config: MacSecLocalKayProps | None = None
    on_fail_permissive_mode: MacSecFailPermissiveModeEnum | None = None
    on_fail_permissive_mode_timeout: float | None = None
    sak_rekey_time_span: float | None = None


@dataclass(repr=False)
class PlcaProps(ArObject):
    plca_local_node_id: int | None = None
    plca_max_burst_count: int | None = None
    plca_max_burst_timer: int | None = None


class MacAddressVlanMembership(Identifiable):
    def __init__(
            self,
            mac_multicast_address_refs: Iterable[str] | None = None,
            vlan_refs: Iterable[str] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.mac_multicast_address_refs = self.eval_children(mac_multicast_address_refs)
        self.vlan_refs = self.eval_children(vlan_refs)


class CouplingPort(Identifiable):
    def __init__(
            self,
            connection_negotiation_behavior: EthernetConnectionNegotiationEnum | None = None,
            coupling_port_role: CouplingPortRoleEnum | None = None,
            coupling_port_details: CouplingPortDetails | None = None,
            default_vlan_ref: str | None = None,
            vlan_modifier_ref: str | None = None,
            vlan_membership: Iterable[VlanMembership] | None = None,
            mac_multicast_address_refs: Iterable[str] | None = None,
            mac_address_vlan_assignments: Iterable[MacAddressVlanMembership] | None = None,  # VAR
            mac_layer_type: EthernetMacLayerTypeEnum | None = None,
            physical_layer_type: EthernetPhysicalLayerTypeEnum | None = None,
            mac_sec_props: Iterable[MacSecProps] | None = None,
            plca_props: PlcaProps | None = None,
            pnc_mapping_refs: Iterable[str] | None = None,
            receive_activity: EthernetSwitchVlanIngressTagEnum | None = None,
            wakeup_sleep_on_dataline_config_ref: str | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if coupling_port_details is not None:
            coupling_port_details.parent = self
        if mac_multicast_address_refs is not None and mac_address_vlan_assignments is None:
            mac_address_vlan_assignments = (MacAddressVlanMembership(mac_multicast_address_refs),)
        self.connection_negotiation_behavior = connection_negotiation_behavior
        self.coupling_port_role = coupling_port_role
        self.coupling_port_details = coupling_port_details
        self.default_vlan_ref = default_vlan_ref
        self.vlan_modifier_ref = vlan_modifier_ref
        self.vlan_membership = self.eval_children(vlan_membership)
        self.mac_address_vlan_assignment = self._set_parent(mac_address_vlan_assignments)
        self.mac_layer_type = mac_layer_type
        self.physical_layer_type = physical_layer_type
        self.mac_sec_props = self.eval_children(mac_sec_props)
        self.plca_props = plca_props
        self.pnc_mapping_refs = self.eval_children(pnc_mapping_refs)
        self.receive_activity = receive_activity
        self.wakeup_sleep_on_dataline_config_ref = wakeup_sleep_on_dataline_config_ref

    @property
    def _findable_children(self) -> Iterable[ArObject]:
        yield from self.mac_address_vlan_assignment
        if self.coupling_port_details is not None:
            yield from self.coupling_port_details.coupling_port_structural_elements
            yield from self.coupling_port_details.ethernet_priority_regenerations
            yield from self.coupling_port_details.ethernet_traffic_class_assignments


@dataclass(repr=False)
class CouplingPortConnection(ArObject):
    first_port_ref: str | None = None
    second_port_ref: str | None = None
    node_port_refs: list[str] | None = None
    plca_local_node_count: int | None = None
    plca_transmit_opportunity_timer: int | None = None


class MacMulticastGroup(Identifiable):
    def __init__(self, mac_multicast_address: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mac_multicast_address = mac_multicast_address


class VlanConfig(Identifiable):
    def __init__(self, vlan_identifier: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vlan_identifier = vlan_identifier


class EthernetCommunicationControllerContent(CommunicationControllerContent):
    def __init__(
            self,
            can_xl_config_ref: str | None = None,
            coupling_ports: Iterable[CouplingPort] | None = None,
            mac_layer_type: EthernetMacLayerTypeEnum | None = None,
            mac_unicast_address: str | None = None,
            maximum_receive_buffer_length: int | None = None,
            maximum_transmit_buffer_length: int | None = None,
            slave_act_as_passive_communication_slave: bool | None = None,
            slave_qualified_unexpected_link_down_time: float | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.can_xl_config_ref = can_xl_config_ref
        self.coupling_ports = self._set_parent(coupling_ports)
        self.mac_layer_type = mac_layer_type
        self.mac_unicast_address = mac_unicast_address
        self.maximum_receive_buffer_length = maximum_receive_buffer_length
        self.maximum_transmit_buffer_length = maximum_transmit_buffer_length
        self.slave_act_as_passive_communication_slave = slave_act_as_passive_communication_slave
        self.slave_qualified_unexpected_link_down_time = slave_qualified_unexpected_link_down_time


class EthernetCommunicationController(
    CommunicationController[EthernetCommunicationControllerContent]
):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.category is None:
            self.category = 'WIRED'

    @property
    def _findable_children(self) -> Iterable[ArObject]:
        for v in self.variants:
            yield from v.coupling_ports


class EthernetCommunicationConnector(CommunicationConnector):
    def __init__(
            self,
            eth_ip_props_ref: str | None = None,
            maximum_transmission_unit: int | None = None,
            neighbor_cache_size: int | None = None,
            path_mtu_enabled: bool | None = None,
            path_mtu_timeout: float | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.eth_ip_props_ref = eth_ip_props_ref
        self.maximum_transmission_unit = maximum_transmission_unit
        self.neighbor_cache_size = neighbor_cache_size
        self.path_mtu_enabled = path_mtu_enabled
        self.path_mtu_timeout = path_mtu_timeout


class EthernetPhysicalChannel(PhysicalChannel):
    def __init__(
            self,
            network_endpoints: Iterable[NetworkEndpoint] | None = None,
            so_ad_config: SoAdConfig | None = None,
            vlan: VlanConfig | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if so_ad_config is not None:
            so_ad_config.parent = self
        if vlan is not None:
            vlan.parent = self
        self.network_endpoints = self._set_parent(network_endpoints)
        self.so_ad_config = so_ad_config
        self.vlan = vlan

    @property
    def _findable_children(self) -> Iterable[ArObject]:
        yield from super()._findable_children
        yield from self.network_endpoints
        if self.so_ad_config is not None:
            yield from self.so_ad_config.socket_addresses
        if self.vlan is not None:
            yield self.vlan


class EthernetClusterContent(CommunicationClusterContent[EthernetPhysicalChannel]):
    def __init__(
            self,
            coupling_port_connections: Iterable[CouplingPortConnection] | None = None,
            coupling_port_startup_active_time: float | None = None,
            coupling_port_switchoff_delay: float | None = None,
            mac_multicast_groups: Iterable[MacMulticastGroup] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.coupling_port_connections = self.eval_children(coupling_port_connections)
        self.coupling_port_startup_active_time = coupling_port_startup_active_time
        self.coupling_port_switchoff_delay = coupling_port_switchoff_delay
        self.mac_multicast_groups = self._set_parent(mac_multicast_groups)

    @property
    def _findable_children(self) -> Iterable[ArObject]:
        yield from super()._findable_children
        yield from self.mac_multicast_groups


class EthernetCluster(CommunicationCluster[EthernetClusterContent]):
    pass
