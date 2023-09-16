from dataclasses import dataclass
from typing import Iterable

from autosar.ar_object import ArObject
from autosar.element import Element


@dataclass
class TpPort:
    port_number: int


@dataclass
class Tp:
    tp_port: TpPort


@dataclass
class UdpTp(Tp):
    pass


@dataclass
class TcpTp(Tp):
    keep_alive_interval: float | None
    keep_alive_probes_max: int | None
    keep_alive_time: float | None
    keep_alives: bool


@dataclass
class TpConfiguration:
    tp: Tp


class CouplingPortConnection(Element):
    def __init__(
            self,
            first_port_ref: str,
            second_port_ref: str,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.first_port_ref = first_port_ref
        self.second_port_ref = second_port_ref


class VLAN(Element):
    def __init__(self, vlan_identifier: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vlan_identifier = vlan_identifier


class IPv4Configuration(Element):
    def __init__(
            self,
            ipv4_address: str,
            ipv4_address_source: str,
            network_mask: str,
            *args, **kwargs,
    ):
        super().__init__(name=None, *args, **kwargs)
        self.ipv4_address = ipv4_address
        self.ipv4_address_source = ipv4_address_source
        self.network_mask = network_mask


class NetworkEndpoint(Element):
    def __init__(
            self,
            desc: str | None,
            network_endpoint_addresses: IPv4Configuration | None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.desc = desc
        if network_endpoint_addresses is not None:
            network_endpoint_addresses.parent = self
        self.network_endpoint_addresses = network_endpoint_addresses


class ApplicationEndpoint(Element):
    def __init__(
            self,
            max_number_of_connections: int,
            network_endpoint_ref: str,
            tp_configuration: TpConfiguration,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.max_number_of_connections = max_number_of_connections
        self.network_endpoint_ref = network_endpoint_ref
        self.tp_configuration = tp_configuration


class SocketAddress(Element):
    def __init__(
            self,
            application_endpoint: ApplicationEndpoint | None,
            connector_ref: str,
            pdu_collection_max_buffer_size: int,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if application_endpoint is not None:
            application_endpoint.parent = self
        self.application_endpoint = application_endpoint
        self.connector_ref = connector_ref
        self.pdu_collection_max_buffer_size = pdu_collection_max_buffer_size

    def find(self, ref: str, role: str | None = None) -> Element | None:
        if self.application_endpoint is None:
            return None
        name, _, tail = ref.partition('/')
        if self.application_endpoint.name == name:
            if len(tail) > 0:
                return self.application_endpoint.find(tail)
            return self.application_endpoint
        return None


class SoAdConfig(Element):
    def __init__(
            self,
            socket_addresses: Iterable[SocketAddress] | None = None,
            *args, **kwargs,
    ):
        super().__init__(name=None, *args, **kwargs)
        self.socket_addresses = self._set_parent(socket_addresses)

    def _set_children_parent(self):
        self._set_parent(self.socket_addresses, self.parent)


class ISignalTriggering(Element):
    def __init__(
            self,
            i_signal_port_refs: list[str] | None = None,
            i_signal_ref: str | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if i_signal_port_refs is None:
            i_signal_port_refs = []
        self.i_signal_port_refs = i_signal_port_refs
        self.i_signal_ref = i_signal_ref


@dataclass
class ISignalTriggeringRefConditional(ArObject):
    i_signal_triggering_ref: str | None = None


class PduTriggering(Element):
    def __init__(
            self,
            i_pdu_port_refs: list[str] | None = None,
            i_pdu_ref: str | None = None,
            i_signal_triggerings: list[ISignalTriggeringRefConditional] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if i_pdu_port_refs is None:
            i_pdu_port_refs = []
        self.i_signal_port_refs = i_pdu_port_refs
        self.i_signal_ref = i_pdu_ref
        if i_signal_triggerings is None:
            i_signal_triggerings = []
        self.i_signal_triggerings = i_signal_triggerings


class EthernetPhysicalChannel(Element):
    def __init__(
            self,
            comm_connectors_refs: list[str] | None = None,
            i_signal_triggerings: Iterable[ISignalTriggering] | None = None,
            pdu_triggerings: Iterable[PduTriggering] | None = None,
            network_endpoints: Iterable[NetworkEndpoint] | None = None,
            so_ad_config: SoAdConfig | None = None,
            vlan: VLAN | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.comm_connectors_refs = comm_connectors_refs
        self.i_signal_triggerings = self._set_parent(i_signal_triggerings)
        self.pdu_triggerings = self._set_parent(pdu_triggerings)
        self.network_endpoints = self._set_parent(network_endpoints)
        self.so_ad_config = so_ad_config
        if vlan is not None:
            vlan.parent = self
        self.vlan = vlan
        self._find_sets = [self.network_endpoints, self.i_signal_triggerings, self.pdu_triggerings]
        if self.so_ad_config is not None:
            self.so_ad_config.parent = self
            self._find_sets.append(self.so_ad_config.socket_addresses)


class EthernetClusterVariant(Element):
    pass


class EthernetClusterConditional(EthernetClusterVariant):
    def __init__(
            self,
            protocol_name: str,
            baud_rate: int,
            physical_channels: Iterable[EthernetPhysicalChannel] | None = None,
            coupling_port_connections: Iterable[CouplingPortConnection] | None = None,
            *args, **kwargs,
    ):
        super().__init__(name=None, *args, **kwargs)
        self.protocol_name = protocol_name
        self.baud_rate = baud_rate
        self.physical_channels = self._set_parent(physical_channels)
        self.coupling_port_connections = self._set_parent(coupling_port_connections)
        self._find_sets = [self.physical_channels]

    def _set_children_parent(self):
        self._set_parent(self.physical_channels, self.parent)
        self._set_parent(self.coupling_port_connections, self.parent)


class EthernetCluster(Element):
    def __init__(
            self,
            ethernet_cluster_variants: Iterable[EthernetClusterVariant] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.ethernet_cluster_variants = self._set_parent(ethernet_cluster_variants)

    def find(self, ref: str, role: str | None = None) -> Element | None:
        for cluster_variant in self.ethernet_cluster_variants:
            elem: Element = cluster_variant.find(ref)
            if elem is not None:
                return elem
        return None
