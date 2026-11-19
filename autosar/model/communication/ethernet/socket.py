from typing import Iterable

from autosar.model.ar_object import ArObject
from autosar.model.base import Identifiable
from autosar.model.communication.ethernet.endpoint import ApplicationEndpoint
from autosar.model.enums import TcpRoleEnum, UdpChecksumCalculationEnum


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


class SoAdConfig(ArObject):
    def __init__(
            self,
            socket_addresses: Iterable[SocketAddress] | None = None,
            connection_bundle: None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.socket_addresses = self._set_parent(socket_addresses)
        self.connection_bundle = connection_bundle
