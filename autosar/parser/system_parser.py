from xml.etree.ElementTree import Element

from autosar.ar_object import ArObject
from autosar.parser.parser_base import ElementParser
from autosar.system import (
    System,
    SystemMapping,
    ClientServerToSignalMapping,
    SenderReceiverToSignalMapping,
    TriggerToSignalMapping,
    ClientServerOperationInstanceRef,
    DataElementInstanceRef,
    TriggerInstanceRef,
)


class SystemParser(ElementParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_supported_tags(self):
        return ['SYSTEM']

    def parse_element(self, xml_element: Element, parent: ArObject | None = None) -> System | None:
        if xml_element.tag == 'SYSTEM':
            return self.parse_system(xml_element, parent)
        return None

    def parse_system(self, xml_root: Element, parent: ArObject | None = None) -> System | None:
        """
        parses <SYSTEM>
        """
        assert (xml_root.tag == 'SYSTEM')
        xml_name = xml_root.find('SHORT-NAME')
        if xml_name is None:
            self._logger.error('Expected to find <SHORT-NAME> inside <SYSTEM> tag')
            return None
        system = System(self.parse_text_node(xml_name), parent)
        for xml_elem in xml_root.findall('./*'):
            match xml_elem.tag:
                case 'SHORT-NAME':
                    pass
                case 'ADMIN-DATA':
                    system.admin_data = self.parse_admin_data_node(xml_elem)
                case 'FIBEX-ELEMENT-REFS' | 'FIBEX-ELEMENTS':
                    self._parse_fibex_element_refs(xml_elem, system)
                case 'MAPPINGS':
                    system.mappings = self._parse_element_list(
                        xml_elem,
                        {'SYSTEM-MAPPING': self._parse_system_mapping},
                    )
                case 'SOFTWARE-COMPOSITION':
                    self._logger.warning(f'Parser for {xml_elem.tag} is not implemented')
                case _:
                    self._logger.warning(f'Unexpected tag for {xml_root.tag}: {xml_elem.tag}')
        return system

    def _parse_fibex_element_refs(self, xml_root: Element, system: System):
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'FIBEX-ELEMENT-REF':
                element_ref = self.parse_text_node(xml_elem)
                if element_ref is not None:
                    system.fibex_element_refs.append(element_ref)
            elif xml_elem.tag == 'FIBEX-ELEMENT-REF-CONDITIONAL':
                element_ref = self.parse_text_node(xml_elem.find('FIBEX-ELEMENT-REF'))
                if element_ref is not None:
                    system.fibex_element_refs.append(element_ref)
            else:
                self._logger.error(f'Unexpected tag for {xml_root.tag}: {xml_elem.tag}')

    def _parse_system_mapping(self, xml_root: Element) -> SystemMapping:
        name = self.parse_text_node(xml_root.find('SHORT-NAME'))
        mapping = SystemMapping(name)
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'SHORT-NAME':
                pass
            elif xml_elem.tag == 'DATA-MAPPINGS':
                mapping.data_mappings = self._parse_element_list(xml_elem, {
                    'CLIENT-SERVER-TO-SIGNAL-MAPPING': self._parse_client_server_mapping,
                    'SENDER-RECEIVER-TO-SIGNAL-MAPPING': self._parse_sender_receiver_mapping,
                    'TRIGGER-TO-SIGNAL-MAPPING': self._parse_trigger_mapping,
                })
            elif xml_elem.tag == 'SW-MAPPINGS':
                self._logger.warning(f'Parser for {xml_elem.tag} is not implemented')
                self._parse_sw_mapping(xml_elem)
            elif xml_elem.tag == 'SW-IMPL-MAPPINGS':
                self._logger.warning(f'Parser for {xml_elem.tag} is not implemented')
                self._parse_sw_impl_mapping(xml_elem)
            else:
                self._logger.warning(f'Unexpected tag for {xml_root.tag}: {xml_elem.tag}')
        return mapping

    def _parse_instance_ref_common_params(self, xml_elem: Element) -> dict[str, str] | None:
        composition_ref = self.parse_text_node(xml_elem.find('CONTEXT-COMPOSITION-REF'))
        component_ref = self.parse_text_node(xml_elem.find('CONTEXT-COMPONENT-REF'))
        port_ref = self.parse_text_node(xml_elem.find('CONTEXT-PORT-REF'))
        if composition_ref is None or component_ref is None or port_ref is None:
            return None
        common_params = {
            'context_composition_ref': composition_ref,
            'context_component_ref': component_ref,
            'context_port_ref': port_ref,
        }
        return common_params

    def _parse_client_server_mapping(self, xml_root: Element) -> ClientServerToSignalMapping | None:
        call_signal_ref = self.parse_text_node(xml_root.find('CALL-SIGNAL-REF'))
        return_signal_ref = self.parse_text_node(xml_root.find('RETURN-SIGNAL-REF'))
        if call_signal_ref is None or return_signal_ref is None:
            return None
        instance_ref_elem = xml_root.find('CLIENT-SERVER-OPERATION-IREF')
        if instance_ref_elem is None:
            return None
        common_params = self._parse_instance_ref_common_params(instance_ref_elem)
        operation_ref = self.parse_text_node(instance_ref_elem.find('TARGET-OPERATION-REF'))
        if common_params is None or operation_ref is None:
            return None
        instance_ref = ClientServerOperationInstanceRef(
            target_operation_ref=operation_ref,
            **common_params,
        )
        mapping = ClientServerToSignalMapping(
            call_signal_ref=call_signal_ref,
            return_signal_ref=return_signal_ref,
            instance_ref=instance_ref,
        )
        return mapping

    def _parse_sender_receiver_mapping(self, xml_root: Element) -> SenderReceiverToSignalMapping | None:
        system_signal_ref = self.parse_text_node(xml_root.find('SYSTEM-SIGNAL-REF'))
        instance_ref_elem = xml_root.find('DATA-ELEMENT-IREF')
        if system_signal_ref is None or instance_ref_elem is None:
            return None
        common_params = self._parse_instance_ref_common_params(instance_ref_elem)
        data_prototype_ref = self.parse_text_node(instance_ref_elem.find('TARGET-DATA-PROTOTYPE-REF'))
        if common_params is None or data_prototype_ref is None:
            return None
        instance_ref = DataElementInstanceRef(
            target_data_prototype_ref=data_prototype_ref,
            **common_params,
        )
        mapping = SenderReceiverToSignalMapping(
            system_signal_ref=system_signal_ref,
            instance_ref=instance_ref,
        )
        return mapping

    def _parse_trigger_mapping(self, xml_root: Element) -> TriggerToSignalMapping | None:
        system_signal_ref = self.parse_text_node(xml_root.find('SYSTEM-SIGNAL-REF'))
        instance_ref_elem = xml_root.find('TRIGGER-IREF')
        if system_signal_ref is None or instance_ref_elem is None:
            return None
        common_params = self._parse_instance_ref_common_params(instance_ref_elem)
        trigger_ref = self.parse_text_node(instance_ref_elem.find('TARGET-TRIGGER-REF'))
        if common_params is None or trigger_ref is None:
            return None
        instance_ref = TriggerInstanceRef(
            target_trigger_ref=trigger_ref,
            **common_params,
        )
        mapping = TriggerToSignalMapping(
            system_signal_ref=system_signal_ref,
            instance_ref=instance_ref,
        )
        return mapping

    def _parse_sw_impl_mapping(self, xml_root: Element):
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag != 'SWC-TO-IMPL-MAPPING':
                self._logger.error(f'Unexpected tag for {xml_root.tag}: {xml_elem.tag}')

    def _parse_sw_mapping(self, xml_root):
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag != 'SWC-TO-ECU-MAPPING':
                self._logger.error(f'Unexpected tag for {xml_root.tag}: {xml_elem.tag}')
