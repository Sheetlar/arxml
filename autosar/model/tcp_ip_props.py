from dataclasses import dataclass

from autosar import ArObject
from autosar.model.element import Element


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


class EthTcpIpProps(Element):
    def __init__(
            self,
            tcp_props: TcpProps,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.tcp_props = tcp_props
