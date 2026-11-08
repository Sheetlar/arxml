from dataclasses import dataclass
from typing import Iterable, TypeVar

from autosar.model.ar_object import ArObject, ArObjectWithParent
from autosar.model.base import Identifiable
from autosar.model.communication.frame import Frame
from autosar.model.enums import (
    Ipv4AddressSourceEnum,
    IpAddressKeepEnum,
    Ipv6AddressSourceEnum,
    UdpChecksumCalculationEnum,
    TcpRoleEnum,
)


@dataclass
class TpPort(ArObject):
    port_number: int = 0
    dynamically_assigned: bool = False

    def __post_init__(self):
        if self.port_number == 0:
            self.dynamically_assigned = True


@dataclass
class TcpUdpConfig(ArObject):
    pass


AnyTcpUdpConfig = TypeVar('AnyTcpUdpConfig', bound=TcpUdpConfig)


@dataclass
class UdpTp(TcpUdpConfig):
    udp_tp_port: TpPort


@dataclass
class TcpTp(TcpUdpConfig):
    tcp_tp_port: TpPort
    keep_alive_interval: float | None = None
    keep_alive_probes_max: int | None = None
    keep_alive_time: float | None = None
    keep_alives: bool | None = None
    nagles_algorithm: bool | None = None
    receive_window_min: int | None = None
    tcp_retransmission_timeout: float | None = None


@dataclass
class NetworkEndpointAddress(ArObject):
    pass


AnyNetworkEndpointAddress = TypeVar('AnyNetworkEndpointAddress', bound=NetworkEndpointAddress)


@dataclass
class IPv4Configuration(NetworkEndpointAddress):
    assignment_priority: int | None = None
    default_gateway: str | None = None
    dns_server_addresses: list[str] | None = None
    ip_address_keep_behavior: IpAddressKeepEnum | None = None
    ipv4_address: str | None = None
    ipv4_address_source: Ipv4AddressSourceEnum | None = None
    network_mask: str | None = None
    ttl: int | None = None


@dataclass
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


@dataclass
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


class StaticSocketConnection(Identifiable):
    def __init__(
            self,
            i_pdu_identifier_refs: Iterable[str] | None = None,
            remote_address_refs: Iterable[str] | None = None,
            tcp_connect_timeout: float | None = None,
            tcp_role: TcpRoleEnum | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.i_pdu_identifier_refs = self.eval_children(i_pdu_identifier_refs)
        self.remote_address_refs = self.eval_children(remote_address_refs)
        self.tcp_connect_timeout = tcp_connect_timeout
        self.tcp_role = tcp_role


class SocketAddress(Identifiable):
    def __init__(
            self,
            allowed_ipv6_ext_headers_ref: str | None = None,
            allowed_tcp_options_ref: str | None = None,
            application_endpoint: ApplicationEndpoint | None = None,
            connector_ref: str | None = None,
            differentiated_service_field: int | None = None,
            flow_label: int | None = None,
            multicast_connector_refs: Iterable[str] | None = None,
            path_mtu_discovery_enabled: bool | None = None,
            pdu_collection_max_buffer_size: int | None = None,
            pdu_collection_timeout: float | None = None,
            static_socket_connections: Iterable[StaticSocketConnection] | None = None,
            ttl: int | None = None,
            udp_checksum_handling: UdpChecksumCalculationEnum | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if application_endpoint is not None:
            application_endpoint.parent = self
        self.allowed_ipv6_ext_headers_ref = allowed_ipv6_ext_headers_ref
        self.allowed_tcp_options_ref = allowed_tcp_options_ref
        self.application_endpoint = application_endpoint
        self.connector_ref = connector_ref
        self.differentiated_service_field = differentiated_service_field
        self.flow_label = flow_label
        self.multicast_connector_refs = self.eval_children(multicast_connector_refs)
        self.path_mtu_discovery_enabled = path_mtu_discovery_enabled
        self.pdu_collection_max_buffer_size = pdu_collection_max_buffer_size
        self.pdu_collection_timeout = pdu_collection_timeout
        self.static_socket_connections = self._set_parent(static_socket_connections)
        self.ttl = ttl
        self.udp_checksum_handling = udp_checksum_handling

    @property
    def _findable_children(self) -> Iterable[ArObject]:
        if self.application_endpoint is not None:
            yield self.application_endpoint


class SoAdConfig(ArObjectWithParent):
    def __init__(
            self,
            socket_addresses: Iterable[SocketAddress] | None = None,
            connection_bundle: None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.socket_addresses = self._set_parent(socket_addresses)
        self.connection_bundle = connection_bundle


class GenericEthernetFrame(Frame):
    pass


class Ieee1722TpFrame(Frame):
    def __init__(
            self,
            relative_representation_time: float | None = None,
            stream_identifier: int | None = None,
            sub_type: int | None = None,
            version: int | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.relative_representation_time = relative_representation_time
        self.stream_identifier = stream_identifier
        self.sub_type = sub_type
        self.version = version


class UserDefinedEthernetFrame(Frame):
    pass
