from dataclasses import dataclass
from typing import Iterable, TypeVar, Any

from autosar.model.ar_object import ArObject
from autosar.model.base import DataFilter
from autosar.model.communication_controller import CommunicationController
from autosar.model.element import Element


@dataclass
class ClientIdRange(ArObject):
    lower_limit: int | None
    upper_limit: int | None


class EcuPartition(Element):
    def __init__(
            self,
            exec_in_user_mode: bool,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.exec_in_user_mode = exec_in_user_mode


class CommPort(Element):
    def __init__(
            self,
            communication_direction: str,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.communication_direction = communication_direction


AnyCommPort = TypeVar('AnyCommPort', bound=CommPort)


class FramePort(CommPort):
    pass


class IPduPort(CommPort):
    def __init__(
            self,
            i_pdu_signal_processing: str | None = None,
            timestamp_rx_acceptance_window: float | None = None,
            rx_security_verification: bool | None = None,
            use_auth_data_freshness: bool | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.i_pdu_signal_processing = i_pdu_signal_processing
        self.timestamp_rx_acceptance_window = timestamp_rx_acceptance_window
        self.rx_security_verification = rx_security_verification
        self.use_auth_data_freshness = use_auth_data_freshness


class ISignalPort(CommPort):
    def __init__(
            self,
            data_filter: DataFilter | None = None,
            handle_invalid: str | None = None,
            first_timeout: float | None = None,
            timeout: float | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.data_filter = data_filter
        self.handle_invalid = handle_invalid
        self.first_timeout = first_timeout
        self.timeout = timeout


class CommunicationConnector(Element):
    def __init__(
            self,
            comm_controller_ref: str,
            ecu_comm_port_instances: Iterable[AnyCommPort] | None = None,
            pnc_gateway_type: str | None = None,
            pnc_filter_array_mask: list[int] | None = None,
            create_ecu_wakeup_source: bool | None = None,
            dynamic_pnc_to_channel_mapping_enabled: bool | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.comm_controller_ref = comm_controller_ref
        self.ecu_comm_port_instances = self._set_parent(ecu_comm_port_instances)
        self.pnc_gateway_type = pnc_gateway_type
        self.pnc_filter_array_mask = pnc_filter_array_mask
        self.create_ecu_wakeup_source = create_ecu_wakeup_source
        self.dynamic_pnc_to_channel_mapping_enabled = dynamic_pnc_to_channel_mapping_enabled
        self._find_sets = (self.ecu_comm_port_instances,)


class CanCommunicationConnector(CommunicationConnector):
    def __init__(
            self,
            pnc_wakeup_can_id: int | None = None,
            pnc_wakeup_can_id_mask: int | None = None,
            pnc_wakeup_data_mask: int | None = None,
            pnc_wakeup_dlc: int | None = None,
            pnc_wakeup_can_id_extended: bool | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.pnc_wakeup_can_id = pnc_wakeup_can_id
        self.pnc_wakeup_can_id_mask = pnc_wakeup_can_id_mask
        self.pnc_wakeup_data_mask = pnc_wakeup_data_mask
        self.pnc_wakeup_dlc = pnc_wakeup_dlc
        self.pnc_wakeup_can_id_extended = pnc_wakeup_can_id_extended


class EthernetCommunicationConnector(CommunicationConnector):
    def __init__(
            self,
            maximum_transmission_unit: int | None = None,
            neighbor_cache_size: int | None = None,
            path_mtu_enabled: bool | None = None,
            path_mtu_timeout: float | None = None,
            eth_ip_props_ref: str | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.maximum_transmission_unit = maximum_transmission_unit
        self.neighbor_cache_size = neighbor_cache_size
        self.path_mtu_enabled = path_mtu_enabled
        self.path_mtu_timeout = path_mtu_timeout
        self.eth_ip_props_ref = eth_ip_props_ref


class EcuInstance(Element):
    def __init__(
            self,
            diagnostic_address: int | None = None,
            comm_controllers: Iterable[CommunicationController] | None = None,
            connectors: Iterable[CommunicationConnector] | None = None,
            client_id_range: ClientIdRange | None = None,
            partitions: Iterable[EcuPartition] | None = None,
            com_configuration_gw_time_base: float | None = None,
            com_configuration_rx_time_base: float | None = None,
            com_configuration_tx_time_base: float | None = None,
            associated_com_i_pdu_group_refs: list[str] | None = None,
            associated_consumed_provided_service_instance_group_refs: list[str] | None = None,
            associated_pdu_r_i_pdu_group_refs: list[str] | None = None,
            ecu_task_proxy_refs: list[str] | None = None,
            tcp_ip_icmp_props_ref: str | None = None,
            tcp_ip_props_ref: str | None = None,
            pnc_prepare_sleep_timer: float | None = None,
            pn_reset_time: float | None = None,
            com_enable_mdt_for_cyclic_transmission: bool | None = None,
            eth_switch_port_group_derivation: bool | None = None,
            pnc_nm_request: bool | None = None,
            pnc_synchronous_wakeup: bool | None = None,
            sleep_mode_supported: bool | None = None,
            wake_up_over_bus_supported: bool | None = None,
            v2x_supported: str | None = None,
            dlt_config: None = None,  # TODO: Implement
            doip_config: None = None,  # TODO: Implement
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if associated_com_i_pdu_group_refs is None:
            associated_com_i_pdu_group_refs = []
        if associated_consumed_provided_service_instance_group_refs is None:
            associated_consumed_provided_service_instance_group_refs = []
        if associated_pdu_r_i_pdu_group_refs is None:
            associated_pdu_r_i_pdu_group_refs = []
        if ecu_task_proxy_refs is None:
            ecu_task_proxy_refs = []
        self.diagnostic_address = diagnostic_address
        self.comm_controllers = self._set_parent(comm_controllers)
        self.connectors = self._set_parent(connectors)
        self.client_id_range = client_id_range
        self.partitions = self._set_parent(partitions)
        self.com_configuration_gw_time_base = com_configuration_gw_time_base
        self.com_configuration_rx_time_base = com_configuration_rx_time_base
        self.com_configuration_tx_time_base = com_configuration_tx_time_base
        self.associated_com_i_pdu_group_refs = associated_com_i_pdu_group_refs
        self.associated_consumed_provided_service_instance_group_refs = associated_consumed_provided_service_instance_group_refs
        self.associated_pdu_r_i_pdu_group_refs = associated_pdu_r_i_pdu_group_refs
        self.ecu_task_proxy_refs = ecu_task_proxy_refs
        self.tcp_ip_icmp_props_ref = tcp_ip_icmp_props_ref
        self.tcp_ip_props_ref = tcp_ip_props_ref
        self.pnc_prepare_sleep_timer = pnc_prepare_sleep_timer
        self.pn_reset_time = pn_reset_time
        self.com_enable_mdt_for_cyclic_transmission = com_enable_mdt_for_cyclic_transmission
        self.eth_switch_port_group_derivation = eth_switch_port_group_derivation
        self.pnc_nm_request = pnc_nm_request
        self.pnc_synchronous_wakeup = pnc_synchronous_wakeup
        self.sleep_mode_supported = sleep_mode_supported
        self.v2x_supported = v2x_supported
        self.wake_up_over_bus_supported = wake_up_over_bus_supported
        self.dlt_config = dlt_config
        self.doip_config = doip_config
        self._find_sets = (self.comm_controllers, self.connectors, self.partitions)


@dataclass
class DefaultValueElement(ArObject):
    element_byte_value: int
    element_position: int


@dataclass
class PduMappingDefaultValue(ArObject):
    default_value_elements: list[DefaultValueElement]


@dataclass
class TargetIPduRef(ArObject):
    target_i_pdu_ref: str
    default_value: PduMappingDefaultValue | None = None


@dataclass
class FrameMapping(ArObject):
    source_frame_ref: str
    target_frame_ref: str
    introduction: Any = None


@dataclass
class IPduMapping(ArObject):
    source_i_pdu_ref: str
    target_i_pdu: TargetIPduRef
    pdu_max_length: int | None = None
    pdu_r_tp_chunk_size: int | None = None
    introduction: Any = None


@dataclass
class ISignalMapping(ArObject):
    source_signal_ref: str
    target_signal_ref: str
    introduction: Any = None


class Gateway(Element):
    def __init__(
            self,
            ecu_ref: str | None = None,
            frame_mappings: list[FrameMapping] | None = None,
            i_pdu_mappings: list[IPduMapping] | None = None,
            signal_mappings: list[ISignalMapping] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.ecu_ref = ecu_ref
        self.frame_mappings = frame_mappings
        self.i_pdu_mappings = i_pdu_mappings
        self.signal_mappings = signal_mappings
