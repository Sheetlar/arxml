from dataclasses import dataclass
from typing import Iterable, TypeVar

from autosar.model.ar_object import ArObject
from autosar.model.base import Identifiable
from autosar.model.enums import (
    Ipv4AddressSourceEnum,
    IpAddressKeepEnum,
    Ipv6AddressSourceEnum,
)


@dataclass(repr=False)
class TpPort(ArObject):
    port_number: int = 0
    dynamically_assigned: bool = False

    def __post_init__(self):
        if self.port_number == 0:
            self.dynamically_assigned = True


@dataclass(repr=False)
class TcpUdpConfig(ArObject):
    pass


AnyTcpUdpConfig = TypeVar('AnyTcpUdpConfig', bound=TcpUdpConfig)


@dataclass(repr=False)
class UdpTp(TcpUdpConfig):
    udp_tp_port: TpPort


@dataclass(repr=False)
class TcpTp(TcpUdpConfig):
    tcp_tp_port: TpPort
    keep_alive_interval: float | None = None
    keep_alive_probes_max: int | None = None
    keep_alive_time: float | None = None
    keep_alives: bool | None = None
    nagles_algorithm: bool | None = None
    receive_window_min: int | None = None
    tcp_retransmission_timeout: float | None = None


@dataclass(repr=False)
class NetworkEndpointAddress(ArObject):
    pass


AnyNetworkEndpointAddress = TypeVar('AnyNetworkEndpointAddress', bound=NetworkEndpointAddress)


@dataclass(repr=False)
class IPv4Configuration(NetworkEndpointAddress):
    assignment_priority: int | None = None
    default_gateway: str | None = None
    dns_server_addresses: list[str] | None = None
    ip_address_keep_behavior: IpAddressKeepEnum | None = None
    ipv4_address: str | None = None
    ipv4_address_source: Ipv4AddressSourceEnum | None = None
    network_mask: str | None = None
    ttl: int | None = None


@dataclass(repr=False)
class IPv6Configuration(NetworkEndpointAddress):
    assignment_priority: int | None = None
    default_router: str | None = None
    dns_server_addresses: list[str] | None = None
    enable_anycast: bool | None = None
    hop_count: int | None = None
    ip_address_keep_behavior: IpAddressKeepEnum | None = None
    ip_address_prefix_length: int | None = None
    ipv6_address: str | None = None
    ipv6_address_source: Ipv6AddressSourceEnum | None = None


@dataclass(repr=False)
class MacMulticastConfiguration(NetworkEndpointAddress):
    mac_multicast_group_ref: str


class NetworkEndpoint(Identifiable):
    def __init__(
            self,
            network_endpoint_addresses: Iterable[AnyNetworkEndpointAddress] | None,
            fully_qualified_domain_name: str | None = None,
            ip_sec_config: None = None,  # IpSecConfig
            infrastructure_services: None = None,  # InfrastructureServices
            priority: int | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.network_endpoint_addresses = self.eval_children(network_endpoint_addresses)
        self.fully_qualified_domain_name = fully_qualified_domain_name
        self.ip_sec_config = ip_sec_config
        self.infrastructure_services = infrastructure_services
        self.priority = priority


class ApplicationEndpoint(Identifiable):
    def __init__(
            self,
            network_endpoint_ref: str,
            tp_configuration: AnyTcpUdpConfig | None = None,
            max_number_of_connections: int | None = None,
            priority: int | None = None,
            tls_crypto_mapping_ref: str | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.network_endpoint_ref = network_endpoint_ref
        self.tp_configuration = tp_configuration
        self.max_number_of_connections = max_number_of_connections
        self.priority = priority
        self.tls_crypto_mapping_ref = tls_crypto_mapping_ref
