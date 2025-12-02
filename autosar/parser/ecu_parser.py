from typing import Callable, TypeAlias
from xml.etree.ElementTree import Element

from autosar.model.ar_object import ArObject
from autosar.model.communication_controller import (
    CommunicationController,
    CanCommunicationController,
    EthernetCommunicationController,
    CouplingPort,
)
from autosar.model.ecu import (
    EcuInstance,
    CommunicationConnector,
    CanCommunicationConnector,
    EthernetCommunicationConnector,
    CommPort,
    FramePort,
    IPduPort,
    ISignalPort,
    ClientIdRange,
    EcuPartition,
    Gateway,
    FrameMapping,
    ISignalMapping,
    IPduMapping,
    TargetIPduRef,
)
from autosar.model.tcp_ip_props import TcpProps, EthTcpIpProps
from autosar.parser.parser_base import ElementParser

SupportedElement: TypeAlias = EcuInstance | EthTcpIpProps | Gateway


class EcuParser(ElementParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.switcher: dict[str, Callable[[Element, ArObject | None], SupportedElement | None]] = {
            'ECU-INSTANCE': self._parse_ecu_instance,
            'ETH-TCP-IP-PROPS': self._parse_eth_tcp_ip_props,
            'GATEWAY': self._parse_gateway,
        }

    def get_supported_tags(self):
        return self.switcher.keys()

    def parse_element(self, xml_element: Element, parent: ArObject | None = None) -> SupportedElement | None:
        if xml_element.tag not in self.switcher:
            return None
        element_parser = self.switcher[xml_element.tag]
        return element_parser(xml_element, parent)

    def _parse_ecu_instance(self, xml_elem: Element, parent: ArObject | None) -> EcuInstance:
        common_tags = self.parse_common_tags(xml_elem)
        diagnostic_address: int | None = None
        comm_controllers: list[CommunicationController] | None = None
        connectors: list[CommunicationConnector] | None = None
        client_id_range: ClientIdRange | None = None
        partitions: list[EcuPartition] | None = None
        com_config_gw_time_base: float | None = None
        com_config_rx_time_base: float | None = None
        com_config_tx_time_base: float | None = None
        com_i_pdu_group_refs: list[str] | None = None
        service_instance_group_refs: list[str] | None = None
        pdu_r_i_pdu_group_refs: list[str] | None = None
        ecu_task_proxy_refs: list[str] | None = None
        tcp_ip_icmp_props_ref: str | None = None
        tcp_ip_props_ref: str | None = None
        pnc_prepare_sleep_timer: float | None = None
        pn_reset_time: float | None = None
        com_enable_mdt_for_cyclic_transmission: bool | None = None
        eth_switch_port_group_derivation: bool | None = None
        pnc_nm_request: bool | None = None
        pnc_synchronous_wakeup: bool | None = None
        sleep_mode_supported: bool | None = None
        wake_up_over_bus_supported: bool | None = None
        v2x_supported: str | None = None
        for child_elem in xml_elem.findall('./*'):
            match child_elem.tag:
                case tag if tag in self.common_tags:
                    pass
                case 'DIAGNOSTIC-ADDRESS':
                    diagnostic_address = self.parse_int_node(child_elem)
                case 'COMM-CONTROLLERS':
                    comm_controllers = self.parse_variable_element_list(child_elem, {
                        'ETHERNET-COMMUNICATION-CONTROLLER': self._parse_eth_controller,
                        'CAN-COMMUNICATION-CONTROLLER': self._parse_can_controller,
                    })
                case 'CONNECTORS':
                    connectors = self.parse_variable_element_list(child_elem, {
                        'ETHERNET-COMMUNICATION-CONNECTOR': self._parse_eth_connector,
                        'CAN-COMMUNICATION-CONNECTOR': self._parse_can_connector,
                    })
                case 'CLIENT-ID-RANGE':
                    lower_limit = self.parse_int_node(child_elem.find('LOWER-LIMIT'))
                    upper_limit = self.parse_int_node(child_elem.find('UPPER-LIMIT'))
                    client_id_range = ClientIdRange(
                        lower_limit=lower_limit,
                        upper_limit=upper_limit,
                    )
                case 'PARTITIONS':
                    partitions = self.parse_element_list(
                        child_elem,
                        self._parse_ecu_partition,
                        'ECU-PARTITION',
                    )
                case 'COM-CONFIGURATION-GW-TIME-BASE':
                    com_config_gw_time_base = self.parse_number_node(child_elem)
                case 'COM-CONFIGURATION-RX-TIME-BASE':
                    com_config_rx_time_base = self.parse_number_node(child_elem)
                case 'COM-CONFIGURATION-TX-TIME-BASE':
                    com_config_tx_time_base = self.parse_number_node(child_elem)
                case 'ASSOCIATED-COM-I-PDU-GROUP-REFS':
                    com_i_pdu_group_refs = list(self.child_string_nodes(child_elem))
                case 'ASSOCIATED-CONSUMED-PROVIDED-SERVICE-INSTANCE-GROUP-REFS':
                    service_instance_group_refs = list(self.child_string_nodes(child_elem))
                case 'ASSOCIATED-PDUR-I-PDU-GROUP-REFS':
                    pdu_r_i_pdu_group_refs = list(self.child_string_nodes(child_elem))
                case 'ECU-TASK-PROXY-REFS':
                    ecu_task_proxy_refs = list(self.child_string_nodes(child_elem))
                case 'TCP-IP-ICMP-PROPS-REF':
                    tcp_ip_icmp_props_ref = self.parse_text_node(child_elem)
                case 'TCP-IP-PROPS-REF':
                    tcp_ip_props_ref = self.parse_text_node(child_elem)
                case 'PNC-PREPARE-SLEEP-TIMER':
                    pnc_prepare_sleep_timer = self.parse_number_node(child_elem)
                case 'PN-RESET-TIME':
                    pn_reset_time = self.parse_number_node(child_elem)
                case 'COM-ENABLE-MDT-FOR-CYCLIC-TRANSMISSION':
                    com_enable_mdt_for_cyclic_transmission = self.parse_boolean_node(child_elem)
                case 'ETH-SWITCH-PORT-GROUP-DERIVATION':
                    eth_switch_port_group_derivation = self.parse_boolean_node(child_elem)
                case 'PNC-NM-REQUEST':
                    pnc_nm_request = self.parse_boolean_node(child_elem)
                case 'PNC-SYNCHRONOUS-WAKEUP':
                    pnc_synchronous_wakeup = self.parse_boolean_node(child_elem)
                case 'SLEEP-MODE-SUPPORTED':
                    sleep_mode_supported = self.parse_boolean_node(child_elem)
                case 'WAKE-UP-OVER-BUS-SUPPORTED':
                    wake_up_over_bus_supported = self.parse_boolean_node(child_elem)
                case 'V-2X-SUPPORTED':
                    v2x_supported = self.parse_text_node(child_elem)
                case _:
                    self.log_unexpected(xml_elem, child_elem)
        ecu = EcuInstance(
            diagnostic_address=diagnostic_address,
            comm_controllers=comm_controllers,
            connectors=connectors,
            client_id_range=client_id_range,
            partitions=partitions,
            com_configuration_gw_time_base=com_config_gw_time_base,
            com_configuration_rx_time_base=com_config_rx_time_base,
            com_configuration_tx_time_base=com_config_tx_time_base,
            associated_com_i_pdu_group_refs=com_i_pdu_group_refs,
            associated_consumed_provided_service_instance_group_refs=service_instance_group_refs,
            associated_pdu_r_i_pdu_group_refs=pdu_r_i_pdu_group_refs,
            ecu_task_proxy_refs=ecu_task_proxy_refs,
            tcp_ip_icmp_props_ref=tcp_ip_icmp_props_ref,
            tcp_ip_props_ref=tcp_ip_props_ref,
            pnc_prepare_sleep_timer=pnc_prepare_sleep_timer,
            pn_reset_time=pn_reset_time,
            com_enable_mdt_for_cyclic_transmission=com_enable_mdt_for_cyclic_transmission,
            eth_switch_port_group_derivation=eth_switch_port_group_derivation,
            pnc_nm_request=pnc_nm_request,
            pnc_synchronous_wakeup=pnc_synchronous_wakeup,
            sleep_mode_supported=sleep_mode_supported,
            v2x_supported=v2x_supported,
            wake_up_over_bus_supported=wake_up_over_bus_supported,
            parent=parent,
            **common_tags,
        )
        return ecu

    def _parse_ecu_partition(self, xml_elem: Element) -> EcuPartition:
        common_args = self.parse_common_tags(xml_elem)
        exec_in_user_mode = self.parse_boolean_node(xml_elem.find('EXEC-IN-USER-MODE'))
        partition = EcuPartition(
            exec_in_user_mode=exec_in_user_mode,
            **common_args,
        )
        return partition

    def _parse_can_controller(self, xml_elem: Element) -> CanCommunicationController:
        # TODO: Variation
        common_args = self.parse_common_tags(xml_elem)
        wake_up_by_controller_supported: bool | None = None
        for child_elem in xml_elem:
            match child_elem.tag:
                case tag if tag in self.common_tags:
                    pass
                case 'WAKE-UP-BY-CONTROLLER-SUPPORTED':
                    wake_up_by_controller_supported = self.parse_boolean_node(child_elem)
                case _:
                    self.log_unexpected(xml_elem, child_elem)
        controller = CanCommunicationController(
            wake_up_by_controller_supported=wake_up_by_controller_supported,
            **common_args,
        )
        return controller

    def _parse_can_connector(self, xml_elem: Element) -> CanCommunicationConnector:
        common_args = self.parse_common_tags(xml_elem)
        comm_controller_ref: str | None = None
        ecu_comm_port_instances: list[CommPort] | None = None
        pnc_gateway_type: str | None = None
        create_ecu_wakeup_source: bool | None = None
        pnc_wakeup_can_id: int | None = None
        pnc_wakeup_can_id_mask: int | None = None
        pnc_wakeup_data_mask: int | None = None
        pnc_wakeup_dlc: int | None = None
        pnc_wakeup_can_id_extended: bool | None = None
        for child_elem in xml_elem:
            match child_elem.tag:
                case tag if tag in self.common_tags:
                    pass
                case 'COMM-CONTROLLER-REF':
                    comm_controller_ref = self.parse_text_node(child_elem)
                case 'ECU-COMM-PORT-INSTANCES':  # TODO: Full implementation
                    ecu_comm_port_instances = self.parse_variable_element_list(child_elem, {
                        'FRAME-PORT': self._parse_comm_port,
                        'I-PDU-PORT': self._parse_comm_port,
                        'I-SIGNAL-PORT': self._parse_comm_port,
                    })
                case 'PNC-GATEWAY-TYPE':
                    pnc_gateway_type = self.parse_text_node(child_elem)
                case 'CREATE-ECU-WAKEUP-SOURCE':
                    create_ecu_wakeup_source = self.parse_boolean_node(child_elem)
                case 'PNC-WAKEUP-CAN-ID':
                    pnc_wakeup_can_id = self.parse_int_node(child_elem)
                case 'PNC-WAKEUP-CAN-ID-MASK':
                    pnc_wakeup_can_id_mask = self.parse_int_node(child_elem)
                case 'PNC-WAKEUP-DATA-MASK':
                    pnc_wakeup_data_mask = self.parse_int_node(child_elem)
                case 'PNC-WAKEUP-DLC':
                    pnc_wakeup_dlc = self.parse_int_node(child_elem)
                case 'PNC-WAKEUP-CAN-ID-EXTENDED':
                    pnc_wakeup_can_id_extended = self.parse_boolean_node(child_elem)
                case _:
                    self.log_unexpected(xml_elem, child_elem)
        connector = CanCommunicationConnector(
            comm_controller_ref=comm_controller_ref,
            ecu_comm_port_instances=ecu_comm_port_instances,
            pnc_gateway_type=pnc_gateway_type,
            create_ecu_wakeup_source=create_ecu_wakeup_source,
            pnc_wakeup_can_id=pnc_wakeup_can_id,
            pnc_wakeup_can_id_mask=pnc_wakeup_can_id_mask,
            pnc_wakeup_data_mask=pnc_wakeup_data_mask,
            pnc_wakeup_dlc=pnc_wakeup_dlc,
            pnc_wakeup_can_id_extended=pnc_wakeup_can_id_extended,
            **common_args,
        )
        return connector

    def _parse_eth_controller(self, xml_elem: Element) -> EthernetCommunicationController:
        common_args = self.parse_common_tags(xml_elem)
        ports = None
        ports_elem = xml_elem.find('ETHERNET-COMMUNICATION-CONTROLLER-VARIANTS/ETHERNET-COMMUNICATION-CONTROLLER-CONDITIONAL/COUPLING-PORTS')
        if ports_elem is not None:
            ports = self.parse_variable_element_list(ports_elem, {'COUPLING-PORT': self._parse_coupling_port})
        controller = EthernetCommunicationController(
            coupling_ports=ports,
            **common_args,
        )
        return controller

    def _parse_coupling_port(self, xml_elem: Element) -> CouplingPort:
        common_args = self.parse_common_tags(xml_elem)
        port = CouplingPort(**common_args)
        return port

    def _parse_eth_connector(self, xml_elem: Element) -> EthernetCommunicationConnector | None:
        common_args = self.parse_common_tags(xml_elem)
        controller_ref = self.parse_text_node(xml_elem.find('COMM-CONTROLLER-REF'))
        port_elem = xml_elem.find('ECU-COMM-PORT-INSTANCES')
        if port_elem is None:
            self._logger.error(f'Missing <ECU-COMM-PORT-INSTANCES> in {xml_elem.tag}')
            return None
        port_instances = self.parse_variable_element_list(port_elem, {
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
        try:
            port_type = tag2type[xml_elem.tag]
        except KeyError:
            self._logger.error(f'Unexpected comm port tag: {xml_elem.tag}')
            return None
        common_args = self.parse_common_tags(xml_elem)
        direction = self.parse_text_node(xml_elem.find('COMMUNICATION-DIRECTION'))
        port = port_type(
            communication_direction=direction,
            **common_args,
        )
        return port

    def _parse_eth_tcp_ip_props(self, xml_elem: Element, parent: ArObject | None) -> EthTcpIpProps | None:
        common_args = self.parse_common_tags(xml_elem)
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

    def _parse_gateway(self, xml_elem: Element, parent: ArObject | None) -> Gateway | None:
        common_args = self.parse_common_tags(xml_elem)
        ecu_ref: str | None = None
        frames: list[FrameMapping] | None = None
        pdus: list[IPduMapping] | None = None
        signals: list[ISignalMapping] | None = None
        for child_elem in xml_elem:
            match child_elem.tag:
                case tag if tag in self.common_tags:
                    pass
                case 'ECU-REF':
                    ecu_ref = self.parse_text_node(xml_elem.find('ECU-REF'))
                case 'FRAME-MAPPINGS':
                    frames = self.parse_element_list(child_elem, self._parse_frame_mapping)
                case 'I-PDU-MAPPINGS':
                    pdus = self.parse_element_list(child_elem, self._parse_i_pdu_mapping)
                case 'SIGNAL-MAPPINGS':
                    signals = self.parse_element_list(child_elem, self._parse_i_signal_mapping, 'I-SIGNAL-MAPPING')
                case _:
                    self.log_unexpected(xml_elem, child_elem)
        if ecu_ref is None:
            self.log_missing_required(xml_elem, 'ECU-REF')
            return None
        return Gateway(
            ecu_ref=ecu_ref,
            frame_mappings=frames,
            i_pdu_mappings=pdus,
            signal_mappings=signals,
            parent=parent,
            **common_args,
        )

    def _parse_frame_mapping(self, xml_elem: Element) -> FrameMapping:
        return FrameMapping(
            source_frame_ref=self.parse_text_node(xml_elem.find('SOURCE-FRAME-REF')),
            target_frame_ref=self.parse_text_node(xml_elem.find('TARGET-FRAME-REF')),
        )

    def _parse_i_pdu_mapping(self, xml_elem: Element) -> IPduMapping:
        def parse_target_pdu() -> TargetIPduRef | None:
            target_pdu_elem = xml_elem.find('TARGET-I-PDU')
            if target_pdu_elem is None:
                return None
            # TODO: Implement default value parsing
            return TargetIPduRef(
                target_i_pdu_ref=self.parse_text_node(target_pdu_elem.find('TARGET-I-PDU-REF')),
            )

        return IPduMapping(
            source_i_pdu_ref=self.parse_text_node(xml_elem.find('SOURCE-I-PDU-REF')),
            target_i_pdu=parse_target_pdu(),
            pdu_max_length=self.parse_int_node(xml_elem.find('PDU-MAX-LENGTH')),
            pdu_r_tp_chunk_size=self.parse_int_node(xml_elem.find('PDUR-TP-CHUNK-SIZE')),
        )

    def _parse_i_signal_mapping(self, xml_elem: Element) -> ISignalMapping:
        return ISignalMapping(
            source_signal_ref=self.parse_text_node(xml_elem.find('SOURCE-SIGNAL-REF')),
            target_signal_ref=self.parse_text_node(xml_elem.find('TARGET-SIGNAL-REF')),
        )
