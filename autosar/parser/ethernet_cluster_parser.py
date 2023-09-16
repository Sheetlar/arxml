from xml.etree.ElementTree import Element

from autosar.ar_object import ArObject
from autosar.ethernet_cluster import (
    EthernetCluster,
    EthernetClusterConditional,
    CouplingPortConnection,
    EthernetPhysicalChannel,
    VLAN,
    NetworkEndpoint,
    SoAdConfig,
    IPv4Configuration,
    SocketAddress,
    ApplicationEndpoint,
    TpConfiguration,
    UdpTp,
    TcpTp,
    TpPort,
    ISignalTriggering,
    PduTriggering,
    ISignalTriggeringRefConditional,
)
from autosar.parser.parser_base import ElementParser


class EthernetClusterParser(ElementParser):
    def get_supported_tags(self):
        return ['ETHERNET-CLUSTER']

    def parse_element(self, xml_element: Element, parent: ArObject | None = None) -> EthernetCluster | None:
        if xml_element.tag == 'ETHERNET-CLUSTER':
            return self._parse_ethernet_cluster(xml_element, parent)
        return None

    def _parse_ethernet_cluster(self, xml_elem: Element, parent: ArObject | None) -> EthernetCluster:
        name = None
        admin_data = None
        ethernet_cluster_variants = None
        for child_elem in xml_elem.findall('./*'):
            match child_elem.tag:
                case 'SHORT-NAME':
                    name = self.parse_text_node(child_elem)
                case 'ADMIN-DATA':
                    admin_data = self.parse_admin_data_node(child_elem)
                case 'ETHERNET-CLUSTER-VARIANTS':
                    ethernet_cluster_variants = self._parse_element_list(
                        child_elem,
                        {'ETHERNET-CLUSTER-CONDITIONAL': self._parse_ethernet_cluster_conditional},
                    )
                case _:
                    self._logger.warning(f'Unexpected tag: {child_elem.tag}')
        cluster = EthernetCluster(
            name=name,
            ethernet_cluster_variants=ethernet_cluster_variants,
            admin_data=admin_data,
            parent=parent,
        )
        return cluster

    def _parse_ethernet_cluster_conditional(self, xml_elem: Element) -> EthernetClusterConditional:
        protocol_name = None
        baud_rate = None
        physical_channels = None
        coupling_port_connections = None
        for child_elem in xml_elem.findall('./*'):
            match child_elem.tag:
                case 'PROTOCOL-NAME':
                    protocol_name = self.parse_text_node(child_elem)
                case 'BAUDRATE':
                    baud_rate = self.parse_int_node(child_elem)
                case 'PHYSICAL-CHANNELS':
                    physical_channels = self._parse_element_list(
                        child_elem,
                        {'ETHERNET-PHYSICAL-CHANNEL': self._parse_eth_phys_channel},
                    )
                case 'COUPLING-PORT-CONNECTIONS':
                    coupling_port_connections = self._parse_element_list(
                        child_elem,
                        {'COUPLING-PORT-CONNECTIONS': self._parse_coupling_port_connection},
                    )
                case _:
                    self._logger.warning(f'Unexpected tag: {child_elem.tag}')
        cluster = EthernetClusterConditional(
            protocol_name=protocol_name,
            baud_rate=baud_rate,
            physical_channels=physical_channels,
            coupling_port_connections=coupling_port_connections,
        )
        return cluster

    def _parse_eth_phys_channel(self, xml_elem: Element) -> EthernetPhysicalChannel:
        name = None
        comm_connectors_refs = None
        network_endpoints = None
        so_ad_config = None
        vlan = None
        signal_triggerings = None
        pdu_triggerings = None
        for child_elem in xml_elem.findall('./*'):
            match child_elem.tag:
                case 'SHORT-NAME':
                    name = self.parse_text_node(child_elem)
                case 'COMM-CONNECTORS':
                    comm_connectors_refs = self._parse_comm_connectors_refs(child_elem)
                case 'NETWORK-ENDPOINTS':
                    network_endpoints = self._parse_element_list(
                        child_elem,
                        {'NETWORK-ENDPOINT': self._parse_network_endpoint},
                    )
                case 'SO-AD-CONFIG':
                    socket_addresses = child_elem.find('SOCKET-ADDRESSS')
                    if socket_addresses is None:
                        self._logger.warning(f'Missing <SOCKET-ADDRESSS> in {child_elem.tag}')
                        continue
                    addresses = self._parse_element_list(
                        socket_addresses,
                        {'SOCKET-ADDRESS': self._parse_socket_address},
                    )
                    so_ad_config = SoAdConfig(socket_addresses=addresses)
                case 'VLAN':
                    vlan = self._parse_vlan(child_elem)
                case 'I-SIGNAL-TRIGGERINGS':
                    signal_triggerings = self._parse_element_list(
                        child_elem,
                        {'I-SIGNAL-TRIGGERING': self._parse_i_signal_triggering},
                    )
                case 'PDU-TRIGGERINGS':
                    pdu_triggerings = self._parse_element_list(
                        child_elem,
                        {'PDU-TRIGGERING': self._parse_pdu_triggering},
                    )
                case _:
                    self._logger.warning(f'Unexpected tag: {child_elem.tag}')
        channel = EthernetPhysicalChannel(
            name=name,
            comm_connectors_refs=comm_connectors_refs,
            network_endpoints=network_endpoints,
            so_ad_config=so_ad_config,
            i_signal_triggerings=signal_triggerings,
            pdu_triggerings=pdu_triggerings,
            vlan=vlan,
        )
        return channel

    def _parse_comm_connectors_refs(self, xml_elem: Element) -> list[str]:
        refs = []
        for child_elem in xml_elem.findall('COMMUNICATION-CONNECTOR-REF-CONDITIONAL'):
            connector_ref = self.parse_text_node(child_elem.find('COMMUNICATION-CONNECTOR-REF'))
            if connector_ref is not None:
                refs.append(connector_ref)
        return refs

    def _parse_network_endpoint(self, xml_elem: Element) -> NetworkEndpoint:
        name = None
        desc = None
        network_endpoint_address = None
        for child_elem in xml_elem.findall('./*'):
            match child_elem.tag:
                case 'SHORT-NAME':
                    name = self.parse_text_node(child_elem)
                case 'DESC':
                    desc = self.parse_text_node(child_elem.find('L-2'))
                case 'NETWORK-ENDPOINT-ADDRESSES':
                    network_endpoint_address = self._parse_ipv4_config(child_elem)
                case _:
                    self._logger.warning(f'Unexpected tag: {child_elem.tag}')
        network_endpoint = NetworkEndpoint(
            name=name,
            desc=desc,
            network_endpoint_addresses=network_endpoint_address,
        )
        return network_endpoint

    def _parse_ipv4_config(self, xml_elem: Element) -> IPv4Configuration | None:
        xml_elem = xml_elem.find('IPV-4-CONFIGURATION')
        if xml_elem is None:
            return None
        address = self.parse_text_node(xml_elem.find('IPV-4-ADDRESS'))
        address_source = self.parse_text_node(xml_elem.find('IPV-4-ADDRESS-SOURCE'))
        net_mask = self.parse_text_node(xml_elem.find('NETWORK-MASK'))
        if address is None or address_source is None or net_mask is None:
            return None
        config = IPv4Configuration(
            ipv4_address=address,
            ipv4_address_source=address_source,
            network_mask=net_mask,
        )
        return config

    def _parse_socket_address(self, xml_elem: Element) -> SocketAddress:
        name = None
        app_endpoint = None
        connector_ref = None
        max_buffer_size = None
        for child_elem in xml_elem.findall('./*'):
            match child_elem.tag:
                case 'SHORT-NAME':
                    name = self.parse_text_node(child_elem)
                case 'CONNECTOR-REF':
                    connector_ref = self.parse_text_node(child_elem)
                case 'PDU-COLLECTION-MAX-BUFFER-SIZE':
                    max_buffer_size = self.parse_int_node(child_elem)
                case 'APPLICATION-ENDPOINT':
                    app_endpoint = self._parse_app_endpoint(child_elem)
                case _:
                    self._logger.warning(f'Unexpected tag: {child_elem.tag}')
        address = SocketAddress(
            name=name,
            application_endpoint=app_endpoint,
            connector_ref=connector_ref,
            pdu_collection_max_buffer_size=max_buffer_size,
        )
        return address

    def _parse_app_endpoint(self, xml_elem: Element) -> ApplicationEndpoint | None:
        name = None
        max_connections = None
        endpoint_ref = None
        configuration = None
        for child_elem in xml_elem.findall('./*'):
            match child_elem.tag:
                case 'SHORT-NAME':
                    name = self.parse_text_node(child_elem)
                case 'NETWORK-ENDPOINT-REF':
                    endpoint_ref = self.parse_text_node(child_elem)
                case 'MAX-NUMBER-OF-CONNECTIONS':
                    max_connections = self.parse_int_node(child_elem)
                case 'TP-CONFIGURATION':
                    tp = None
                    for tp_elem in child_elem.findall('./*'):
                        match tp_elem.tag:
                            case 'UDP-TP':
                                tp = self._parse_udp_tp(tp_elem)
                            case 'TCP-TP':
                                tp = self._parse_tcp_tp(tp_elem)
                            case _:
                                self._logger.warning(f'Unexpected tag: {child_elem.tag}')
                    if tp is not None:
                        configuration = TpConfiguration(tp=tp)
                case _:
                    self._logger.warning(f'Unexpected tag: {child_elem.tag}')
        if configuration is None:
            return None
        endpoint = ApplicationEndpoint(
            name=name,
            max_number_of_connections=max_connections,
            network_endpoint_ref=endpoint_ref,
            tp_configuration=configuration,
        )
        return endpoint

    def _parse_udp_tp(self, xml_elem: Element) -> UdpTp | None:
        udp_tp_port_elem = xml_elem.find('UDP-TP-PORT')
        if udp_tp_port_elem is None:
            self._logger.warning(f'Missing <UDP-TP-PORT> in {xml_elem.tag}')
            return None
        port_number = self.parse_int_node(udp_tp_port_elem.find('PORT-NUMBER'))
        if port_number is None:
            self._logger.warning(f'Missing <PORT-NUMBER> in {udp_tp_port_elem.tag}')
            return None
        udp_tp = UdpTp(tp_port=TpPort(port_number=port_number))
        return udp_tp

    def _parse_tcp_tp(self, xml_elem: Element) -> TcpTp | None:
        tcp_tp_port = None
        keep_alive_interval = None
        keep_alive_probes_max = None
        keep_alive_time = None
        keep_alives = False
        for child_elem in xml_elem.findall('./*'):
            match child_elem.tag:
                case 'TCP-TP-PORT':
                    port_number = self.parse_int_node(child_elem.find('PORT-NUMBER'))
                    if port_number is None:
                        self._logger.warning(f'Missing <PORT-NUMBER> in {child_elem.tag}')
                        continue
                    tcp_tp_port = TpPort(port_number=port_number)
                case 'KEEP-ALIVE-INTERVAL':
                    keep_alive_interval = self.parse_float_node(child_elem)
                case 'KEEP-ALIVE-PROBES-MAX':
                    keep_alive_probes_max = self.parse_int_node(child_elem)
                case 'KEEP-ALIVE-TIME':
                    keep_alive_time = self.parse_float_node(child_elem)
                case 'KEEP-ALIVES':
                    keep_alives = self.parse_boolean_node(child_elem)
                case _:
                    self._logger.warning(f'Unexpected tag: {child_elem.tag}')
        if tcp_tp_port is None:
            return None
        tcp_tp = TcpTp(
            tp_port=tcp_tp_port,
            keep_alive_interval=keep_alive_interval,
            keep_alive_probes_max=keep_alive_probes_max,
            keep_alive_time=keep_alive_time,
            keep_alives=keep_alives,
        )
        return tcp_tp

    def _parse_vlan(self, xml_elem: Element) -> VLAN:
        name = self.parse_text_node(xml_elem.find('SHORT-NAME'))
        vlan_id = self.parse_int_node(xml_elem.find('VLAN-IDENTIFIER'))
        vlan = VLAN(
            name=name,
            vlan_identifier=vlan_id,
        )
        return vlan

    def _parse_i_signal_triggering(self, xml_elem: Element) -> ISignalTriggering:
        name = None
        port_refs = []
        signal_ref = None
        for child_elem in xml_elem.findall('./*'):
            match child_elem.tag:
                case 'SHORT-NAME':
                    name = self.parse_text_node(child_elem)
                case 'I-SIGNAL-REF':
                    signal_ref = self.parse_text_node(child_elem)
                case 'I-SIGNAL-PORT-REFS':
                    for sub_elem in child_elem.findall('./*'):
                        if sub_elem.tag != 'I-SIGNAL-PORT-REF':
                            self._logger.error(f'Unexpected tag for {child_elem.tag}: {sub_elem.tag}')
                            continue
                        port_ref = self.parse_text_node(sub_elem)
                        if port_ref is not None:
                            port_refs.append(port_ref)
        triggering = ISignalTriggering(
            name=name,
            i_signal_port_refs=port_refs,
            i_signal_ref=signal_ref,
        )
        return triggering

    def _parse_pdu_triggering(self, xml_elem: Element) -> PduTriggering:
        name = None
        port_refs = []
        pdu_ref = None
        triggerings = []
        for child_elem in xml_elem.findall('./*'):
            match child_elem.tag:
                case 'SHORT-NAME':
                    name = self.parse_text_node(child_elem)
                case 'I-PDU-REF':
                    pdu_ref = self.parse_text_node(child_elem)
                case 'I-PDU-PORT-REFS':
                    for sub_elem in child_elem.findall('./*'):
                        if sub_elem.tag != 'I-SIGNAL-PORT-REF':
                            self._logger.error(f'Unexpected tag for {child_elem.tag}: {sub_elem.tag}')
                            continue
                        port_ref = self.parse_text_node(sub_elem)
                        if port_ref is not None:
                            port_refs.append(port_ref)
                case 'I-SIGNAL-TRIGGERINGS':
                    for sub_elem in child_elem.findall('./*'):
                        if sub_elem.tag != 'I-SIGNAL-TRIGGERING-REF-CONDITIONAL':
                            self._logger.error(f'Unexpected tag for {child_elem.tag}: {sub_elem.tag}')
                            continue
                        signal_ref = self.parse_text_node(sub_elem.find('I-SIGNAL-TRIGGERING-REF'))
                        triggerings.append(ISignalTriggeringRefConditional(i_signal_triggering_ref=signal_ref))
        triggering = PduTriggering(
            name=name,
            i_pdu_port_refs=port_refs,
            i_pdu_ref=pdu_ref,
            i_signal_triggerings=triggerings,
        )
        return triggering

    def _parse_coupling_port_connection(self, xml_elem: Element) -> CouplingPortConnection:
        first_port_ref = self.parse_text_node(xml_elem.find('FIRST-PORT-REF'))
        second_port_ref = self.parse_text_node(xml_elem.find('SECOND-PORT-REF'))
        connection = CouplingPortConnection(
            first_port_ref=first_port_ref,
            second_port_ref=second_port_ref,
        )
        return connection
