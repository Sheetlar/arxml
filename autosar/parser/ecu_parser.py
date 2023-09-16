from typing import Callable
from xml.etree.ElementTree import Element

from autosar.ar_object import ArObject
from autosar.ecu import (
    EcuInstance,
    ClientIdRange,
    EthernetCommunicationController,
    CouplingPort,
    EthernetCommunicationConnector,
    CommPort,
    FramePort,
    IPduPort,
    ISignalPort,
    EthTcpIpProps,
    TcpProps,
)
from autosar.parser.parser_base import ElementParser


class EcuParser(ElementParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.switcher: dict[str, Callable[[Element, ArObject | None], EcuInstance | EthTcpIpProps | None]] = {
            'ECU-INSTANCE': self._parse_ecu_instance,
            'ETH-TCP-IP-PROPS': self._parse_eth_tcp_ip_props,
        }

    def get_supported_tags(self):
        return self.switcher.keys()

    def parse_element(self, xml_element: Element, parent: ArObject | None = None) -> EcuInstance | EthTcpIpProps | None:
        if xml_element.tag not in self.switcher:
            return None
        element_parser = self.switcher[xml_element.tag]
        return element_parser(xml_element, parent)

    def _parse_ecu_instance(self, xml_elem: Element, parent: ArObject | None) -> EcuInstance:
        client_id_range = None
        comm_controllers = None
        connectors = None
        diagnostic_address = None
        pn_reset_time = None
        pnc_prepare_sleep_timer = None
        sleep_mode_supported = False
        tcp_ip_props_ref = None
        wake_up_over_bus_supported = False
        common_args = self._parse_common_tags(xml_elem)
        for child_elem in xml_elem.findall('./*'):
            match child_elem.tag:
                case tag if tag in self.common_tags:
                    pass
                case 'CLIENT-ID-RANGE':
                    lower_limit = self.parse_int_node(child_elem.find('LOWER-LIMIT'))
                    upper_limit = self.parse_int_node(child_elem.find('UPPER-LIMIT'))
                    client_id_range = ClientIdRange(
                        lower_limit=lower_limit,
                        upper_limit=upper_limit,
                    )
                case 'COMM-CONTROLLERS':
                    comm_controllers = self._parse_element_list(
                        child_elem,
                        {'ETHERNET-COMMUNICATION-CONTROLLER': self._parse_comm_controller},
                    )
                case 'CONNECTORS':
                    connectors = self._parse_element_list(
                        child_elem,
                        {'ETHERNET-COMMUNICATION-CONNECTOR': self._parse_connector},
                    )
                case 'DIAGNOSTIC-ADDRESS':
                    diagnostic_address = self.parse_int_node(child_elem)
                case 'PN-RESET-TIME':
                    pn_reset_time = self.parse_number_node(child_elem)
                case 'PNC-PREPARE-SLEEP-TIMER':
                    pnc_prepare_sleep_timer = self.parse_number_node(child_elem)
                case 'SLEEP-MODE-SUPPORTED':
                    sleep_mode_supported = self.parse_boolean_node(child_elem)
                case 'TCP-IP-PROPS-REF':
                    tcp_ip_props_ref = self.parse_text_node(child_elem)
                case 'WAKE-UP-OVER-BUS-SUPPORTED':
                    wake_up_over_bus_supported = self.parse_boolean_node(child_elem)
                case _:
                    self._logger.warning(f'Unexpected tag for {xml_elem.tag}: {child_elem.tag}')
        ecu = EcuInstance(
            client_id_range=client_id_range,
            comm_controllers=comm_controllers,
            connectors=connectors,
            diagnostic_address=diagnostic_address,
            pn_reset_time=pn_reset_time,
            pnc_prepare_sleep_timer=pnc_prepare_sleep_timer,
            sleep_mode_supported=sleep_mode_supported,
            tcp_ip_props_ref=tcp_ip_props_ref,
            wake_up_over_bus_supported=wake_up_over_bus_supported,
            parent=parent,
            **common_args,
        )
        return ecu

    def _parse_comm_controller(self, xml_elem: Element) -> EthernetCommunicationController:
        common_args = self._parse_common_tags(xml_elem)
        ports = None
        ports_elem = xml_elem.find('ETHERNET-COMMUNICATION-CONTROLLER-VARIANTS/ETHERNET-COMMUNICATION-CONTROLLER-CONDITIONAL/COUPLING-PORTS')
        if ports_elem is not None:
            ports = self._parse_element_list(ports_elem, {'COUPLING-PORT': self._parse_coupling_port})
        controller = EthernetCommunicationController(
            coupling_ports=ports,
            **common_args,
        )
        return controller

    def _parse_coupling_port(self, xml_elem: Element) -> CouplingPort:
        common_args = self._parse_common_tags(xml_elem)
        port = CouplingPort(**common_args)
        return port

    def _parse_connector(self, xml_elem: Element) -> EthernetCommunicationConnector | None:
        common_args = self._parse_common_tags(xml_elem)
        controller_ref = self.parse_text_node(xml_elem.find('COMM-CONTROLLER-REF'))
        port_elem = xml_elem.find('ECU-COMM-PORT-INSTANCES')
        if port_elem is None:
            self._logger.error(f'Missing <ECU-COMM-PORT-INSTANCES> in {xml_elem.tag}')
            return None
        port_instances = self._parse_element_list(port_elem, {
            'FRAME-PORT': self._parse_comm_port,
            'I-PDU-PORT': self._parse_comm_port,
            'I-SIGNAL-PORT': self._parse_comm_port,
        })
        mtu = self.parse_int_node(xml_elem.find('MAXIMUM-TRANSMISSION-UNIT'))
        connector = EthernetCommunicationConnector(
            comm_controller_ref=controller_ref,
            ecu_comm_port_instances=port_instances,
            maximum_transmission_unit=mtu,
            **common_args,
        )
        return connector

    def _parse_comm_port(self, xml_elem: Element) -> CommPort | None:
        tag2type = {
            'FRAME-PORT': FramePort,
            'I-PDU-PORT': IPduPort,
            'I-SIGNAL-PORT': ISignalPort,
        }
        if xml_elem.tag not in tag2type:
            self._logger.error(f'Unexpected comm port tag: {xml_elem.tag}')
            return None
        port_type = tag2type[xml_elem.tag]
        common_args = self._parse_common_tags(xml_elem)
        direction = self.parse_text_node(xml_elem.find('COMMUNICATION-DIRECTION'))
        port = port_type(
            communication_direction=direction,
            **common_args,
        )
        return port

    def _parse_eth_tcp_ip_props(self, xml_elem: Element, parent: ArObject | None) -> EthTcpIpProps | None:
        common_args = self._parse_common_tags(xml_elem)
        props_elem = xml_elem.find('TCP-PROPS')
        if props_elem is None:
            return None
        tcp_props = TcpProps(
            tcp_congestion_avoidance_avoidance_enabled=self.parse_boolean_node(props_elem.find('TCP-CONGESTION-AVOIDANCE-ENABLED')),
            tcp_delayed_ack_timeout=self.parse_number_node(props_elem.find('TCP-DELAYED-ACK-TIMEOUT')),
            tcp_fast_recovery_enabled=self.parse_boolean_node(props_elem.find('TCP-FAST-RECOVERY-ENABLED')),
            tcp_fast_retransmit_enabled=self.parse_boolean_node(props_elem.find('TCP-FAST-RETRANSMIT-ENABLED')),
            tcp_fin_wait_2_timeout=self.parse_number_node(props_elem.find('TCP-FIN-WAIT-2-TIMEOUT')),
            tcp_keep_alive_enabled=self.parse_boolean_node(props_elem.find('TCP-KEEP-ALIVE-ENABLED')),
            tcp_keep_alive_interval=self.parse_number_node(props_elem.find('TCP-KEEP-ALIVE-INTERVAL')),
            tcp_keep_alive_probes_max=self.parse_int_node(props_elem.find('TCP-KEEP-ALIVE-PROBES-MAX')),
            tcp_keep_alive_time=self.parse_number_node(props_elem.find('TCP-KEEP-ALIVE-TIME')),
            tcp_max_rtx=self.parse_number_node(props_elem.find('TCP-MAX-RTX')),
            tcp_msl=self.parse_number_node(props_elem.find('TCP-MSL')),
            tcp_nagle_enabled=self.parse_boolean_node(props_elem.find('TCP-NAGLE-ENABLED')),
            tcp_receive_window_max=self.parse_number_node(props_elem.find('TCP-RECEIVE-WINDOW-MAX')),
            tcp_retransmission_timeout=self.parse_number_node(props_elem.find('TCP-RETRANSMISSION-TIMEOUT')),
            tcp_slow_start_enabled=self.parse_boolean_node(props_elem.find('TCP-SLOW-START-ENABLED')),
            tcp_syn_max_rtx=self.parse_number_node(props_elem.find('TCP-SYN-MAX-RTX')),
            tcp_syn_received_timeout=self.parse_number_node(props_elem.find('TCP-SYN-RECEIVED-TIMEOUT')),
            tcp_ttl=self.parse_int_node(props_elem.find('TCP-TTL')),
        )
        props = EthTcpIpProps(
            tcp_props=tcp_props,
            parent=parent,
            **common_args,
        )
        return props
