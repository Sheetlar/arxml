from typing import Callable
from xml.etree.ElementTree import Element

from autosar.ar_object import ArObject
from autosar.base import split_ref, has_admin_data, parse_admin_data_node
from autosar.component import (
    ApplicationSoftwareComponent,
    ComplexDeviceDriverComponent,
    ServiceComponent,
    ParameterComponent,
    SensorActuatorComponent,
    NvBlockComponent,
    CompositionComponent,
    ComponentPrototype,
    ProviderInstanceRef,
    AssemblyConnector,
    RequesterInstanceRef,
    InnerPortInstanceRef,
    DelegationConnector,
    OuterPortRef,
    ComponentType,
)
from autosar.constant import ValueAR4
from autosar.parser.behavior_parser import BehaviorParser
from autosar.parser.constant_parser import ConstantParser
from autosar.parser.parser_base import ElementParser
from autosar.port import (
    RequirePort,
    OperationComSpec,
    DataElementComSpec,
    ProvidePort,
    ModeSwitchComSpec,
    ParameterComSpec,
    NvProvideComSpec,
    NvRequireComSpec,
)


def _get_data_elem_name_from_com_spec(xml_elem: Element, port_interface_ref: str) -> str | None:
    if xml_elem.find('./DATA-ELEMENT-REF') is not None:
        data_elem_ref = split_ref(xml_elem.find('./DATA-ELEMENT-REF').text)
        assert (data_elem_ref is not None)
        data_elem_name = data_elem_ref.pop()
        tmp = '/' + '/'.join(data_elem_ref)
        if port_interface_ref == tmp:
            return data_elem_name
    return None


def _get_operation_name_from_com_spec(xml_elem: Element, port_interface_ref: str) -> str | None:
    xml_operation = xml_elem.find('./OPERATION-REF')
    if xml_operation is not None:
        operation_ref = split_ref(xml_operation.text)
        assert (operation_ref is not None)
        operation_name = operation_ref.pop()
        tmp = '/' + '/'.join(operation_ref)
        if port_interface_ref == tmp:
            return operation_name
    return None


def _get_parameter_name_from_com_spec(xml_elem: Element, port_interface_ref: str) -> str | None:
    if xml_elem.tag == 'PARAMETER-REF':
        parameter_ref = split_ref(xml_elem.text)
        assert (parameter_ref is not None)
        name = parameter_ref.pop()
        tmp = '/' + '/'.join(parameter_ref)
        if port_interface_ref == tmp:
            return name
    return None


def _get_variable_name_from_com_spec(xml_elem: Element, port_interface_ref: str) -> str | None:
    if xml_elem.tag == 'VARIABLE-REF':
        variable_ref = split_ref(xml_elem.text)
        assert (variable_ref is not None)
        name = variable_ref.pop()
        tmp = '/' + '/'.join(variable_ref)
        if port_interface_ref == tmp:
            return name
    return None


