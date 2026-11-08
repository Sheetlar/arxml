from typing import TypeVar, Generic
from xml.etree.ElementTree import Element

from autosar.model.communication.communication_cluster import (
    ISignalTriggering,
    PduTriggering,
)
from autosar.model.communication.ethernet import NetworkEndpoint, SoAdConfig
from autosar.model.topology.abstract import PhysicalChannel, CommunicationClusterContent, CommunicationCluster
from autosar.model.topology.can import CanPhysicalChannel, CanClusterContent, CanCluster
from autosar.model.topology.ethernet import EthernetPhysicalChannel, VlanConfig, EthernetClusterContent, CouplingPortConnection, MacMulticastGroup, EthernetCluster
from autosar.parser.communication.ethernet import NetworkEndpointParser, SoAdConfigParser
from autosar.parser.topology.ethernet.coupling_port import CouplingPortConnectionParser
from autosar.parser.topology.ethernet.vlan import MacMulticastGroupParser, VlanConfigParser
from autosar.parser.communication.frame_triggering import FrameTriggeringParserSelector, FT
from autosar.parser.communication.pdu_triggering import PduTriggeringParser
from autosar.parser.communication.signal_triggering import ISignalTriggeringParser
from autosar.parser.identifiable import IdentifiableParser
from autosar.parser.parser_base import (
    handler,
    multiple,
    multiple_with_check,
    ref_variation,
    BasicParserWithParent,
    PropertySetParser, not_implemented_handler,
)

CC = TypeVar('CC', bound=CommunicationCluster)
CCC = TypeVar('CCC', bound=CommunicationClusterContent)
PC = TypeVar('PC', bound=PhysicalChannel)


class PhysicalChannelParser(IdentifiableParser[PC]):
    @handler('COMM-CONNECTORS', param='comm_connectors_refs')
    @ref_variation(element_name='COMMUNICATION-CONNECTOR')
    def _parse_comm_controller(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('FRAME-TRIGGERINGS')
    @multiple
    def _parse_frame_triggering(self, xml_element: Element) -> FT | None:
        try:
            parser = FrameTriggeringParserSelector(xml_element.tag)
        except NotImplementedError:
            self._not_implemented.add(xml_element.tag)
            return None
        return parser.parse_element(xml_element)

    @handler('I-SIGNAL-TRIGGERINGS')
    @multiple_with_check
    def _parse_signal_triggering(self, xml_element: Element) -> ISignalTriggering | None:
        parser = ISignalTriggeringParser()
        return parser.parse_element(xml_element)

    @handler('PDU-TRIGGERINGS')
    @multiple_with_check
    def _parse_pdu_triggering(self, xml_element: Element) -> PduTriggering | None:
        parser = PduTriggeringParser()
        return parser.parse_element(xml_element)


class CanPhysicalChannelParser(PhysicalChannelParser[CanPhysicalChannel]):
    _returned_type = CanPhysicalChannel


class EthernetPhysicalChannelParser(
    PhysicalChannelParser[EthernetPhysicalChannel]
):
    _returned_type = EthernetPhysicalChannel

    @handler('NETWORK-ENDPOINTS')
    @multiple_with_check
    def _parse_network_endpoint(self, xml_element: Element) -> NetworkEndpoint | None:
        parser = NetworkEndpointParser()
        return parser.parse_element(xml_element)

    @handler('SO-AD-CONFIG')
    def _parse_so_ad_config(self, xml_element: Element) -> SoAdConfig | None:
        parser = SoAdConfigParser()
        return parser.parse_element(xml_element)

    @handler('VLAN')
    def _parse_vlan(self, xml_element: Element) -> VlanConfig | None:
        parser = VlanConfigParser()
        return parser.parse_element(xml_element)


class CommunicationClusterContentParser(BasicParserWithParent[CCC], Generic[CCC, PC]):
    _phys_channel_parser: type[PhysicalChannelParser[PC]]
    _phys_channel_tag: str

    @handler('BAUDRATE')
    def _parse_baudrate(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('PROTOCOL-NAME')
    def _parse_proto_name(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('PROTOCOL-VERSION')
    def _parse_proto_version(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('PHYSICAL-CHANNELS')
    @multiple
    def _parse_phys_channel(self, xml_element: Element) -> PC | None:
        if xml_element.tag != self._phys_channel_tag:
            raise NameError
        pcp = self._phys_channel_parser()
        return pcp.parse_element(xml_element)


class CanClusterContentParser(
    CommunicationClusterContentParser[CanClusterContent, CanPhysicalChannel]
):
    _returned_type = CanClusterContent
    _phys_channel_parser = CanPhysicalChannelParser
    _phys_channel_tag = 'CAN-PHYSICAL-CHANNEL'

    @handler('CAN-FD-BAUDRATE')
    def _parse_fd_baudrate(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('CAN-XL-BAUDRATE')
    def _parse_xl_baudrate(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @not_implemented_handler('CAN-CLUSTER-BUS-OFF-RECOVERY')
    def _parse_recovery(self, xml_element: Element):
        ...


class EthernetClusterContentParser(
    CommunicationClusterContentParser[
        EthernetClusterContent,
        EthernetPhysicalChannel,
    ]
):
    _returned_type = EthernetClusterContent
    _phys_channel_parser = EthernetPhysicalChannelParser
    _phys_channel_tag = 'ETHERNET-PHYSICAL-CHANNEL'

    @handler('COUPLING-PORT-CONNECTIONS')
    @multiple_with_check
    def _parse_coupling_port_connection(self, xml_element: Element) -> CouplingPortConnection | None:
        parser = CouplingPortConnectionParser()
        return parser.parse_element(xml_element)

    @handler('COUPLING-PORT-STARTUP-ACTIVE-TIME')
    def _parse_startup_active_time(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('COUPLING-PORT-SWITCHOFF-DELAY')
    def _parse_switchoff_delay(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('MAC-MULTICAST-GROUPS')
    @multiple_with_check
    def _parse_mac_multicast_group(self, xml_element: Element) -> MacMulticastGroup | None:
        parser = MacMulticastGroupParser()
        return parser.parse_element(xml_element)


class CommunicationClusterParser(IdentifiableParser[CC], PropertySetParser[CC, CCC]):
    """Abstract"""


class CanClusterParser(
    CommunicationClusterParser[CanCluster, CanClusterContent]
):
    _returned_type = CanCluster
    _variant_parser_type = CanClusterContentParser
    _tag = 'CAN-CLUSTER'


class EthernetClusterParser(
    CommunicationClusterParser[EthernetCluster, EthernetClusterContent]
):
    _returned_type = EthernetCluster
    _variant_parser_type = EthernetClusterContentParser
    _tag = 'ETHERNET-CLUSTER'
