from xml.etree.ElementTree import Element

from autosar.model.ar_object import ArObject
from autosar.model.can_cluster import (
    CanCluster,
    CanClusterVariants,
    CanPhysicalChannel,
    CanFrameTriggering,
    RxIdentifierRange,
)
from autosar.model.communication_cluster import (
    ISignalTriggering,
    PduTriggering,
    TriggerIPduSendCondition,
)
from autosar.parser.parser_base import ElementParser


class CanClusterParser(ElementParser):
    def get_supported_tags(self):
        return ['CAN-CLUSTER']

    def parse_element(self, xml_element: Element, parent: ArObject | None = None) -> CanClusterVariants | None:
        if xml_element.tag == 'CAN-CLUSTER':
            return self._parse_can_cluster(xml_element, parent)
        return None

    def _parse_can_cluster(self, xml_elem: Element, parent: ArObject | None) -> CanClusterVariants:
        variation_point: list[tuple] = []
        common_args = self.parse_common_tags(xml_elem)
        for child_elem in xml_elem:
            match child_elem.tag:
                case tag if tag in self.common_tags:
                    pass
                case 'CAN-CLUSTER-VARIANTS':
                    variation_point = self.parse_variable_element_list(
                        child_elem,
                        {'CAN-CLUSTER-CONDITIONAL': self._parse_can_cluster_variation},
                    )
                case _:
                    self.log_unexpected(xml_elem, child_elem)
        cluster = CanClusterVariants(
            variants=(
                CanCluster(
                    protocol_name=n,
                    protocol_version=v,
                    baudrate=baud,
                    can_fd_baudrate=fd,
                    can_xl_baudrate=xl,
                    physical_channels=channels,
                    parent=parent,
                    **common_args,
                )
                for n, v, baud, fd, xl, channels in variation_point
            ),
            parent=parent,
            **common_args,
        )
        return cluster

    def _parse_can_cluster_variation(self, xml_elem: Element) -> tuple:
        protocol_name: str | None = None
        protocol_version: str | None = None
        baud_rate: int | None = None
        can_fd_baudrate: int | None = None
        can_xl_baudrate: int | None = None
        physical_channels: list[CanPhysicalChannel] | None = None
        for child_elem in xml_elem:
            match child_elem.tag:
                case 'PROTOCOL-NAME':
                    protocol_name = self.parse_text_node(child_elem)
                case 'PROTOCOL-VERSION':
                    protocol_version = self.parse_text_node(child_elem)
                case 'BAUDRATE':
                    baud_rate = self.parse_int_node(child_elem)
                case 'CAN-FD-BAUDRATE':
                    can_fd_baudrate = self.parse_int_node(child_elem)
                case 'CAN-XL-BAUDRATE':
                    can_xl_baudrate = self.parse_int_node(child_elem)
                case 'PHYSICAL-CHANNELS':
                    physical_channels = self.parse_variable_element_list(
                        child_elem,
                        {'CAN-PHYSICAL-CHANNEL': self._parse_can_phys_channel},
                    )
                case 'CAN-CLUSTER-BUS-OFF-RECOVERY':
                    self.log_not_implemented(xml_elem, child_elem)
                case _:
                    self.log_unexpected(xml_elem, child_elem)
        return (
            protocol_name,
            protocol_version,
            baud_rate,
            can_fd_baudrate,
            can_xl_baudrate,
            physical_channels,
        )

    def _parse_can_phys_channel(self, xml_elem: Element) -> CanPhysicalChannel:
        comm_connectors_refs: list[str] | None = None
        frame_triggerings = None
        signal_triggerings = None
        pdu_triggerings = None
        managed_channels_refs: list[str] | None = None
        common_tags = self.parse_common_tags(xml_elem)
        for child_elem in xml_elem:
            match child_elem.tag:
                case tag if tag in self.common_tags:
                    pass
                case 'COMM-CONNECTORS':
                    comm_connectors_refs = self._parse_comm_connectors_refs(child_elem)
                case 'FRAME-TRIGGERINGS':
                    frame_triggerings = self.parse_variable_element_list(
                        child_elem,
                        {'CAN-FRAME-TRIGGERING': self._parse_can_frame_triggering},
                    )
                case 'I-SIGNAL-TRIGGERINGS':
                    signal_triggerings = self.parse_variable_element_list(
                        child_elem,
                        {'I-SIGNAL-TRIGGERING': self._parse_i_signal_triggering},
                    )
                case 'PDU-TRIGGERINGS':
                    pdu_triggerings = self.parse_variable_element_list(
                        child_elem,
                        {'PDU-TRIGGERING': self._parse_pdu_triggering},
                    )
                case 'MANAGED-PHYSICAL-CHANNEL-REFS':
                    managed_channels_refs = self.parse_variable_element_list(
                        child_elem,
                        {'PHYSICAL-CHANNEL-REF': self.parse_text_node},
                    )
                case _:
                    self.log_unexpected(xml_elem, child_elem)
        channel = CanPhysicalChannel(
            comm_connectors_refs=comm_connectors_refs,
            frame_triggerings=frame_triggerings,
            i_signal_triggerings=signal_triggerings,
            pdu_triggerings=pdu_triggerings,
            managed_physical_channels_refs=managed_channels_refs,
            **common_tags,
        )
        return channel

    def _parse_comm_connectors_refs(self, xml_elem: Element) -> list[str]:
        refs = []
        for child_elem in xml_elem.findall('COMMUNICATION-CONNECTOR-REF-CONDITIONAL'):
            connector_ref = self.parse_text_node(child_elem.find('COMMUNICATION-CONNECTOR-REF'))
            if connector_ref is not None:
                refs.append(connector_ref)
        return refs

    def _parse_can_frame_triggering(self, xml_elem: Element) -> CanFrameTriggering | None:
        _NOT_IMPLEMENTED_TAGS = (
            'ABSOLUTELY-SCHEDULED-TIMINGS',
            'CAN-XL-FRAME-TRIGGERING-PROPS',
            'J-1939REQUESTABLE',
        )
        frame_ref: str | None = None
        port_refs: list[str] | None = None
        pdu_trig_refs: list[str] | None = None
        addressing_mode: str | None = None
        identifier: int | None = None
        rx_behavior: str | None = None
        tx_behavior: str | None = None
        rx_mask: str | None = None
        tx_mask: str | None = None
        rx_id_range: RxIdentifierRange | None = None
        common_tags = self.parse_common_tags(xml_elem)
        for child_elem in xml_elem:
            match child_elem.tag:
                case tag if tag in self.common_tags:
                    pass
                case tag if tag in _NOT_IMPLEMENTED_TAGS:
                    self.log_not_implemented(xml_elem, child_elem)
                case 'CAN-ADDRESSING-MODE':
                    addressing_mode = self.parse_text_node(child_elem)
                case 'IDENTIFIER':
                    identifier = self.parse_int_node(child_elem)
                case 'FRAME-REF':
                    frame_ref = self.parse_text_node(child_elem)
                case 'FRAME-PORT-REFS':
                    port_refs = list(self.child_string_nodes(child_elem, 'FRAME-PORT-REF'))
                case 'PDU-TRIGGERINGS':
                    pdu_trig_refs = list(self.variation_child_string_nodes(child_elem, 'PDU-TRIGGERING-REF'))
                case 'CAN-FRAME-RX-BEHAVIOR':
                    rx_behavior = self.parse_text_node(child_elem)
                case 'CAN-FRAME-TX-BEHAVIOR':
                    tx_behavior = self.parse_text_node(child_elem)
                case 'RX-MASK':
                    rx_mask = self.parse_text_node(child_elem)
                case 'TX-MASK':
                    tx_mask = self.parse_text_node(child_elem)
                case 'RX-IDENTIFIER-RANGE':
                    lower = self.parse_int_node(child_elem.find('LOWER-CAN-ID'))
                    upper = self.parse_int_node(child_elem.find('UPPER-CAN-ID'))
                    if lower is None:
                        self.log_missing_required(child_elem, 'LOWER-CAN-ID')
                        continue
                    if upper is None:
                        self.log_missing_required(child_elem, 'UPPER-CAN-ID')
                        continue
                    rx_id_range = RxIdentifierRange(lower_can_id=lower, upper_can_id=upper)
                case _:
                    self.log_unexpected(xml_elem, child_elem)
        if addressing_mode is None:
            self.log_missing_required(xml_elem, 'CAN-ADDRESSING-MODE')
            return None
        if frame_ref is None:
            self.log_missing_required(xml_elem, 'FRAME-REF')
            return None
        triggering = CanFrameTriggering(
            can_addressing_mode=addressing_mode,
            identifier=identifier,
            can_frame_rx_behavior=rx_behavior,
            can_frame_tx_behavior=tx_behavior,
            rx_mask=rx_mask,
            tx_mask=tx_mask,
            rx_identifier_range=rx_id_range,
            frame_ref=frame_ref,
            frame_ports_refs=port_refs,
            pdu_triggerings_refs=pdu_trig_refs,
            **common_tags,
        )
        return triggering

    def _parse_i_signal_triggering(self, xml_elem: Element) -> ISignalTriggering:
        signal_ref: str | None = None
        group_ref: str | None = None
        port_refs: list[str] | None = None
        common_tags = self.parse_common_tags(xml_elem)
        for child_elem in xml_elem.findall('./*'):
            match child_elem.tag:
                case tag if tag in self.common_tags:
                    pass
                case 'I-SIGNAL-REF':
                    signal_ref = self.parse_text_node(child_elem)
                case 'I-SIGNAL-GROUP-REF':
                    group_ref = self.parse_text_node(child_elem)
                case 'I-SIGNAL-PORT-REFS':
                    port_refs = list(self.child_string_nodes(child_elem, 'I-SIGNAL-PORT-REF'))
                case _:
                    self.log_unexpected(xml_elem, child_elem)
        triggering = ISignalTriggering(
            i_signal_ref=signal_ref,
            i_signal_port_refs=port_refs,
            i_signal_group_ref=group_ref,
            **common_tags,
        )
        return triggering

    def _parse_pdu_triggering(self, xml_elem: Element) -> PduTriggering | None:
        pdu_ref: str | None = None
        port_refs: list[str] | None = None
        triggering_refs: list[str] | None = None
        conditions: list[TriggerIPduSendCondition] = []
        crypto_profile: str | None = None
        common_tags = self.parse_common_tags(xml_elem)
        for child_elem in xml_elem:
            match child_elem.tag:
                case tag if tag in self.common_tags:
                    pass
                case 'I-PDU-REF':
                    pdu_ref = self.parse_text_node(child_elem)
                case 'I-PDU-PORT-REFS':
                    port_refs = list(self.child_string_nodes(child_elem, 'I-SIGNAL-PORT-REF'))
                case 'I-SIGNAL-TRIGGERINGS':
                    triggering_refs = list(self.variation_child_string_nodes(child_elem, 'I-SIGNAL-TRIGGERING-REF'))
                case 'TRIGGER-I-PDU-SEND-CONDITIONS':
                    for sub_elem in child_elem:
                        if sub_elem.tag != 'TRIGGER-I-PDU-SEND-CONDITION':
                            self.log_unexpected(child_elem, sub_elem)
                            continue
                        condition = TriggerIPduSendCondition(
                            mode_declaration_refs=list(map(self.parse_text_node, sub_elem.findall('MODE-DECLARATION-REF'))),
                        )
                        conditions.append(condition)
                case 'SEC-OC-CRYPTO-MAPPING-REF':
                    crypto_profile = self.parse_text_node(child_elem)
                case _:
                    self.log_unexpected(xml_elem, child_elem)
        if pdu_ref is None:
            self.log_missing_required(xml_elem, 'I-PDU-REF')
            return None
        triggering = PduTriggering(
            i_pdu_ref=pdu_ref,
            i_pdu_port_refs=port_refs,
            i_signal_triggering_refs=triggering_refs,
            sec_oc_crypto_mapping_ref=crypto_profile,
            trigger_i_pdu_send_conditions=conditions,
            **common_tags,
        )
        return triggering
