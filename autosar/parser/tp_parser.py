from typing import Callable
from xml.etree.ElementTree import Element

from autosar.model.ar_object import ArObject
from autosar.model.transport_protocol import (
    AnyTpConfig,
    CanTpConfig,
    CanTpAddress,
    CanTpChannel,
    CanTpConnection,
    CanTpEcu,
    CanTpNode,
)
from autosar.parser.parser_base import ElementParser


class TransportProtocolParser(ElementParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.switcher: dict[str, Callable[[Element, ArObject | None], AnyTpConfig | None]] = {
            'CAN-TP-CONFIG': self._parse_can_tp_config,
        }

    def get_supported_tags(self):
        return self.switcher.keys()

    def parse_element(self, xml_element: Element, parent: ArObject | None = None) -> AnyTpConfig | None:
        if xml_element.tag not in self.switcher:
            return None
        element_parser = self.switcher[xml_element.tag]
        return element_parser(xml_element, parent)

    def _parse_can_tp_config(self, xml_elem: Element, parent: ArObject | None = None) -> CanTpConfig:
        common_args = self.parse_common_tags(xml_elem)
        cluster_ref: str | None = None
        addresses: list[CanTpAddress] | None = None
        channels: list[CanTpChannel] | None = None
        connections: list[CanTpConnection] | None = None
        ecus: list[CanTpEcu] | None = None
        nodes: list[CanTpNode] | None = None
        for child_elem in xml_elem:
            match child_elem.tag:
                case tag if tag in self.common_tags:
                    pass
                case 'COMMUNICATION-CLUSTER-REF':
                    cluster_ref = self.parse_text_node(child_elem)
                case 'TP-ADDRESSS':
                    addresses = self.parse_element_list(
                        child_elem,
                        self._parse_can_tp_address,
                        'CAN-TP-ADDRESS',
                    )
                case 'TP-CHANNELS':
                    channels = self.parse_element_list(
                        child_elem,
                        self._parse_can_tp_channel,
                        'CAN-TP-CHANNEL',
                    )
                case 'TP-CONNECTIONS':
                    connections = self.parse_element_list(
                        child_elem,
                        self._parse_can_tp_connection,
                        'CAN-TP-CONNECTION',
                    )
                case 'TP-ECUS':
                    ecus = self.parse_element_list(
                        child_elem,
                        self._parse_can_tp_ecu,
                        'CAN-TP-ECU',
                    )
                case 'TP-NODES':
                    nodes = self.parse_element_list(
                        child_elem,
                        self._parse_can_tp_node,
                        'CAN-TP-NODE',
                    )
                case _:
                    self.log_unexpected(xml_elem, child_elem)
        return CanTpConfig(
            communication_cluster_ref=cluster_ref,
            tp_addresses=addresses,
            tp_channels=channels,
            tp_connections=connections,
            tp_ecus=ecus,
            tp_nodes=nodes,
            parent=parent,
            **common_args,
        )

    def _parse_can_tp_address(self, xml_elem: Element) -> CanTpAddress:
        return CanTpAddress(
            tp_address=self.parse_int_node(xml_elem.find('TP-ADDRESS')),
            tp_address_extension_value=self.parse_int_node(xml_elem.find('TP-ADDRESS-EXTENSION-VALUE')),
            **self.parse_common_tags(xml_elem),
        )

    def _parse_can_tp_channel(self, xml_elem: Element) -> CanTpChannel:
        return CanTpChannel(
            channel_id=self.parse_int_node(xml_elem.find('CHANNEL-ID')),
            channel_mode=self.parse_text_node(xml_elem.find('CHANNEL-MODE')),
            **self.parse_common_tags(xml_elem),
        )

    def _parse_can_tp_connection(self, xml_elem: Element) -> CanTpConnection:
        return CanTpConnection(
            addressing_format=self.parse_text_node(xml_elem.find('ADDRESSING-FORMAT')),
            can_tp_channel_ref=self.parse_text_node(xml_elem.find('CAN-TP-CHANNEL-REF')),
            data_pdu_ref=self.parse_text_node(xml_elem.find('DATA-PDU-REF')),
            padding_activation=self.parse_boolean_node(xml_elem.find('PADDING-ACTIVATION')),
            tp_sdu_ref=self.parse_text_node(xml_elem.find('TP-SDU-REF')),
            cancellation=self.parse_boolean_node(xml_elem.find('CANCELLATION')),
            flow_control_pdu_ref=self.parse_text_node(xml_elem.find('FLOW-CONTROL-PDU-REF')),
            max_block_size=self.parse_int_node(xml_elem.find('MAX-BLOCK-SIZE')),
            multicast_ref=self.parse_text_node(xml_elem.find('MULTICAST-REF')),
            receiver_refs=list(self.child_string_nodes(xml_elem.find('RECEIVER-REFS'))),
            ta_type=self.parse_text_node(xml_elem.find('TA-TYPE')),
            timeout_br=self.parse_number_node(xml_elem.find('TIMEOUT-BR')),
            timeout_bs=self.parse_number_node(xml_elem.find('TIMEOUT-BS')),
            timeout_cr=self.parse_number_node(xml_elem.find('TIMEOUT-CR')),
            timeout_cs=self.parse_number_node(xml_elem.find('TIMEOUT-CS')),
            transmitter_ref=self.parse_text_node(xml_elem.find('TRANSMITTER-REF')),
        )

    def _parse_can_tp_ecu(self, xml_elem: Element) -> CanTpEcu:
        return CanTpEcu(
            ecu_instance_ref=self.parse_text_node(xml_elem.find('ECU-INSTANCE-REF')),
            cycle_time_main_function=self.parse_number_node(xml_elem.find('CYCLE-TIME-MAIN-FUNCTION')),
        )

    def _parse_can_tp_node(self, xml_elem: Element) -> CanTpNode:
        return CanTpNode(
            connector_ref=self.parse_text_node(xml_elem.find('CONNECTOR-REF')),
            tp_address_ref=self.parse_text_node(xml_elem.find('TP-ADDRESS-REF')),
            max_fc_wait=self.parse_int_node(xml_elem.find('MAX-FC-WAIT')),
            st_min=self.parse_number_node(xml_elem.find('ST-MIN')),
            timeout_ar=self.parse_number_node(xml_elem.find('TIMEOUT-AR')),
            timeout_as=self.parse_number_node(xml_elem.find('TIMEOUT-AS')),
            **self.parse_common_tags(xml_elem),
        )
