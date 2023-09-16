from xml.etree.ElementTree import Element

from autosar.ar_object import ArObject
from autosar.behavior import (
    InternalBehavior,
    PortAPIOption,
    PerInstanceMemory,
    ExclusiveArea,
    SwcInternalBehavior,
    RunnableEntity,
    DataReceivePoint,
    DataSendPoint,
    ModeAccessPoint,
    LocalParameterRef,
    RequireModeGroupInstanceRef,
    ProvideModeGroupInstanceRef,
    ModeInstanceRef,
    ParameterInstanceRef,
    ModeDependency,
    ModeDependencyRef,
    DisabledModeInstanceRef,
    InitEvent,
    ModeSwitchEvent,
    ModeSwitchAckEvent,
    TimingEvent,
    DataReceivedEvent,
    OperationInvokedEvent,
    DataInstanceRef,
    OperationInstanceRef,
    DataElementInstanceRef,
    SwcNvBlockNeeds,
    RoleBasedRPortAssignment,
    CalPrmElemPrototype,
    SyncServerCallPoint,
    VariableAccess,
    SwcServiceDependency,
    ParameterDataPrototype,
    ServiceNeeds,
    NvmBlockConfig,
    NvmBlockNeeds,
    RoleBasedDataAssignment,
    RoleBasedPortAssignment,
    NvBlockDescriptor,
    NvBlockDataMapping,
    NvRamBlockElement,
    ReadNvData,
    WrittenNvData,
    WrittenReadNvData,
    NvBlockRamBlock,
    NvBlockRomBlock,
    ModeSwitchPoint,
    ParameterAccessPoint,
)
from autosar.element import Element as ArElement
from autosar.parser.constant_parser import ConstantParser
from autosar.parser.parser_base import ElementParser


