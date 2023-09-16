from xml.etree.ElementTree import Element

from autosar.ar_object import ArObject
from autosar.some_ip_tp import SomeIpConfig, SomeIpConnection, SomeIpTPChannel
from autosar.parser.parser_base import ElementParser


class SomeIpTpParser(ElementParser):
    def get_supported_tags(self):
        return ['SOMEIP-TP-CONFIG']

    def parse_element(self, xml_element: Element, parent: ArObject | None = None):
        if xml_element.tag == 'SOMEIP-TP-CONFIG':
            return self._parse_tp_config(xml_element, parent)
        return None

    def _parse_tp_config(self, xml_elem: Element, parent: ArObject | None) -> SomeIpConfig:
        common_args = self._parse_common_tags(xml_elem)
        ref = None
        channels = None
        connections = None
        for child_elem in xml_elem.findall('./*'):
            match child_elem.tag:
                case tag if tag in self.common_tags:
                    pass
                case 'COMMUNICATION-CLUSTER-REF':
                    ref = self.parse_text_node(child_elem)
                case 'TP-CHANNELS':
                    channels = self._parse_element_list(
                        child_elem,
                        {'SOMEIP-TP-CHANNEL': self._parse_channel},
                    )
                case 'TP-CONNECTIONS':
                    connections = self._parse_element_list(
                        child_elem,
                        {'SOMEIP-TP-CONNECTION': self._parse_connection},
                    )
                case _:
                    self._logger.warning(f'Unexpected tag for {xml_elem.tag}: {child_elem.tag}')
        config = SomeIpConfig(
            communication_cluster_ref=ref,
            tp_channels=channels,
            tp_connections=connections,
            parent=parent,
            **common_args,
        )
        return config

    def _parse_channel(self, xml_elem: Element) -> SomeIpTPChannel:
        common_args = self._parse_common_tags(xml_elem)
        separation_time = self.parse_number_node(xml_elem.find('SEPARATION-TIME'))
        channel = SomeIpTPChannel(
            separation_time=separation_time,
            **common_args,
        )
        return channel

    def _parse_connection(self, xml_elem: Element) -> SomeIpConnection:
        separation_time = self.parse_number_node(xml_elem.find('SEPARATION-TIME'))
        channel_ref = self.parse_text_node(xml_elem.find('TP-CHANNEL-REF'))
        sdu_ref = self.parse_text_node(xml_elem.find('TP-SDU-REF'))
        transport_ref = self.parse_text_node(xml_elem.find('TRANSPORT-PDU-REF'))
        connection = SomeIpConnection(
            separation_time=separation_time,
            tp_channel_ref=channel_ref,
            tp_sdu_ref=sdu_ref,
            transport_pdu_ref=transport_ref,
        )
        return connection