class ComponentTypeParser(ElementParser):
    """
    ComponentType parser
    """

    def __init__(self, version=3.0):
        super().__init__(version)
        if self.version >= 4.0:
            self.behavior_parser = BehaviorParser(version)
            self.constant_parser = ConstantParser(version)

        if 3.0 <= self.version < 4.0:
            self.switcher: dict[str, Callable[[Element, ArObject | None], ComponentType | None]] = {
                'APPLICATION-SOFTWARE-COMPONENT-TYPE': self.parse_software_component,
                'COMPLEX-DEVICE-DRIVER-COMPONENT-TYPE': self.parse_software_component,
                'COMPOSITION-TYPE': self.parse_composition_type,
                'CALPRM-COMPONENT-TYPE': self.parse_software_component,
                'SERVICE-COMPONENT-TYPE': self.parse_software_component,
            }
        elif self.version >= 4.0:
            self.switcher: dict[str, Callable[[Element, ArObject | None], ComponentType | None]] = {
                'APPLICATION-SW-COMPONENT-TYPE': self.parse_software_component,
                'COMPLEX-DEVICE-DRIVER-SW-COMPONENT-TYPE': self.parse_software_component,
                'SERVICE-COMPONENT-TYPE': self.parse_software_component,
                'PARAMETER-SW-COMPONENT-TYPE': self.parse_software_component,
                'COMPOSITION-SW-COMPONENT-TYPE': self.parse_composition_type,
                'SENSOR-ACTUATOR-SW-COMPONENT-TYPE': self.parse_software_component,
                'SERVICE-SW-COMPONENT-TYPE': self.parse_software_component,
                'NV-BLOCK-SW-COMPONENT-TYPE': self.parse_software_component
            }

    def get_supported_tags(self):
        return self.switcher.keys()

    def parse_element(self, xml_element: Element, parent: ArObject | None = None) -> ComponentType | None:
        parse_func = self.switcher.get(xml_element.tag)
        if parse_func is not None:
            return parse_func(xml_element, parent)
        return None

    def parse_software_component(self, xml_root: Element, parent: ArObject | None = None) -> ComponentType | None:
        handled_tags = ['SHORT-NAME']
        if xml_root.tag == 'APPLICATION-SOFTWARE-COMPONENT-TYPE':  # for AUTOSAR 3.x
            component_type = ApplicationSoftwareComponent(self.parse_text_node(xml_root.find('SHORT-NAME')), parent)
        elif (xml_root.tag == 'COMPLEX-DEVICE-DRIVER-COMPONENT-TYPE') or (xml_root.tag == 'COMPLEX-DEVICE-DRIVER-SW-COMPONENT-TYPE'):
            component_type = ComplexDeviceDriverComponent(self.parse_text_node(xml_root.find('SHORT-NAME')), parent)
        elif xml_root.tag == 'APPLICATION-SW-COMPONENT-TYPE':  # for AUTOSAR 4.x
            component_type = ApplicationSoftwareComponent(self.parse_text_node(xml_root.find('SHORT-NAME')), parent)
        elif (xml_root.tag == 'SERVICE-COMPONENT-TYPE') or (xml_root.tag == 'SERVICE-SW-COMPONENT-TYPE'):
            component_type = ServiceComponent(self.parse_text_node(xml_root.find('SHORT-NAME')), parent)
        elif xml_root.tag == 'CALPRM-COMPONENT-TYPE':  # for AUTOSAR 3.x
            component_type = ParameterComponent(self.parse_text_node(xml_root.find('SHORT-NAME')), parent)
        elif xml_root.tag == 'PARAMETER-SW-COMPONENT-TYPE':  # for AUTOSAR 4.x
            component_type = ParameterComponent(self.parse_text_node(xml_root.find('SHORT-NAME')), parent)
        elif xml_root.tag == 'SENSOR-ACTUATOR-SW-COMPONENT-TYPE':  # for AUTOSAR 4.x
            component_type = SensorActuatorComponent(self.parse_text_node(xml_root.find('SHORT-NAME')), parent)
        elif xml_root.tag == 'NV-BLOCK-SW-COMPONENT-TYPE':  # for AUTOSAR 4.x
            component_type = NvBlockComponent(self.parse_text_node(xml_root.find('SHORT-NAME')), parent)
        else:
            self._logger.warning(f'Unexpected tag: {xml_root.tag}')
            return None
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag in handled_tags:
                continue
            if xml_elem.tag == 'ADMIN-DATA':
                component_type.admin_data = self.parse_admin_data_node(xml_elem)
            elif xml_elem.tag == 'DESC':
                pass  # Implement later
            elif xml_elem.tag == 'PORTS':
                self.parse_component_ports(component_type, xml_root)
            elif xml_elem.tag == 'INTERNAL-BEHAVIORS':
                behaviors = xml_elem.findall('./SWC-INTERNAL-BEHAVIOR')
                if len(behaviors) > 1:
                    self._logger.error(f'{component_type}: an SWC cannot have multiple internal behaviors')
                    continue
                elif len(behaviors) == 1:
                    component_type.behavior = self.behavior_parser.parse_swc_internal_behavior(behaviors[0], component_type)
            elif xml_elem.tag == 'NV-BLOCK-DESCRIPTORS' and isinstance(component_type, NvBlockComponent):
                for descriptor_xml in xml_elem.findall('./NV-BLOCK-DESCRIPTOR'):
                    descriptor = self.behavior_parser.parse_nv_block_sw_cnv_block_descriptor(descriptor_xml, component_type)
                    component_type.nv_block_descriptors.append(descriptor)
            elif xml_elem.tag == 'CATEGORY':
                component_type.category = self.parse_text_node(xml_elem)
            else:
                self._logger.warning(f'Unexpected tag: {xml_elem.tag}')
        return component_type

    def parse_component_ports(self, component_type: ComponentType, xml_root: Element):
        xml_ports = xml_root.find('PORTS')
        assert (xml_ports is not None)
        for xml_port in xml_ports.findall('*'):
            if xml_port.tag == "R-PORT-PROTOTYPE":
                port_name = xml_port.find('SHORT-NAME').text
                port_interface_ref = self.parse_text_node(xml_port.find('REQUIRED-INTERFACE-TREF'))
                port = RequirePort(port_name, port_interface_ref, auto_create_com_spec=False, parent=component_type)
                if has_admin_data(xml_port):
                    port.admin_data = parse_admin_data_node(xml_port.find('ADMIN-DATA'))
                if xml_port.findall('./REQUIRED-COM-SPECS') is not None:
                    for xml_item in xml_port.findall('./REQUIRED-COM-SPECS/*'):
                        if xml_item.tag == 'CLIENT-COM-SPEC':
                            operation_name = _get_operation_name_from_com_spec(xml_item, port_interface_ref)
                            com_spec = OperationComSpec(operation_name)
                            port.com_spec.append(com_spec)
                        elif xml_item.tag == 'UNQUEUED-RECEIVER-COM-SPEC' or xml_item.tag == 'NONQUEUED-RECEIVER-COM-SPEC':
                            data_elem_name = _get_data_elem_name_from_com_spec(xml_item, port_interface_ref)
                            com_spec = DataElementComSpec(data_elem_name)
                            if xml_item.find('./ALIVE-TIMEOUT') is not None:
                                com_spec.alive_timeout = self.parse_text_node(xml_item.find('./ALIVE-TIMEOUT'))
                            if self.version >= 4.0:
                                xml_elem = xml_item.find('./INIT-VALUE')
                                if xml_elem is not None:
                                    com_spec.init_value, com_spec.init_value_ref = self._parse_ar4_init_value(xml_elem)
                            else:
                                if xml_item.find('./INIT-VALUE-REF') is not None:
                                    com_spec.init_value_ref = self.parse_text_node(xml_item.find('./INIT-VALUE-REF'))
                            port.com_spec.append(com_spec)
                        elif xml_item.tag == 'QUEUED-RECEIVER-COM-SPEC':
                            data_elem_name = _get_data_elem_name_from_com_spec(xml_item, port_interface_ref)
                            com_spec = DataElementComSpec(data_elem_name)
                            if xml_item.find('./QUEUE-LENGTH') is not None:
                                com_spec.queue_length = self.parse_text_node(xml_item.find('./QUEUE-LENGTH'))
                            port.com_spec.append(com_spec)
                        elif xml_item.tag == 'MODE-SWITCH-RECEIVER-COM-SPEC':
                            com_spec = self._parse_mode_switch_receiver_com_spec(xml_item)
                            port.com_spec.append(com_spec)
                        elif xml_item.tag == 'PARAMETER-REQUIRE-COM-SPEC':
                            com_spec = self._parse_parameter_com_spec(xml_item, port_interface_ref)
                            if com_spec is not None:
                                port.com_spec.append(com_spec)
                        elif xml_item.tag == 'NV-REQUIRE-COM-SPEC':
                            com_spec = self._parse_nv_require_com_spec(xml_item, port_interface_ref)
                            if com_spec is not None:
                                port.com_spec.append(com_spec)
                        else:
                            self._logger.warning(f'Parser not implemented: {xml_item.tag}')
                component_type.require_ports.append(port)
            elif xml_port.tag == 'P-PORT-PROTOTYPE':
                port_name = xml_port.find('SHORT-NAME').text
                port_interface_ref = self.parse_text_node(xml_port.find('PROVIDED-INTERFACE-TREF'))
                port = ProvidePort(port_name, port_interface_ref, auto_create_com_spec=False, parent=component_type)
                if has_admin_data(xml_port):
                    port.admin_data = parse_admin_data_node(xml_port.find('ADMIN-DATA'))
                if xml_port.findall('./PROVIDED-COM-SPECS') is not None:
                    for xml_item in xml_port.findall('./PROVIDED-COM-SPECS/*'):
                        if xml_item.tag == 'SERVER-COM-SPEC':
                            operation_name = _get_operation_name_from_com_spec(xml_item, port_interface_ref)
                            com_spec = OperationComSpec(operation_name)
                            com_spec.queue_length = self.parse_int_node(xml_item.find('QUEUE-LENGTH'))
                            port.com_spec.append(com_spec)
                        elif xml_item.tag == 'UNQUEUED-SENDER-COM-SPEC' or xml_item.tag == 'NONQUEUED-SENDER-COM-SPEC':
                            data_elem_name = _get_data_elem_name_from_com_spec(xml_item, port_interface_ref)
                            com_spec = DataElementComSpec(data_elem_name)
                            if self.version >= 4.0:
                                xml_elem = xml_item.find('./INIT-VALUE')
                                if xml_elem is not None:
                                    com_spec.init_value, com_spec.init_value_ref = self._parse_ar4_init_value(xml_elem)
                            else:
                                if xml_item.find('./INIT-VALUE-REF') is not None:
                                    com_spec.init_value_ref = self.parse_text_node(xml_item.find('./INIT-VALUE-REF'))
                            if xml_item.find('./CAN-INVALIDATE') is not None:
                                com_spec.can_invalidate = True if self.parse_text_node(xml_item.find('./CAN-INVALIDATE')) == 'true' else False
                            port.com_spec.append(com_spec)
                        elif xml_item.tag == 'QUEUED-SENDER-COM-SPEC':
                            data_elem_name = _get_data_elem_name_from_com_spec(xml_item, port_interface_ref)
                            com_spec = DataElementComSpec(data_elem_name)
                            assert (com_spec is not None)
                            port.com_spec.append(com_spec)
                        elif xml_item.tag == 'PARAMETER-PROVIDE-COM-SPEC':
                            com_spec = self._parse_parameter_com_spec(xml_item, port_interface_ref)
                            if com_spec is not None:
                                port.com_spec.append(com_spec)
                        elif xml_item.tag == 'MODE-SWITCH-SENDER-COM-SPEC':
                            com_spec = self._parse_mode_switch_sender_com_spec(xml_item)
                            assert (com_spec is not None)
                            port.com_spec.append(com_spec)
                        elif xml_item.tag == 'NV-PROVIDE-COM-SPEC':
                            com_spec = self._parse_nv_provide_com_spec(xml_item, port_interface_ref)
                            if com_spec is not None:
                                port.com_spec.append(com_spec)
                        else:
                            self._logger.warning(f'Parser not implemented: {xml_item.tag}')
                component_type.provide_ports.append(port)

    def parse_composition_type(self, xml_root: Element, parent: ArObject | None = None) -> ComponentType:
        """
        parses COMPOSITION-TYPE
        """
        assert (xml_root.tag == 'COMPOSITION-TYPE') or (xml_root.tag == 'COMPOSITION-SW-COMPONENT-TYPE')
        data_type_mapping_refs = None
        swc = CompositionComponent(self.parse_text_node(xml_root.find('SHORT-NAME')), parent)
        self.push()
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'SHORT-NAME':
                continue
            elif xml_elem.tag == 'PORTS':
                self.parse_component_ports(swc, xml_root)
            elif xml_elem.tag == 'COMPONENTS':
                self.parse_components(xml_elem, swc)
            elif xml_elem.tag == 'CONNECTORS':
                if self.version >= 4.0:
                    self.parse_connectors_v4(xml_elem, swc)
                else:
                    self.parse_connectors_v3(xml_elem, swc)
            elif xml_elem.tag == 'DATA-TYPE-MAPPING-REFS':
                data_type_mapping_refs = []
                for xml_child in xml_elem.findall('./*'):
                    if xml_child.tag == 'DATA-TYPE-MAPPING-REF':
                        tmp = self.parse_text_node(xml_child)
                        assert (tmp is not None)
                        data_type_mapping_refs.append(tmp)
            elif xml_elem.tag == 'PORT-GROUPS':
                self._logger.warning(f'Unhandled: {xml_elem.tag}')
            else:
                self.default_handler(xml_elem)
        if data_type_mapping_refs is not None:
            swc.data_type_mapping_refs = data_type_mapping_refs
        self.pop(swc)
        return swc

    def parse_components(self, xml_root: Element, parent: CompositionComponent):
        """
        parses <COMPONENTS>
        """
        assert (xml_root.tag == 'COMPONENTS')
        for elem in xml_root.findall('./*'):
            component_tag = 'SW-COMPONENT-PROTOTYPE' if self.version >= 4.0 else 'COMPONENT-PROTOTYPE'
            if elem.tag != component_tag:
                self._logger.error(f'Unexpected tag: {elem.tag}')
                continue
            name = self.parse_text_node(elem.find('SHORT-NAME'))
            type_ref = self.parse_text_node(elem.find('TYPE-TREF'))
            parent.components.append(ComponentPrototype(name, type_ref, parent))

    def parse_connectors_v3(self, xml_root: Element, parent: CompositionComponent):
        """
        parses <CONNECTORS> (AUTOSAR 3)
        """
        assert (xml_root.tag == 'CONNECTORS')
        for elem in xml_root.findall('./*'):
            if elem.tag == 'ASSEMBLY-CONNECTOR-PROTOTYPE':
                name = self.parse_text_node(elem.find('SHORT-NAME'))
                provider_component_ref = self.parse_text_node(elem.find('./PROVIDER-IREF/COMPONENT-PROTOTYPE-REF'))
                provider_port_ref = self.parse_text_node(elem.find('./PROVIDER-IREF/P-PORT-PROTOTYPE-REF'))
                requester_component_ref = self.parse_text_node(elem.find('./REQUESTER-IREF/COMPONENT-PROTOTYPE-REF'))
                requester_port_ref = self.parse_text_node(elem.find('./REQUESTER-IREF/R-PORT-PROTOTYPE-REF'))
                parent.assembly_connectors.append(AssemblyConnector(
                    name,
                    ProviderInstanceRef(provider_component_ref, provider_port_ref),
                    RequesterInstanceRef(requester_component_ref, requester_port_ref),
                ))
            elif elem.tag == 'DELEGATION-CONNECTOR-PROTOTYPE':
                name = self.parse_text_node(elem.find('SHORT-NAME'))
                inner_component_ref = self.parse_text_node(elem.find('./INNER-PORT-IREF/COMPONENT-PROTOTYPE-REF'))
                inner_port_ref = self.parse_text_node(elem.find('./INNER-PORT-IREF/PORT-PROTOTYPE-REF'))
                outer_port_ref = self.parse_text_node(elem.find('./OUTER-PORT-REF'))
                parent.delegation_connectors.append(DelegationConnector(
                    name,
                    InnerPortInstanceRef(inner_component_ref, inner_port_ref),
                    OuterPortRef(outer_port_ref),
                ))
            else:
                self._logger.warning(f'Unexpected tag: {elem.tag}')

    def parse_connectors_v4(self, xml_root: Element, parent: CompositionComponent):
        """
        parses <CONNECTORS> (AUTOSAR 4)
        """
        assert (xml_root.tag == 'CONNECTORS')
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'ASSEMBLY-SW-CONNECTOR':
                name = self.parse_text_node(xml_elem.find('SHORT-NAME'))
                provider_component_ref = None
                provider_port_ref = None
                requester_component_ref = None
                requester_port_ref = None
                for xml_child in xml_elem.findall('./*'):
                    if xml_child.tag == 'SHORT-NAME':
                        continue
                    elif xml_child.tag == 'PROVIDER-IREF':
                        provider_component_ref = self.parse_text_node(xml_child.find('./CONTEXT-COMPONENT-REF'))
                        provider_port_ref = self.parse_text_node(xml_child.find('./TARGET-P-PORT-REF'))
                    elif xml_child.tag == 'REQUESTER-IREF':
                        requester_component_ref = self.parse_text_node(xml_child.find('./CONTEXT-COMPONENT-REF'))
                        requester_port_ref = self.parse_text_node(xml_child.find('./TARGET-R-PORT-REF'))
                    else:
                        self._logger.warning(f'Unexpected tag: {xml_child.tag}')
                        continue
                if provider_component_ref is None:
                    self._logger.error(f'PROVIDER-IREF/CONTEXT-COMPONENT-REF is missing: item={name}' % name)
                    return
                if provider_port_ref is None:
                    self._logger.error(f'PROVIDER-IREF/TARGET-P-PORT-REF is missing: item={name}' % name)
                    return
                if requester_component_ref is None:
                    self._logger.error(f'REQUESTER-IREF/CONTEXT-COMPONENT-REF is missing: item={name}' % name)
                    return
                if requester_port_ref is None:
                    self._logger.error(f'REQUESTER-IREF/TARGET-R-PORT-REF is missing: item={name}' % name)
                    return
                parent.assembly_connectors.append(AssemblyConnector(
                    name,
                    ProviderInstanceRef(provider_component_ref, provider_port_ref),
                    RequesterInstanceRef(requester_component_ref, requester_port_ref),
                ))
            elif xml_elem.tag == 'DELEGATION-SW-CONNECTOR':
                name = self.parse_text_node(xml_elem.find('SHORT-NAME'))
                inner_component_ref = None
                inner_port_ref = None
                for xml_child in xml_elem.findall('./INNER-PORT-IREF/*'):
                    if xml_child.tag == 'R-PORT-IN-COMPOSITION-INSTANCE-REF':
                        inner_component_ref = self.parse_text_node(xml_child.find('./CONTEXT-COMPONENT-REF'))
                        inner_port_ref = self.parse_text_node(xml_child.find('./TARGET-R-PORT-REF'))
                    elif xml_child.tag == 'P-PORT-IN-COMPOSITION-INSTANCE-REF':
                        inner_component_ref = self.parse_text_node(xml_child.find('./CONTEXT-COMPONENT-REF'))
                        inner_port_ref = self.parse_text_node(xml_child.find('./TARGET-P-PORT-REF'))
                    else:
                        self._logger.error(f'Unexpected tag: {xml_child.tag}')
                        continue
                if inner_component_ref is None:
                    self._logger.error(f'R-PORT-IN-COMPOSITION-INSTANCE-REF/CONTEXT-COMPONENT-REF is missing: item={name}' % name)
                    return
                if inner_port_ref is None:
                    self._logger.error(f'R-PORT-IN-COMPOSITION-INSTANCE-REF/TARGET-R-PORT-REF is missing: item={name}' % name)
                    return
                outer_port_ref = self.parse_text_node(xml_elem.find('./OUTER-PORT-REF'))
                parent.delegation_connectors.append(DelegationConnector(
                    name,
                    InnerPortInstanceRef(inner_component_ref, inner_port_ref),
                    OuterPortRef(outer_port_ref),
                ))
            else:
                self._logger.warning(f'Unexpected tag: {xml_elem.tag}')

    def _parse_mode_switch_receiver_com_spec(self, xml_root: Element) -> ModeSwitchComSpec:
        enhanced_mode = None
        support_async = None
        mode_group_ref = None
        assert (xml_root.tag == 'MODE-SWITCH-RECEIVER-COM-SPEC')
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'ENHANCED-MODE-API':
                enhanced_mode = self.parse_boolean_node(xml_elem)
            elif xml_elem.tag == 'SUPPORTS-ASYNCHRONOUS-MODE-SWITCH':
                support_async = self.parse_boolean_node(xml_elem)
            elif xml_elem.tag == 'MODE-GROUP-REF':
                mode_group_ref = self.parse_text_node(xml_elem)
            else:
                self._logger.warning(f'Unexpected tag: {xml_elem.tag}')
        return ModeSwitchComSpec(None, enhanced_mode, support_async, mode_group_ref=mode_group_ref)

    def _parse_mode_switch_sender_com_spec(self, xml_root: Element) -> ModeSwitchComSpec:
        enhanced_mode = None
        queue_length = None
        mode_switch_ack_timeout = None
        mode_group_ref = None
        assert (xml_root.tag == 'MODE-SWITCH-SENDER-COM-SPEC')
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'ENHANCED-MODE-API':
                enhanced_mode = self.parse_boolean_node(xml_elem)
            elif xml_elem.tag == 'MODE-GROUP-REF':
                mode_group_ref = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'MODE-SWITCHED-ACK':
                for xml_child in xml_elem.findall('./*'):
                    if xml_child.tag == 'TIMEOUT':
                        tmp = self.parse_float_node(xml_child)
                        if tmp is not None:
                            mode_switch_ack_timeout = int(tmp * 1000)  # We use milliseconds in our internal model
            elif xml_elem.tag == 'QUEUE-LENGTH':
                queue_length = self.parse_int_node(xml_elem)
            else:
                self._logger.warning(f'Unexpected tag: {xml_elem.tag}')
        return ModeSwitchComSpec(None, enhanced_mode, None, queue_length, mode_switch_ack_timeout, mode_group_ref)

    def _parse_parameter_com_spec(self, xml_root: Element, port_interface_ref: str) -> ParameterComSpec | None:
        init_value = None
        name = None
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'INIT-VALUE':
                init_value, init_value_ref = self._parse_ar4_init_value(xml_elem)
                if init_value_ref is not None:
                    raise NotImplementedError('CONSTANT-REFERENCE')
            elif xml_elem.tag == 'PARAMETER-REF':
                name = _get_parameter_name_from_com_spec(xml_elem, port_interface_ref)
            else:
                raise NotImplementedError(xml_elem.tag)
        if name is None:
            self._logger.error('PARAMETER-REQUIRE-COM-SPEC must have a PARAMETER-REF')
            return None
        return ParameterComSpec(name, init_value)

    def _parse_nv_provide_com_spec(self, xml_root: Element, port_interface_ref: str) -> NvProvideComSpec | None:
        rom_block_init_value = None
        rom_block_init_value_ref = None
        ram_block_init_value = None
        ram_block_init_value_ref = None
        name = None
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'RAM-BLOCK-INIT-VALUE':
                ram_block_init_value, ram_block_init_value_ref = self._parse_ar4_init_value(xml_elem)
            elif xml_elem.tag == 'ROM-BLOCK-INIT-VALUE':
                rom_block_init_value, rom_block_init_value_ref = self._parse_ar4_init_value(xml_elem)
            elif xml_elem.tag == 'VARIABLE-REF':
                name = _get_variable_name_from_com_spec(xml_elem, port_interface_ref)
            else:
                self._logger.warning(f'Unexpected tag: {xml_elem.tag}')
        if name is None:
            self._logger.error('NV-PROVIDE-COM-SPEC must have a VARIABLE-REF')
            return None
        return NvProvideComSpec(
            name,
            ram_block_init_value=ram_block_init_value,
            ram_block_init_value_ref=ram_block_init_value_ref,
            rom_block_init_value=rom_block_init_value,
            rom_block_init_value_ref=rom_block_init_value_ref,
        )

    def _parse_nv_require_com_spec(self, xml_root: Element, port_interface_ref: str) -> NvRequireComSpec | None:
        init_value = None
        init_value_ref = None
        name = None
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'INIT-VALUE':
                init_value, init_value_ref = self._parse_ar4_init_value(xml_elem)
            elif xml_elem.tag == 'VARIABLE-REF':
                name = _get_variable_name_from_com_spec(xml_elem, port_interface_ref)
            else:
                self._logger.warning(f'Unexpected tag: {xml_elem.tag}')
        if name is None:
            self._logger.error('NV-PROVIDE-COM-SPEC must have a VARIABLE-REF')
        return NvRequireComSpec(
            name,
            init_value=init_value,
            init_value_ref=init_value_ref,
        )

    def _parse_ar4_init_value(self, xml_elem: Element) -> tuple[ValueAR4 | None, str | None]:
        init_value = None
        init_value_ref = None
        for xml_child in xml_elem.findall('./*'):
            if xml_child.tag == 'CONSTANT-REFERENCE':
                init_value_ref = self.parse_text_node(xml_child.find('./CONSTANT-REF'))
            else:
                values = self.constant_parser.parse_value_v4(xml_elem, None)
                if len(values) != 1:
                    self._logger.error(f'{xml_elem.tag} cannot cannot contain multiple elements')
                    continue
                init_value = values[0]
        return init_value, init_value_ref
