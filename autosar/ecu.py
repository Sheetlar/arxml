from dataclasses import dataclass
from typing import Iterable

from autosar.ar_object import ArObject
from autosar.element import Element


@dataclass
class ClientIdRange(ArObject):
    lower_limit: int | None
    upper_limit: int | None


@dataclass
class TcpProps(ArObject):
    tcp_congestion_avoidance_avoidance_enabled: bool = False
    tcp_delayed_ack_timeout: int | float | None = None
    tcp_fast_recovery_enabled: bool = False
    tcp_fast_retransmit_enabled: bool = False
    tcp_fin_wait_2_timeout: int | float | None = None
    tcp_keep_alive_enabled: bool = False
    tcp_keep_alive_interval: int | float | None = None
    tcp_keep_alive_probes_max: int | None = None
    tcp_keep_alive_time: int | float | None = None
    tcp_max_rtx: int | float | None = None
    tcp_msl: int | float | None = None
    tcp_nagle_enabled: bool = False
    tcp_receive_window_max: int | float | None = None
    tcp_retransmission_timeout: int | float | None = None
    tcp_slow_start_enabled: bool = False
    tcp_syn_max_rtx: int | float | None = None
    tcp_syn_received_timeout: int | float | None = None
    tcp_ttl: int | None = None


class CouplingPort(Element):
    pass


class CommPort(Element):
    def __init__(
            self,
            communication_direction: str,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.communication_direction = communication_direction


class FramePort(CommPort):
    pass


class IPduPort(CommPort):
    pass


class ISignalPort(CommPort):
    pass


class EthernetCommunicationController(Element):
    def __init__(
            self,
            coupling_ports: Iterable[CouplingPort] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.coupling_ports = self._set_parent(coupling_ports)
        self._find_sets = [self.coupling_ports]


class EthernetCommunicationConnector(Element):
    def __init__(
            self,
            comm_controller_ref: str | None = None,
            ecu_comm_port_instances: Iterable[CommPort] | None = None,
            maximum_transmission_unit: int | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.comm_controller_ref = comm_controller_ref
        self.ecu_comm_port_instances = self._set_parent(ecu_comm_port_instances)
        self.maximum_transmission_unit = maximum_transmission_unit
        self._find_sets = [self.ecu_comm_port_instances]


class EcuInstance(Element):
    def __init__(
            self,
            client_id_range: ClientIdRange | None = None,
            comm_controllers: Iterable[EthernetCommunicationController] | None = None,
            connectors: Iterable[EthernetCommunicationConnector] | None = None,
            diagnostic_address: int | None = None,
            pn_reset_time: float | str | None = None,
            pnc_prepare_sleep_timer: float | str | None = None,
            sleep_mode_supported: bool = False,
            tcp_ip_props_ref: str | None = None,
            wake_up_over_bus_supported: bool = False,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.client_id_range = client_id_range
        self.comm_controllers = self._set_parent(comm_controllers)
        self.connectors = self._set_parent(connectors)
        self.diagnostic_address = diagnostic_address
        self.pn_reset_time = pn_reset_time
        self.pnc_prepare_sleep_timer = pnc_prepare_sleep_timer
        self.sleep_mode_supported = sleep_mode_supported
        self.tcp_ip_props_ref = tcp_ip_props_ref
        self.wake_up_over_bus_supported = wake_up_over_bus_supported
        self._find_sets = [self.comm_controllers, self.connectors]


class EthTcpIpProps(Element):
    def __init__(
            self,
            tcp_props: TcpProps,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.tcp_props = tcp_props