class BehaviorParser(ElementParser):
    def __init__(self, version: float = 3.0):
        super().__init__(version)
        self.constant_parser = ConstantParser(version)

    def get_supported_tags(self):
        if 3.0 <= self.version < 4.0:
            return ['INTERNAL-BEHAVIOR']
        elif self.version >= 4.0:
            return ['SWC-INTERNAL-BEHAVIOR']
        else:
            return []

    def parse_element(self, xml_element: Element, parent: ArObject | None = None) -> InternalBehavior | SwcInternalBehavior | None:
        if 3.0 <= self.version < 4.0 and xml_element.tag == 'INTERNAL-BEHAVIOR':
            return self.parse_internal_behavior(xml_element, parent)
        elif self.version >= 4.0 and xml_element.tag == 'SWC-INTERNAL-BEHAVIOR':
            return self.parse_swc_internal_behavior(xml_element, parent)
        return None

    def parse_internal_behavior(self, xml_root: Element, parent: ArObject) -> InternalBehavior | None:
        """AUTOSAR 3 Internal Behavior"""
        assert (xml_root.tag == 'INTERNAL-BEHAVIOR')
        name = self.parse_text_node(xml_root.find('SHORT-NAME'))
        component_ref = self.parse_text_node(xml_root.find('COMPONENT-REF'))
        multiple_instance = False
        xml_support_multiple_inst = xml_root.find('SUPPORTS-MULTIPLE-INSTANTIATION')
        if (xml_support_multiple_inst is not None) and (xml_support_multiple_inst.text == 'true'):
            multiple_instance = True
        ws = parent.root_ws()
        assert (ws is not None)
        if (name is not None) and (component_ref is not None):
            internal_behavior = InternalBehavior(name, component_ref, multiple_instance, parent)
            swc = ws.find(component_ref)
            if swc is not None:
                swc.behavior = internal_behavior
            for xml_node in xml_root.findall('./*'):
                if (xml_node.tag == 'SHORT-NAME') or (xml_node.tag == 'COMPONENT-REF') or (xml_node.tag == 'SUPPORTS-MULTIPLE-INSTANTIATION'):
                    continue
                if xml_node.tag == 'EVENTS':
                    for xml_event in xml_node.findall('./*'):
                        if xml_event.tag == 'MODE-SWITCH-EVENT':
                            event = self.parse_mode_switch_event(xml_event, internal_behavior)
                        elif xml_event.tag == 'TIMING-EVENT':
                            event = self.parse_timing_event(xml_event, internal_behavior)
                        elif xml_event.tag == 'DATA-RECEIVED-EVENT':
                            event = self.parse_data_received_event(xml_event, internal_behavior)
                        elif xml_event.tag == 'OPERATION-INVOKED-EVENT':
                            event = self.parse_operation_invoked_event(xml_event, internal_behavior)
                        else:
                            self._logger.warning(f'Unexpected tag: {xml_event.tag}')
                            continue
                        if event is None:
                            self._logger.error('Event is None')
                            continue
                        internal_behavior.events.append(event)
                elif xml_node.tag == 'PORT-API-OPTIONS':
                    for xml_option in xml_node.findall('./PORT-API-OPTION'):
                        port_api_option = PortAPIOption(
                            self.parse_text_node(xml_option.find('PORT-REF')),
                            self.parse_boolean_node(xml_option.find('ENABLE-TAKE-ADDRESS')),
                            self.parse_boolean_node(xml_option.find('INDIRECT-API')),
                        )
                        if port_api_option is not None:
                            internal_behavior.port_api_options.append(port_api_option)
                elif xml_node.tag == 'RUNNABLES':
                    for xm_runnable in xml_node.findall('./RUNNABLE-ENTITY'):
                        runnable_entity = self.parse_runnable_entity(xm_runnable, internal_behavior)
                        if runnable_entity is not None:
                            internal_behavior.runnables.append(runnable_entity)
                elif xml_node.tag == 'PER-INSTANCE-MEMORYS':
                    for xml_elem in xml_node.findall('./PER-INSTANCE-MEMORY'):
                        per_instance_memory = PerInstanceMemory(
                            self.parse_text_node(xml_elem.find('SHORT-NAME')),
                            self.parse_text_node(xml_elem.find('TYPE-DEFINITION')),
                            internal_behavior,
                        )
                        internal_behavior.per_instance_memories.append(per_instance_memory)
                elif xml_node.tag == 'SERVICE-NEEDSS':
                    for xml_elem in xml_node.findall('./*'):
                        if xml_elem.tag != 'SWC-NV-BLOCK-NEEDS':
                            self._logger.error(f'Unexpected tag: {xml_elem.tag}')
                            continue
                        swc_nv_block_needs = self.parse_swc_nv_block_needs(xml_elem)
                        if swc_nv_block_needs is not None:
                            internal_behavior.swc_nv_block_needs.append(swc_nv_block_needs)
                elif xml_node.tag == 'SHARED-CALPRMS':
                    for xml_elem in xml_node.findall('./*'):
                        if xml_elem.tag != 'CALPRM-ELEMENT-PROTOTYPE':
                            self._logger.error(f'Unexpected tag: {xml_elem.tag}')
                            continue
                        cal_prm_elem_prototype = self.parse_cal_prm_elem_prototype(xml_elem, internal_behavior)
                        assert (cal_prm_elem_prototype is not None)
                        internal_behavior.shared_cal_params.append(cal_prm_elem_prototype)
                elif xml_node.tag == 'EXCLUSIVE-AREAS':
                    for xml_elem in xml_node.findall('./*'):
                        if xml_elem.tag != 'EXCLUSIVE-AREA':
                            self._logger.error(f'Unexpected tag: {xml_elem.tag}')
                            continue
                        exclusive_area = ExclusiveArea(self.parse_text_node(xml_elem.find('SHORT-NAME')), internal_behavior)
                        internal_behavior.exclusive_areas.append(exclusive_area)
                else:
                    self._logger.warning(f'Unexpected tag: {xml_node.tag}')
            return internal_behavior

    def parse_swc_internal_behavior(self, xml_root: Element, parent: ArObject) -> SwcInternalBehavior | None:
        """AUTOSAR 4 internal behavior"""
        assert (xml_root.tag == 'SWC-INTERNAL-BEHAVIOR')
        name = self.parse_text_node(xml_root.find('SHORT-NAME'))
        multiple_instance = False
        xml_support_multiple_inst = xml_root.find('SUPPORTS-MULTIPLE-INSTANTIATION')
        if xml_support_multiple_inst is not None:
            multiple_instance = self.parse_boolean_node(xml_support_multiple_inst)
            assert (multiple_instance is not None)
        ws = parent.root_ws()
        assert (ws is not None)
        if name is None:
            return None
        handled_xml = ['SHORT-NAME', 'SUPPORTS-MULTIPLE-INSTANTIATION']
        internal_behavior = SwcInternalBehavior(name, parent.ref, multiple_instance, parent)
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag in handled_xml:
                continue
            elif xml_elem.tag == 'DATA-TYPE-MAPPING-REFS':
                for xml_child in xml_elem.findall('./*'):
                    if xml_child.tag == 'DATA-TYPE-MAPPING-REF':
                        tmp = self.parse_text_node(xml_child)
                        assert (tmp is not None)
                        internal_behavior.append_data_type_mapping_ref(tmp)
            elif xml_elem.tag == 'EVENTS':
                for xml_event in xml_elem.findall('./*'):
                    if xml_event.tag == 'INIT-EVENT':
                        event = self.parse_init_event(xml_event, internal_behavior)
                    elif xml_event.tag == 'SWC-MODE-SWITCH-EVENT':
                        event = self.parse_mode_switch_event(xml_event, internal_behavior)
                    elif xml_event.tag == 'TIMING-EVENT':
                        event = self.parse_timing_event(xml_event, internal_behavior)
                    elif xml_event.tag == 'DATA-RECEIVED-EVENT':
                        event = self.parse_data_received_event(xml_event, internal_behavior)
                    elif xml_event.tag == 'OPERATION-INVOKED-EVENT':
                        event = self.parse_operation_invoked_event(xml_event, internal_behavior)
                    elif xml_event.tag == 'MODE-SWITCHED-ACK-EVENT':
                        event = self.parse_mode_switched_ack_event(xml_event, internal_behavior)
                    elif xml_event.tag == 'DATA-RECEIVE-ERROR-EVENT':
                        # TODO: Implement later
                        event = None
                    else:
                        self._logger.warning(f'Unexpected tag: {xml_event.tag}')
                        continue
                    if event is None:
                        self._logger.error('Event is None')
                        continue
                    internal_behavior.events.append(event)
            elif xml_elem.tag == 'PORT-API-OPTIONS':
                for xml_option in xml_elem.findall('./PORT-API-OPTION'):
                    port_api_option = PortAPIOption(
                        self.parse_text_node(xml_option.find('PORT-REF')),
                        self.parse_boolean_node(xml_option.find('ENABLE-TAKE-ADDRESS')),
                        self.parse_boolean_node(xml_option.find('INDIRECT-API')),
                    )
                    if port_api_option is not None:
                        internal_behavior.port_api_options.append(port_api_option)
            elif xml_elem.tag == 'RUNNABLES':
                for xm_runnable in xml_elem.findall('./RUNNABLE-ENTITY'):
                    runnable_entity = self.parse_runnable_entity(xm_runnable, internal_behavior)
                    if runnable_entity is not None:
                        internal_behavior.runnables.append(runnable_entity)
            elif xml_elem.tag == 'AR-TYPED-PER-INSTANCE-MEMORYS':
                for xml_child in xml_elem.findall('./*'):
                    if xml_child.tag != 'VARIABLE-DATA-PROTOTYPE':
                        self._logger.error(f'Unexpected tag: {xml_child.tag}')
                        continue
                    data_element = self.parse_variable_data_prototype(xml_child, internal_behavior)
                    # noinspection PyTypeChecker
                    internal_behavior.per_instance_memories.append(data_element)
            elif xml_elem.tag == 'SERVICE-DEPENDENCYS':
                for xml_child_elem in xml_elem.findall('./*'):
                    if xml_child_elem.tag != 'SWC-SERVICE-DEPENDENCY':
                        self._logger.error(f'Unexpected tag: {xml_child_elem.tag}')
                        continue
                    swc_service_dependency = self.parse_swc_service_dependency(xml_child_elem, internal_behavior)
                    internal_behavior.service_dependencies.append(swc_service_dependency)
            elif xml_elem.tag == 'SHARED-PARAMETERS':
                for xml_child_elem in xml_elem.findall('./*'):
                    if xml_child_elem.tag == 'PARAMETER-DATA-PROTOTYPE':
                        self._logger.error(f'Unexpected tag: {xml_child_elem.tag}')
                        continue
                    tmp = self.parse_parameter_data_prototype(xml_child_elem, internal_behavior)
                    if tmp is not None:
                        internal_behavior.parameter_data_prototype.append(tmp)
            elif xml_elem.tag == 'EXCLUSIVE-AREAS':
                for xml_child in xml_elem.findall('./*'):
                    if xml_child.tag != 'EXCLUSIVE-AREA':
                        self._logger.error(f'Unexpected tag: {xml_elem.tag}')
                        continue
                    exclusive_area = ExclusiveArea(self.parse_text_node(xml_child.find('SHORT-NAME')), internal_behavior)
                    internal_behavior.exclusive_areas.append(exclusive_area)
            elif xml_elem.tag == 'PER-INSTANCE-PARAMETERS':
                pass  # implement later
            elif xml_elem.tag == 'EXPLICIT-INTER-RUNNABLE-VARIABLES':
                pass  # implement later
            elif xml_elem.tag == 'HANDLE-TERMINATION-AND-RESTART':
                pass  # implement later
            elif xml_elem.tag == 'STATIC-MEMORYS':
                pass  # implement later
            else:
                self._logger.warning(f'Unexpected tag: {xml_elem.tag}')
        return internal_behavior

    def parse_runnable_entity(self, xml_root: Element, parent: ArElement) -> RunnableEntity | None:
        name = None
        symbol = None
        xml_data_receive_points = None
        xml_data_send_points = None
        xml_server_call_points = None
        xml_can_enter_exclusive_areas = None
        admin_data = None
        xml_mode_access_points = None
        xml_parameter_access_points = None
        can_be_invoked_concurrently = False
        xml_mode_switch_points = None
        min_start_interval = None
        if self.version < 4.0:
            for xml_elem in xml_root.findall('*'):
                if xml_elem.tag == 'SHORT-NAME':
                    name = self.parse_text_node(xml_elem)
                elif xml_elem.tag == 'CAN-BE-INVOKED-CONCURRENTLY':
                    can_be_invoked_concurrently = self.parse_boolean_node(xml_elem)
                elif xml_elem.tag == 'DATA-RECEIVE-POINTS':
                    xml_data_receive_points = xml_elem
                elif xml_elem.tag == 'DATA-SEND-POINTS':
                    xml_data_send_points = xml_elem
                elif xml_elem.tag == 'SERVER-CALL-POINTS':
                    xml_server_call_points = xml_elem
                elif xml_elem.tag == 'SYMBOL':
                    symbol = self.parse_text_node(xml_elem)
                elif xml_elem.tag == 'CAN-ENTER-EXCLUSIVE-AREA-REFS':
                    xml_can_enter_exclusive_areas = xml_elem
                elif xml_elem.tag == 'ADMIN-DATA':
                    admin_data = self.parse_admin_data_node(xml_elem)
                else:
                    self._logger.warning(f'Unexpected tag: {xml_elem.tag}')
        else:
            for xml_elem in xml_root.findall('*'):
                if xml_elem.tag == 'SHORT-NAME':
                    name = self.parse_text_node(xml_elem)
                elif xml_elem.tag == 'CAN-BE-INVOKED-CONCURRENTLY':
                    can_be_invoked_concurrently = self.parse_boolean_node(xml_elem)
                elif xml_elem.tag == 'MODE-ACCESS-POINTS':
                    xml_mode_access_points = xml_elem
                elif xml_elem.tag == 'DATA-RECEIVE-POINT-BY-ARGUMENTS':
                    xml_data_receive_points = xml_elem
                elif xml_elem.tag == 'DATA-SEND-POINTS':
                    xml_data_send_points = xml_elem
                elif xml_elem.tag == 'SERVER-CALL-POINTS':
                    xml_server_call_points = xml_elem
                elif xml_elem.tag == 'SYMBOL':
                    symbol = self.parse_text_node(xml_elem)
                elif xml_elem.tag == 'CAN-ENTER-EXCLUSIVE-AREA-REFS':
                    xml_can_enter_exclusive_areas = xml_elem
                elif xml_elem.tag == 'MINIMUM-START-INTERVAL':
                    min_start_interval = self.parse_number_node(xml_elem)
                elif xml_elem.tag == 'ADMIN-DATA':
                    admin_data = self.parse_admin_data_node(xml_elem)
                elif xml_elem.tag == 'PARAMETER-ACCESSS':
                    xml_parameter_access_points = xml_elem
                elif xml_elem.tag == 'MODE-SWITCH-POINTS':
                    xml_mode_switch_points = xml_elem
                elif xml_elem.tag == 'READ-LOCAL-VARIABLES':
                    pass  # implement later
                elif xml_elem.tag == 'WRITTEN-LOCAL-VARIABLES':
                    pass  # implement later
                elif xml_elem.tag == 'DATA-READ-ACCESSS':
                    pass  # implement later
                elif xml_elem.tag == 'DATA-WRITE-ACCESSS':
                    pass  # implement later
                elif xml_elem.tag == 'RUNS-INSIDE-EXCLUSIVE-AREA-REFS':
                    pass  # implement later
                else:
                    self._logger.warning(f'Unexpected tag: {xml_elem.tag}')
        if name is None:
            return None
        runnable_entity = RunnableEntity(name, can_be_invoked_concurrently, symbol, parent)
        if min_start_interval is not None:
            runnable_entity.min_start_interval = float(1000 * min_start_interval)
        if xml_data_receive_points is not None:
            if self.version < 4.0:
                for xml_data_point in xml_data_receive_points.findall('./DATA-RECEIVE-POINT'):
                    name = self.parse_text_node(xml_data_point.find('SHORT-NAME'))
                    data_element_instance_ref = self.parse_data_element_instance_ref(
                        xml_data_point.find('DATA-ELEMENT-IREF'),
                        'R-PORT-PROTOTYPE-REF',
                    )
                    if data_element_instance_ref is not None:
                        data_receive_point = DataReceivePoint(
                            data_element_instance_ref.port_ref,
                            data_element_instance_ref.data_elem_ref,
                            name,
                        )
                        runnable_entity.append(data_receive_point)
            else:
                for xml_variable_access in xml_data_receive_points.findall('VARIABLE-ACCESS'):
                    name = self.parse_text_node(xml_variable_access.find('SHORT-NAME'))
                    accessed_variable = self.parse_accessed_variable(xml_variable_access.find('./ACCESSED-VARIABLE'))
                    assert (accessed_variable is not None)
                    data_receive_point = DataReceivePoint(
                        accessed_variable.port_prototype_ref,
                        accessed_variable.target_data_prototype_ref,
                        name,
                    )
                    runnable_entity.append(data_receive_point)
        if xml_data_send_points is not None:
            if self.version < 4.0:
                for xml_data_point in xml_data_send_points.findall('./DATA-SEND-POINT'):
                    name = self.parse_text_node(xml_data_point.find('SHORT-NAME'))
                    data_element_instance_ref = self.parse_data_element_instance_ref(
                        xml_data_point.find('DATA-ELEMENT-IREF'),
                        'P-PORT-PROTOTYPE-REF',
                    )
                    if data_element_instance_ref is not None:
                        data_send_point = DataSendPoint(
                            data_element_instance_ref.port_ref,
                            data_element_instance_ref.data_elem_ref,
                            name,
                        )
                        runnable_entity.append(data_send_point)
            else:
                for xml_variable_access in xml_data_send_points.findall('VARIABLE-ACCESS'):
                    name = self.parse_text_node(xml_variable_access.find('SHORT-NAME'))
                    accessed_variable = self.parse_accessed_variable(xml_variable_access.find('./ACCESSED-VARIABLE'))
                    assert (accessed_variable is not None)
                    data_send_point = DataSendPoint(
                        accessed_variable.port_prototype_ref,
                        accessed_variable.target_data_prototype_ref,
                        name,
                    )
                    runnable_entity.append(data_send_point)
        if xml_mode_access_points is not None:
            for xml_elem in xml_mode_access_points.findall('./*'):
                if xml_elem.tag != 'MODE-ACCESS-POINT':
                    self._logger.error(f'Unexpected tag: {xml_elem.tag}')
                    continue
                mode_access_point = self.parse_mode_access_point(xml_elem)
                assert (mode_access_point is not None)
                runnable_entity.mode_access_points.append(mode_access_point)
        if xml_server_call_points is not None:
            for xml_server_call_point in xml_server_call_points.findall('./SYNCHRONOUS-SERVER-CALL-POINT'):
                sync_server_call_point = self.parse_sync_server_call_point(xml_server_call_point)
                if sync_server_call_point is not None:
                    runnable_entity.server_call_points.append(sync_server_call_point)
        if xml_can_enter_exclusive_areas is not None:
            for xml_can_enter_exclusive_area_ref in xml_can_enter_exclusive_areas.findall('./CAN-ENTER-EXCLUSIVE-AREA-REF'):
                runnable_entity.exclusive_area_refs.append(self.parse_text_node(xml_can_enter_exclusive_area_ref))
        if self.version >= 4.0 and xml_parameter_access_points is not None:
            for xml_child in xml_parameter_access_points.findall('./*'):
                if xml_child.tag != 'PARAMETER-ACCESS':
                    self._logger.error(f'Unexpected tag: {xml_child.tag}')
                    continue
                tmp = self.parse_parameter_access_point(xml_child, runnable_entity)
                if tmp is not None:
                    runnable_entity.parameter_access_points.append(tmp)
        if xml_mode_switch_points is not None:
            for xml_elem in xml_mode_switch_points.findall('./*'):
                if xml_elem.tag != 'MODE-SWITCH-POINT':
                    self._logger.error(f'Unexpected tag: {xml_elem.tag}')
                    continue
                mode_switch_point = self._parse_mode_switch_point(xml_elem)
                if mode_switch_point is not None:
                    runnable_entity.mode_switch_points.append(mode_switch_point)
        if runnable_entity is not None:
            runnable_entity.admin_data = admin_data
        return runnable_entity

    def parse_mode_access_point(self, xml_root: Element) -> ModeAccessPoint:
        assert (xml_root.tag == 'MODE-ACCESS-POINT')
        name = None
        mode_group_instance_ref = None
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'SHORT-NAME':
                name = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'MODE-GROUP-IREF':
                for child_elem in xml_elem.findall('./*'):
                    if child_elem.tag == 'R-MODE-GROUP-IN-ATOMIC-SWC-INSTANCE-REF':
                        if mode_group_instance_ref is not None:
                            self._logger.error('Multiple instances of R-MODE-GROUP-IN-ATOMIC-SWC-INSTANCE-REF not implemented')
                            continue
                        mode_group_instance_ref = self._parse_require_mode_group_instance_ref(child_elem)
                    elif child_elem.tag == 'P-MODE-GROUP-IN-ATOMIC-SWC-INSTANCE-REF':
                        if mode_group_instance_ref is not None:
                            self._logger.error('Multiple instances of P-MODE-GROUP-IN-ATOMIC-SWC-INSTANCE-REF not implemented')
                        mode_group_instance_ref = self._parse_provide_mode_group_instance_ref(child_elem)
                    else:
                        self._logger.warning(f'Unexpected tag: {child_elem.tag}')
            else:
                self._logger.warning(f'Unexpected tag: {xml_elem.tag}')
        return ModeAccessPoint(name, mode_group_instance_ref)

    def _parse_mode_switch_point(self, xml_root: Element) -> ModeSwitchPoint | None:
        assert (xml_root.tag == 'MODE-SWITCH-POINT')
        name = None
        mode_group_instance_ref = None
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'SHORT-NAME':
                name = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'MODE-GROUP-IREF':
                mode_group_instance_ref = self._parse_provide_mode_group_instance_ref(xml_elem)
            else:
                self._logger.warning(f'Unexpected tag: {xml_elem.tag}')
        if name is None:
            return None
        return ModeSwitchPoint(name, mode_group_instance_ref)

    def parse_parameter_access_point(self, xml_root, parent: ArObject | None = None) -> ParameterAccessPoint | None:
        assert (xml_root.tag == 'PARAMETER-ACCESS')
        (name, accessed_parameter) = (None, None)
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'SHORT-NAME':
                name = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'ACCESSED-PARAMETER':
                for xml_child in xml_elem.findall('./*'):
                    if xml_child.tag == 'AUTOSAR-PARAMETER-IREF':
                        accessed_parameter = self.parse_parameter_instance_ref(xml_child)
                    elif xml_child.tag == 'LOCAL-PARAMETER-REF':
                        accessed_parameter = LocalParameterRef(self.parse_text_node(xml_child))
                    else:
                        self._logger.warning(f'Unexpected tag: {xml_child.tag}')
            else:
                raise NotImplementedError(xml_elem.tag)
        if name is None or accessed_parameter is None:
            return None
        return ParameterAccessPoint(name, accessed_parameter, parent)

    def _parse_require_mode_group_instance_ref(self, xml_root: Element) -> RequireModeGroupInstanceRef | None:
        """parses <R-MODE-GROUP-IN-ATOMIC-SWC-INSTANCE-REF>"""
        assert (xml_root.tag == 'R-MODE-GROUP-IN-ATOMIC-SWC-INSTANCE-REF')
        require_port_ref = None
        mode_group_ref = None
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'CONTEXT-R-PORT-REF':
                require_port_ref = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'TARGET-MODE-GROUP-REF':
                mode_group_ref = self.parse_text_node(xml_elem)
            else:
                self._logger.warning(f'Unexpected tag: {xml_elem.tag}')
        if require_port_ref is None:
            self._logger.error('CONTEXT-R-PORT-REF not set')
            return None
        if mode_group_ref is None:
            self._logger.error('TARGET-MODE-GROUP-REF not set')
            return None
        return RequireModeGroupInstanceRef(require_port_ref, mode_group_ref)

    def _parse_provide_mode_group_instance_ref(self, xml_root: Element) -> ProvideModeGroupInstanceRef | None:
        """parses <P-MODE-GROUP-IN-ATOMIC-SWC-INSTANCE-REF>"""
        # This XML item exists multiple times (at least 4 different places) in the AUTOSAR 4 XSD using different XML tag.
        assert (xml_root.tag in ['P-MODE-GROUP-IN-ATOMIC-SWC-INSTANCE-REF', 'MODE-GROUP-IREF'])
        provide_port_ref = None
        mode_group_ref = None
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'CONTEXT-P-PORT-REF':
                provide_port_ref = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'TARGET-MODE-GROUP-REF':
                mode_group_ref = self.parse_text_node(xml_elem)
            else:
                self._logger.warning(f'Unexpected tag: {xml_elem.tag}')
        if provide_port_ref is None:
            self._logger.error('CONTEXT-P-PORT-REF not set')
            return None
        if mode_group_ref is None:
            self._logger.error('TARGET-MODE-GROUP-REF not set')
            return None
        return ProvideModeGroupInstanceRef(provide_port_ref, mode_group_ref)

    def parse_mode_instance_ref(self, xml_root: Element) -> ModeInstanceRef | None:
        """parses <MODE-IREF>"""
        assert (xml_root.tag == 'MODE-IREF')
        if self.version < 4.0:
            mode_declaration_ref = self.parse_text_node(xml_root.find('MODE-DECLARATION-REF'))
            mode_declaration_group_prototype_ref = self.parse_text_node(xml_root.find('MODE-DECLARATION-GROUP-PROTOTYPE-REF'))
            require_port_prototype_ref = self.parse_text_node(xml_root.find('R-PORT-PROTOTYPE-REF'))
        elif self.version >= 4.0:
            mode_declaration_ref = self.parse_text_node(xml_root.find('TARGET-MODE-DECLARATION-REF'))
            mode_declaration_group_prototype_ref = self.parse_text_node(xml_root.find('CONTEXT-MODE-DECLARATION-GROUP-PROTOTYPE-REF'))
            require_port_prototype_ref = self.parse_text_node(xml_root.find('CONTEXT-PORT-REF'))
        else:
            self._logger.error(f'Unsupported version: {self.version}')
            return None
        return ModeInstanceRef(mode_declaration_ref, mode_declaration_group_prototype_ref, require_port_prototype_ref)

    def parse_parameter_instance_ref(self, xml_root: Element) -> ParameterInstanceRef:
        """parses <AUTOSAR-PARAMETER-IREF>"""
        assert (xml_root.tag == 'AUTOSAR-PARAMETER-IREF')
        port_ref = self.parse_text_node(xml_root.find('PORT-PROTOTYPE-REF'))
        parameter_data_ref = self.parse_text_node(xml_root.find('TARGET-DATA-PROTOTYPE-REF'))
        return ParameterInstanceRef(port_ref, parameter_data_ref)

    def _parse_mode_dependency(self, xml_root, *_) -> ModeDependency:
        """parses <MODE-DEPENDENCY>"""
        assert (xml_root.tag == 'MODE-DEPENDENCY')
        mode_dependency = ModeDependency()
        if xml_root.find('DEPENDENT-ON-MODE-IREFS') is not None:
            for xml_node in xml_root.findall('./DEPENDENT-ON-MODE-IREFS/DEPENDENT-ON-MODE-IREF'):
                mode_instance_ref = self._parse_dependent_on_mode_instance_ref(xml_node)
                if mode_instance_ref is not None:
                    mode_dependency.mode_instance_refs.append(mode_instance_ref)
        return mode_dependency

    def _parse_dependent_on_mode_instance_ref(self, xml_root: Element, *_) -> ModeDependencyRef:
        """parses <DEPENDENT-ON-MODE-IREF>"""
        assert (xml_root.tag == 'DEPENDENT-ON-MODE-IREF')
        mode_declaration_ref = self.parse_text_node(xml_root.find('MODE-DECLARATION-REF'))
        mode_declaration_group_prototype_ref = self.parse_text_node(xml_root.find('MODE-DECLARATION-GROUP-PROTOTYPE-REF'))
        require_port_prototype_ref = self.parse_text_node(xml_root.find('R-PORT-PROTOTYPE-REF'))
        return ModeDependencyRef(mode_declaration_ref, mode_declaration_group_prototype_ref, require_port_prototype_ref)

    def _parse_disabled_modes_instance_refs(self, xml_root: Element, *_) -> list[DisabledModeInstanceRef]:
        """parses <DISABLED-MODE-IREFS>"""
        assert (xml_root.tag == 'DISABLED-MODE-IREFS')
        disabled_in_modes = []
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag != 'DISABLED-MODE-IREF':
                self._logger.error(f'Unexpected tag: {xml_elem.tag}')
                continue
            disabled_mode_ref = self._parse_disabled_mode_instance_ref(xml_elem)
            if disabled_mode_ref is not None:
                disabled_in_modes.append(disabled_mode_ref)
        return disabled_in_modes

    def _parse_disabled_mode_instance_ref(self, xml_root: Element) -> DisabledModeInstanceRef | None:
        """parses <DISABLED-MODE-IREF>"""
        require_port_prototype_ref = None
        mode_declaration_group_prototype_ref = None
        mode_declaration_ref = None
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'CONTEXT-PORT-REF':
                require_port_prototype_ref = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'CONTEXT-MODE-DECLARATION-GROUP-PROTOTYPE-REF':
                mode_declaration_group_prototype_ref = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'TARGET-MODE-DECLARATION-REF':
                mode_declaration_ref = self.parse_text_node(xml_elem)
            else:
                self._logger.warning(f'Unexpected tag: {xml_elem.tag}')
        if mode_declaration_ref is None or mode_declaration_group_prototype_ref is None or require_port_prototype_ref is None:
            self._logger.error('Parse Error: <CONTEXT-PORT-REF DEST>, <CONTEXT-MODE-DECLARATION-GROUP-PROTOTYPE-REF> '
                               'and <TARGET-MODE-DECLARATION-REF> must be defined')
            return None
        return DisabledModeInstanceRef(mode_declaration_ref, mode_declaration_group_prototype_ref, require_port_prototype_ref)

    def parse_init_event(self, xml_node: Element, parent: ArObject | None = None) -> InitEvent:
        name = self.parse_text_node(xml_node.find('SHORT-NAME'))
        start_on_event_ref = self.parse_text_node(xml_node.find('START-ON-EVENT-REF'))
        init_event = InitEvent(name, start_on_event_ref, parent)
        return init_event

    def parse_mode_switch_event(self, xml_node: Element, parent: ArObject | None = None) -> ModeSwitchEvent | None:
        """parses AUTOSAR3 <MODE-SWITCH-EVENT>"""
        if self.version < 4.0:
            assert (xml_node.tag == 'MODE-SWITCH-EVENT')
            name = self.parse_text_node(xml_node.find('SHORT-NAME'))
            mode_inst_ref = self.parse_mode_instance_ref(xml_node.find('MODE-IREF'))
            start_on_event_ref = self.parse_text_node(xml_node.find('START-ON-EVENT-REF'))
            activation = self.parse_text_node(xml_node.find('ACTIVATION'))
            mode_switch_event = ModeSwitchEvent(name, start_on_event_ref, activation, parent, self.version)
            mode_switch_event.mode_inst_ref = mode_inst_ref
        elif self.version >= 4.0:
            assert (xml_node.tag == 'SWC-MODE-SWITCH-EVENT')
            name = self.parse_text_node(xml_node.find('SHORT-NAME'))
            mode_instance_refs = []
            for xml_elem in xml_node.findall('./MODE-IREFS/*'):
                if xml_elem.tag != 'MODE-IREF':
                    self._logger.error(f'Unexpected tag: {xml_elem.tag}')
                    continue
                mode_instance_ref = self.parse_mode_instance_ref(xml_elem)
                if mode_instance_ref is not None:
                    mode_instance_refs.append(mode_instance_ref)
            start_on_event_ref = self.parse_text_node(xml_node.find('START-ON-EVENT-REF'))
            activation = self.parse_text_node(xml_node.find('ACTIVATION'))
            mode_switch_event = ModeSwitchEvent(name, start_on_event_ref, activation, parent, self.version)
            mode_switch_event.mode_inst_ref = mode_instance_refs[0]
        else:
            self._logger.error(f'Unsupported version: {self.version}')
            return None
        return mode_switch_event

    def parse_mode_switched_ack_event(self, xml_node: Element, parent: ArObject | None = None) -> ModeSwitchAckEvent | None:
        if self.version < 4.0:
            self._logger.error(f'Unsupported version: {self.version}')
            return None
        assert (xml_node.tag == 'MODE-SWITCHED-ACK-EVENT')
        name = None
        start_on_event_ref = None
        event_source_ref = None
        xml_disabled_mode_refs = None
        for xml_elem in xml_node.findall('./*'):
            if xml_elem.tag == 'SHORT-NAME':
                name = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'DISABLED-MODE-IREFS':
                xml_disabled_mode_refs = xml_elem
            elif xml_elem.tag == 'START-ON-EVENT-REF':
                start_on_event_ref = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'EVENT-SOURCE-REF':
                event_source_ref = self.parse_text_node(xml_elem)
            else:
                self._logger.warning(f'Unexpected tag: {xml_elem.tag}')
        if name is None:
            return None
        mode_switch_event = ModeSwitchAckEvent(name, start_on_event_ref, event_source_ref, parent)
        if xml_disabled_mode_refs is not None:
            mode_switch_event.disabled_in_modes = self._parse_disabled_modes_instance_refs(xml_disabled_mode_refs)
        return mode_switch_event

    def parse_timing_event(self, xml_node: Element, parent: ArObject | None = None) -> TimingEvent | None:
        name = None
        start_on_event_ref = None
        period = None
        xml_mode_dependency = None
        xml_disabled_mode_refs = None
        for xml_elem in xml_node.findall('./*'):
            if xml_elem.tag == 'SHORT-NAME':
                name = self.parse_text_node(xml_elem)
            elif self.version >= 4.0 and xml_elem.tag == 'DISABLED-MODE-IREFS':
                xml_disabled_mode_refs = xml_elem
            elif self.version < 4.0 and xml_elem.tag == 'MODE-DEPENDENCY':
                xml_mode_dependency = xml_elem
            elif xml_elem.tag == 'START-ON-EVENT-REF':
                start_on_event_ref = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'PERIOD':
                period = self.parse_text_node(xml_elem)
            else:
                self._logger.warning(f'Unexpected tag: {xml_elem.tag}')

        if name is None or start_on_event_ref is None or period is None:
            self._logger.error('Parse error: <SHORT-NAME> and <START-ON-EVENT-REF> and <PERIOD> must be defined')
            return None
        timing_event = TimingEvent(name, start_on_event_ref, float(period) * 1000, parent)
        if xml_mode_dependency is not None:
            timing_event.mode_dependency = self._parse_mode_dependency(xml_mode_dependency)
        elif xml_disabled_mode_refs is not None:
            timing_event.disabled_in_modes = self._parse_disabled_modes_instance_refs(xml_disabled_mode_refs)
        return timing_event

    def parse_data_received_event(self, xml_root: Element, parent: ArObject | None = None) -> DataReceivedEvent:
        name = self.parse_text_node(xml_root.find('SHORT-NAME'))
        start_on_event_ref = self.parse_text_node(xml_root.find('START-ON-EVENT-REF'))
        port_tag = 'CONTEXT-R-PORT-REF' if self.version >= 4.0 else 'R-PORT-PROTOTYPE-REF'
        data_instance_ref = self.parse_data_instance_ref(xml_root.find('DATA-IREF'), port_tag)
        data_received_event = DataReceivedEvent(name, start_on_event_ref, parent)
        xml_mode_dependency = xml_root.find('MODE-DEPENDENCY')
        if xml_mode_dependency is not None:
            data_received_event.mode_dependency = self._parse_mode_dependency(xml_mode_dependency)
        data_received_event.data_instance_ref = data_instance_ref
        return data_received_event

    def parse_operation_invoked_event(self, xml_root: Element, parent: ArObject | None = None) -> OperationInvokedEvent:
        name = None
        start_on_event_ref = None
        mode_dependency = None
        operation_instance_ref = None
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'SHORT-NAME':
                name = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'START-ON-EVENT-REF':
                start_on_event_ref = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'OPERATION-IREF':
                port_tag = 'CONTEXT-P-PORT-REF' if self.version >= 4.0 else 'P-PORT-PROTOTYPE-REF'
                operation_instance_ref = self.parse_operation_instance_ref(xml_elem, port_tag)
            elif xml_elem.tag == 'MODE-DEPENDENCY':
                mode_dependency = self._parse_mode_dependency(xml_elem)
            else:
                self._logger.warning(f'Unexpected tag: {xml_elem.tag}')
        operation_invoked_event = OperationInvokedEvent(name, start_on_event_ref, parent)
        operation_invoked_event.mode_dependency = mode_dependency
        operation_invoked_event.operation_instance_ref = operation_instance_ref
        return operation_invoked_event

    def parse_data_instance_ref(self, xml_root: Element, port_tag: str) -> DataInstanceRef:
        """parses <DATA-IREF>"""
        assert (xml_root.tag == 'DATA-IREF')
        data_elem_tag = 'TARGET-DATA-ELEMENT-REF' if self.version >= 4.0 else 'DATA-ELEMENT-PROTOTYPE-REF'
        port_ref = None
        data_elem_ref = None
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == port_tag:
                port_ref = self.parse_text_node(xml_elem)
            elif xml_elem.tag == data_elem_tag:
                data_elem_ref = self.parse_text_node(xml_elem)
            else:
                self._logger.warning(f'Unexpected tag: {xml_elem.tag}')
        return DataInstanceRef(port_ref, data_elem_ref)

    def parse_operation_instance_ref(self, xml_root: Element, port_tag: str) -> OperationInstanceRef:
        """parses <OPERATION-IREF>"""
        assert (xml_root.tag == 'OPERATION-IREF')
        assert (xml_root.find(port_tag) is not None)

        if self.version >= 4.0:
            if port_tag == 'CONTEXT-P-PORT-REF':
                operation_tag = 'TARGET-PROVIDED-OPERATION-REF'
            else:
                operation_tag = 'TARGET-REQUIRED-OPERATION-REF'
        else:
            operation_tag = 'OPERATION-PROTOTYPE-REF'
        return OperationInstanceRef(
            self.parse_text_node(xml_root.find(port_tag)),
            self.parse_text_node(xml_root.find(operation_tag)),
        )

    def parse_data_element_instance_ref(self, xml_root: Element, port_tag: str):
        """parses <DATA-ELEMENT-IREF>"""
        assert (xml_root.tag == 'DATA-ELEMENT-IREF')
        assert (xml_root.find(port_tag) is not None)
        return DataElementInstanceRef(
            self.parse_text_node(xml_root.find(port_tag)),
            self.parse_text_node(xml_root.find('DATA-ELEMENT-PROTOTYPE-REF')),
        )

    def parse_swc_nv_block_needs(self, xml_root: Element) -> SwcNvBlockNeeds:
        name = self.parse_text_node(xml_root.find('SHORT-NAME'))
        number_of_data_sets = self.parse_int_node(xml_root.find('N-DATA-SETS'))
        read_only = self.parse_boolean_node(xml_root.find('READONLY'))
        reliability = self.parse_text_node(xml_root.find('RELIABILITY'))
        resistant_to_changed_sw = self.parse_boolean_node(xml_root.find('RESISTANT-TO-CHANGED-SW'))
        restore_at_start = self.parse_boolean_node(xml_root.find('RESTORE-AT-START'))
        write_only_once = self.parse_boolean_node(xml_root.find('WRITE-ONLY-ONCE'))
        writing_frequency = self.parse_int_node(xml_root.find('WRITING-FREQUENCY'))
        writing_priority = self.parse_text_node(xml_root.find('WRITING-PRIORITY'))
        default_block_ref = self.parse_text_node(xml_root.find('DEFAULT-BLOCK-REF'))
        mirror_block_ref = self.parse_text_node(xml_root.find('MIRROR-BLOCK-REF'))
        service_call_ports = self.parse_service_call_ports(xml_root.find('SERVICE-CALL-PORTS'))
        assert (len(service_call_ports) > 0)
        swc_nv_block_needs = SwcNvBlockNeeds(
            name,
            number_of_data_sets,
            read_only,
            reliability,
            resistant_to_changed_sw,
            restore_at_start,
            write_only_once,
            writing_frequency,
            writing_priority,
            default_block_ref,
            mirror_block_ref,
        )
        swc_nv_block_needs.service_call_ports = service_call_ports
        return swc_nv_block_needs

    def parse_service_call_ports(self, xml_root: Element) -> list[RoleBasedRPortAssignment]:
        """parses <SERVICE-CALL-PORTS>"""
        assert (xml_root.tag == 'SERVICE-CALL-PORTS')
        service_call_ports = []
        for xml_node in xml_root.findall('ROLE-BASED-R-PORT-ASSIGNMENT'):
            role_based_r_port_assignment = RoleBasedRPortAssignment(
                self.parse_text_node(xml_node.find('R-PORT-PROTOTYPE-REF')),
                self.parse_text_node(xml_node.find('ROLE')),
            )
            service_call_ports.append(role_based_r_port_assignment)
        return service_call_ports

    def parse_cal_prm_elem_prototype(self, xml_root: Element, parent: ArObject) -> CalPrmElemPrototype:
        """
        parses <CALPRM-ELEMENT-PROTOTYPE>
        """
        name = self.parse_text_node(xml_root.find('SHORT-NAME'))
        admin_data = self.parse_admin_data_node(xml_root.find('ADMIN-DATA'))
        type_ref = self.parse_text_node(xml_root.find('TYPE-TREF'))
        cal_prm_elem_prototype = CalPrmElemPrototype(name, type_ref, parent, admin_data)
        for xml_elem in xml_root.findall('./SW-DATA-DEF-PROPS/*'):
            if xml_elem.tag != 'SW-ADDR-METHOD-REF':
                self._logger.error(f'Unexpected tag: {xml_elem.tag}')
                continue
            cal_prm_elem_prototype.sw_data_def_props.append(self.parse_text_node(xml_elem))
        return cal_prm_elem_prototype

    def parse_sync_server_call_point(self, xml_root: Element) -> SyncServerCallPoint | None:
        """
        parses <SYNCHRONOUS-SERVER-CALL-POINT>
        """
        assert (xml_root.tag == 'SYNCHRONOUS-SERVER-CALL-POINT')
        name = None
        operation_instance_refs = []
        timeout = 0.0
        if self.version >= 4.0:
            for xml_elem in xml_root.findall('*'):
                if xml_elem.tag == 'SHORT-NAME':
                    name = self.parse_text_node(xml_elem)
                elif xml_elem.tag == 'OPERATION-IREF':
                    operation_instance_refs.append(self.parse_operation_instance_ref(
                        xml_elem,
                        'CONTEXT-R-PORT-REF',
                    ))
                elif xml_elem.tag == 'TIMEOUT':
                    timeout = self.parse_float_node(xml_elem)
                else:
                    self._logger.warning(f'Unexpected tag: {xml_elem.tag}')
        else:
            for xml_elem in xml_root.findall('*'):
                if xml_elem.tag == 'SHORT-NAME':
                    name = self.parse_text_node(xml_elem)
                elif xml_elem.tag == 'OPERATION-IREFS':
                    for xml_operation in xml_elem.findall('*'):
                        if xml_operation.tag != 'OPERATION-IREF':
                            self._logger.error(f'Unexpected tag: {xml_operation.tag}')
                            continue
                        operation_instance_refs.append(self.parse_operation_instance_ref(
                            xml_operation,
                            'R-PORT-PROTOTYPE-REF',
                        ))
                elif xml_elem.tag == 'TIMEOUT':
                    timeout = self.parse_float_node(xml_elem)
                else:
                    self._logger.warning(f'Unexpected tag: {xml_elem.tag}')
        if name is None:
            return None
        retval = SyncServerCallPoint(name, timeout)
        retval.operation_instance_refs = operation_instance_refs
        return retval

    def parse_accessed_variable(self, xml_root: Element) -> VariableAccess:
        assert (xml_root.tag == 'ACCESSED-VARIABLE')
        xml_port_prototype_ref = xml_root.find('./AUTOSAR-VARIABLE-IREF/PORT-PROTOTYPE-REF')
        xml_target_data_prototype_ref = xml_root.find('./AUTOSAR-VARIABLE-IREF/TARGET-DATA-PROTOTYPE-REF')
        assert (xml_port_prototype_ref is not None)
        assert (xml_target_data_prototype_ref is not None)
        return VariableAccess(
            self.parse_text_node(xml_root.find('SHORT-NAME')),
            self.parse_text_node(xml_port_prototype_ref),
            self.parse_text_node(xml_target_data_prototype_ref),
        )

    def parse_swc_service_dependency(self, xml_root: Element, parent: ArObject | None = None) -> SwcServiceDependency:
        """parses <SWC-SERVICE-DEPENDENCY>"""
        assert (xml_root.tag == 'SWC-SERVICE-DEPENDENCY')
        name = None
        desc = None
        service_needs = None
        role_based_data_assignments = []
        role_based_port_assignments = []
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'SHORT-NAME':
                name = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'DESC':
                desc = self.parse_desc_direct(xml_elem)
            elif xml_elem.tag == 'ASSIGNED-DATAS':
                for xml_child_elem in xml_elem.findall('./*'):
                    if xml_child_elem.tag != 'ROLE-BASED-DATA-ASSIGNMENT':
                        self._logger.error(f'Unexpected tag: {xml_child_elem.tag}')
                        continue
                    tmp = self._parse_role_based_data_assignment(xml_child_elem)
                    if tmp is not None:
                        role_based_data_assignments.append(tmp)
            elif xml_elem.tag == 'ASSIGNED-PORTS':
                for xml_child_elem in xml_elem.findall('./*'):
                    if xml_child_elem.tag != 'ROLE-BASED-PORT-ASSIGNMENT':
                        self._logger.error(f'Unexpected tag: {xml_child_elem.tag}')
                        continue
                    tmp = self._parse_role_based_port_assignment(xml_child_elem)
                    if tmp is not None:
                        role_based_port_assignments.append(tmp)
            elif xml_elem.tag == 'SERVICE-NEEDS':
                service_needs = self.parse_service_needs(xml_elem)
            else:
                self._logger.warning(f'Unexpected tag: {xml_elem.tag}')
        swc_service_dependency = SwcServiceDependency(name, parent=parent)
        if desc is not None:
            swc_service_dependency.desc = desc[0]
            swc_service_dependency.desc_attr = desc[1]
        if service_needs is not None:
            swc_service_dependency.service_needs = service_needs
        if len(role_based_data_assignments) > 0:
            swc_service_dependency.role_based_data_assignments = role_based_data_assignments
        if len(role_based_port_assignments) > 0:
            swc_service_dependency.role_based_port_assignments = role_based_port_assignments
        return swc_service_dependency

    def parse_parameter_data_prototype(self, xml_root: Element, parent: ArObject | None = None) -> ParameterDataPrototype:
        """parses <PARAMETER-DATA-PROTOTYPE> (AUTOSAR 4)"""
        assert (xml_root.tag == 'PARAMETER-DATA-PROTOTYPE')
        type_ref = None
        sw_address_method_ref = None
        sw_calibration_access = None
        init_value = None
        init_value_ref = None
        self.push()
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'SW-DATA-DEF-PROPS':
                variants = self.parse_sw_data_def_props(xml_elem)
                if len(variants) > 0:
                    sw_address_method_ref = variants[0].sw_address_method_ref
                    sw_calibration_access = variants[0].sw_calibration_access
            elif xml_elem.tag == 'INIT-VALUE':
                for xml_child in xml_elem.findall('./*'):
                    if xml_child.tag == 'CONSTANT-REFERENCE':
                        init_value_ref = self.parse_text_node(xml_child.find('./CONSTANT-REF'))
                    else:
                        values = self.constant_parser.parse_value_v4(xml_elem, None)
                        if len(values) != 1:
                            self._logger.error(f'{xml_elem.tag} cannot cannot contain multiple elements')
                        init_value = values[0]
            elif xml_elem.tag == 'TYPE-TREF':
                type_ref = self.parse_text_node(xml_elem)
            else:
                self.base_handler(xml_elem)
        obj = ParameterDataPrototype(
            self.name,
            type_ref=type_ref,
            sw_address_method_ref=sw_address_method_ref,
            sw_calibration_access=sw_calibration_access,
            init_value=init_value,
            init_value_ref=init_value_ref,
            parent=parent,
            admin_data=self.admin_data,
        )
        self.pop(obj)
        return obj

    def parse_service_needs(self, xml_root: Element, parent: ArObject | None = None) -> ServiceNeeds:
        """parses <SERVICE-NEEDS> (AUTOSAR 4)"""
        assert (xml_root.tag == 'SERVICE-NEEDS')
        xml_nv_block_needs = None
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag != 'NV-BLOCK-NEEDS':
                self._logger.error(f'Unexpected tag: {xml_elem.tag}')
                continue
            xml_nv_block_needs = xml_elem
        service_needs = ServiceNeeds(None, parent)
        if xml_nv_block_needs is not None:
            service_needs.nvm_block_needs = self.parse_nvm_block_needs(xml_nv_block_needs, service_needs)
        return service_needs

    def parse_nvm_block_needs(self, xml_root: Element, parent: ArObject | None = None) -> NvmBlockNeeds | None:
        """parses <NV-BLOCK-NEEDS> (AUTOSAR 4)"""
        config = NvmBlockConfig()

        self.push()
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'N-DATA-SETS':
                config.number_of_data_sets = self.parse_int_node(xml_elem)
            elif xml_elem.tag == 'N-ROM-BLOCKS':
                config.number_of_rom_blocks = self.parse_int_node(xml_elem)
            elif xml_elem.tag == 'RAM-BLOCK-STATUS-CONTROL':
                config.ram_block_status_control = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'RELIABILITY':
                config.reliability = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'WRITING-PRIORITY':
                config.writing_priority = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'WRITING-FREQUENCY':
                config.writing_frequency = self.parse_int_node(xml_elem)
            elif xml_elem.tag == 'CALC-RAM-BLOCK-CRC':
                config.calc_ram_block_crc = self.parse_boolean_node(xml_elem)
            elif xml_elem.tag == 'CHECK-STATIC-BLOCK-ID':
                config.check_static_block_id = self.parse_boolean_node(xml_elem)
            elif xml_elem.tag == 'READONLY':
                config.read_only = self.parse_boolean_node(xml_elem)
            elif xml_elem.tag == 'RESISTANT-TO-CHANGED-SW':
                config.resistant_to_changed_sw = self.parse_boolean_node(xml_elem)
            elif xml_elem.tag == 'RESTORE-AT-START':
                config.restore_at_startup = self.parse_boolean_node(xml_elem)
            elif xml_elem.tag == 'STORE-AT-SHUTDOWN':
                config.store_at_shutdown = self.parse_boolean_node(xml_elem)
            elif xml_elem.tag == 'WRITE-VERIFICATION':
                config.write_verification = self.parse_boolean_node(xml_elem)
            elif xml_elem.tag == 'WRITE-ONLY-ONCE':
                config.write_only_once = self.parse_boolean_node(xml_elem)
            elif xml_elem.tag == 'USE-AUTO-VALIDATION-AT-SHUT-DOWN':
                config.auto_validation_at_shutdown = self.parse_boolean_node(xml_elem)
            elif xml_elem.tag == 'USE-CRC-COMP-MECHANISM':
                config.use_crc_comp_mechanism = self.parse_boolean_node(xml_elem)
            elif xml_elem.tag == 'STORE-EMERGENCY':
                config.store_emergency = self.parse_boolean_node(xml_elem)
            elif xml_elem.tag == 'STORE-IMMEDIATE':
                config.store_immediate = self.parse_boolean_node(xml_elem)
            elif xml_elem.tag == 'STORE-CYCLIC':
                config.store_cyclic = self.parse_boolean_node(xml_elem)
            elif xml_elem.tag == 'CYCLIC-WRITING-PERIOD':
                config.cyclic_write_period = self.parse_float_node(xml_elem)
            else:
                self.base_handler(xml_elem)

        if self.name is None:
            self._logger.error('<SHORT-NAME> is missing or incorrectly formatted')
            return None
        config.check()
        obj = NvmBlockNeeds(self.name, block_config=config, parent=parent, admin_data=self.admin_data)
        self.pop(obj)
        return obj

    def _parse_role_based_data_assignment(self, xml_root: Element) -> RoleBasedDataAssignment | None:
        assert (xml_root.tag == 'ROLE-BASED-DATA-ASSIGNMENT')
        role = None
        local_variable_ref = None
        local_parameter_ref = None
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'ROLE':
                role = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'USED-DATA-ELEMENT':
                for xml_child in xml_elem.findall('./*'):
                    if xml_child.tag != 'LOCAL-VARIABLE-REF':
                        self._logger.error(f'Unexpected tag: {xml_child.tag}')
                        continue
                    local_variable_ref = self.parse_text_node(xml_child)
            elif xml_elem.tag == 'USED-PARAMETER-ELEMENT':
                pass
                for xml_child in xml_elem.findall('./*'):
                    if xml_child.tag != 'LOCAL-PARAMETER-REF':
                        self._logger.error(f'Unexpected tag: {xml_child.tag}')
                        continue
                    local_parameter_ref = LocalParameterRef(self.parse_text_node(xml_child))
            else:
                raise NotImplementedError(xml_elem.tag)
        if role is None or (local_variable_ref is None and local_parameter_ref is None):
            return None
        return RoleBasedDataAssignment(role, local_variable_ref, local_parameter_ref)

    def _parse_role_based_port_assignment(self, xml_root: Element) -> RoleBasedPortAssignment | None:
        assert (xml_root.tag == 'ROLE-BASED-PORT-ASSIGNMENT')
        port_ref = None
        role = None
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'PORT-PROTOTYPE-REF':
                port_ref = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'ROLE':
                port_ref = self.parse_text_node(xml_elem)
            else:
                self.base_handler(xml_elem)
        if port_ref is None:
            return None
        return RoleBasedPortAssignment(port_ref, role)

    def parse_autosar_variable_ref_xml(self, xml_root: Element) -> tuple[str | None, str | None, str | None]:
        local_variable_ref = None
        port_prototype_ref = None
        target_data_prototype_ref = None
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'LOCAL-VARIABLE-REF':
                local_variable_ref = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'AUTOSAR-VARIABLE-IREF' or xml_elem.tag == 'AUTOSAR-VARIABLE-IN-IMPL-DATATYPE':
                xml_port_prototype_ref = xml_elem.find('./PORT-PROTOTYPE-REF')
                xml_target_data_prototype_ref = xml_elem.find('./TARGET-DATA-PROTOTYPE-REF')
                assert (xml_port_prototype_ref is not None)
                assert (xml_target_data_prototype_ref is not None)
                port_prototype_ref = self.parse_text_node(xml_port_prototype_ref)
                target_data_prototype_ref = self.parse_text_node(xml_target_data_prototype_ref)
        return local_variable_ref, port_prototype_ref, target_data_prototype_ref

    def parse_nv_block_sw_cnv_block_descriptor(self, xml_root: Element, parent: ArObject):
        """AUTOSAR 4 NV-BLOCK-DESCRIPTOR"""
        assert (xml_root.tag == 'NV-BLOCK-DESCRIPTOR')
        name = self.parse_text_node(xml_root.find('SHORT-NAME'))
        ws = parent.root_ws()
        assert (ws is not None)
        if name is None:
            return None
        handled_xml = ['SHORT-NAME']
        descriptor = NvBlockDescriptor(name, parent)
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag in handled_xml:
                continue
            elif xml_elem.tag == 'DATA-TYPE-MAPPING-REFS':
                for xml_child in xml_elem.findall('./*'):
                    if xml_child.tag == 'DATA-TYPE-MAPPING-REF':
                        tmp = self.parse_text_node(xml_child)
                        assert (tmp is not None)
                        descriptor.data_type_mapping_refs.append(tmp)
            elif xml_elem.tag == 'NV-BLOCK-DATA-MAPPINGS':
                for xml_mapping in xml_elem.findall('./NV-BLOCK-DATA-MAPPING'):
                    data_mapping = NvBlockDataMapping(descriptor)
                    descriptor.nv_block_data_mappings.append(data_mapping)
                    for xml_data in xml_mapping.findall('./*'):
                        (
                            local_variable_ref,
                            port_prototype_ref,
                            target_data_prototype_ref,
                        ) = self.parse_autosar_variable_ref_xml(xml_data)
                        if xml_data.tag == 'NV-RAM-BLOCK-ELEMENT':
                            if local_variable_ref is None:
                                self._logger.error(f'Cannot find needed LOCAL-VARIABLE-REF for NV-RAM-BLOCK-ELEMENT in {descriptor.name}')
                                continue
                            data_mapping.nv_ram_block_element = NvRamBlockElement(data_mapping, local_variable_ref=local_variable_ref)
                        elif xml_data.tag == 'READ-NV-DATA':
                            if port_prototype_ref is None and target_data_prototype_ref is None:
                                self._logger.error(f'Cannot find needed AUTOSAR-VARIABLE-IREF '
                                                   f'or AUTOSAR-VARIABLE-IN-IMPL-DATATYPE for READ-NV-DATA in {descriptor.name}')
                                continue
                            data_mapping.read_nv_data = ReadNvData(
                                data_mapping,
                                autosar_variable_port_ref=port_prototype_ref,
                                autosar_variable_element_ref=target_data_prototype_ref,
                            )
                        elif xml_data.tag == 'WRITTEN-NV-DATA':
                            if port_prototype_ref is None and target_data_prototype_ref is None:
                                self._logger.error(f'Cannot find needed AUTOSAR-VARIABLE-IREF '
                                                   f'or AUTOSAR-VARIABLE-IN-IMPL-DATATYPE for WRITTEN-NV-DATA in {descriptor.name}')
                                continue
                            data_mapping.written_nv_data = WrittenNvData(
                                data_mapping,
                                autosar_variable_port_ref=port_prototype_ref,
                                autosar_variable_element_ref=target_data_prototype_ref,
                            )
                        elif xml_data.tag == 'WRITTEN-READ-NV-DATA':
                            if port_prototype_ref is None and target_data_prototype_ref is None:
                                self._logger.error(f'Cannot find needed AUTOSAR-VARIABLE-IREF '
                                                   f'or AUTOSAR-VARIABLE-IN-IMPL-DATATYPE for WRITTEN-READ-NV-DATA in {descriptor.name}')
                                continue
                            data_mapping.written_read_nv_data = WrittenReadNvData(
                                data_mapping,
                                autosar_variable_port_ref=port_prototype_ref,
                                autosar_variable_element_ref=target_data_prototype_ref,
                            )
                        else:
                            self._logger.warning(f'Unexpected tag: {xml_data.tag}')
            elif xml_elem.tag == 'NV-BLOCK-NEEDS':
                descriptor.nv_block_needs = self.parse_nvm_block_needs(xml_elem, descriptor)
            elif xml_elem.tag == 'RAM-BLOCK':
                # Change tag so it is correct for the parser.
                xml_elem.tag = 'VARIABLE-DATA-PROTOTYPE'
                data_element = self.parse_variable_data_prototype(xml_elem, descriptor)
                if data_element is not None:
                    # Cast the object to correct class.
                    descriptor.ram_block = NvBlockRamBlock.cast(data_element)
            elif xml_elem.tag == 'ROM-BLOCK':
                # Change tag so it is correct for the parser.
                xml_elem.tag = 'PARAMETER-DATA-PROTOTYPE'
                data_element = self.parse_parameter_data_prototype(xml_elem, descriptor)
                # Cast the object to correct class.
                descriptor.rom_block = NvBlockRomBlock.cast(data_element)
            elif xml_elem.tag == 'SUPPORT-DIRTY-FLAG':
                dirty_flag = self.parse_boolean_node(xml_elem)
                if dirty_flag is not None:
                    descriptor.support_dirty_flag = dirty_flag
            elif xml_elem.tag == 'TIMING-EVENT-REF':
                timing_ref = self.parse_text_node(xml_elem)
                if timing_ref is None:
                    continue
                timing_event = None
                parts = timing_ref.partition('/')
                while True:
                    name, _, tail = parts
                    if name == parent.name:
                        timing_event = parent.find(tail)
                        if timing_event is not None:
                            break
                    elif len(tail) == 0:
                        break
                    parts = tail.partition('/')

                if timing_event is None:
                    self._logger.error(f'Cannot find timing event "{timing_ref}"')
                    continue
                descriptor.timing_event_ref = timing_event.name
            else:
                self._logger.warning(f'Unexpected tag: {xml_elem.tag}')
        return descriptor
