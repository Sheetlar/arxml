from typing import Callable
from xml.etree.ElementTree import Element

from autosar.ar_object import ArObject
from autosar.base import has_admin_data, parse_admin_data_node
from autosar.element import DataElement, ParameterDataPrototype, SoftwareAddressMethod
from autosar.mode import ModeGroup
from autosar.parser.parser_base import ElementParser
from autosar.portinterface import (
    SenderReceiverInterface,
    InvalidationPolicy,
    ParameterInterface,
    ClientServerInterface,
    ModeSwitchInterface,
    Operation,
    Argument,
    ApplicationError,
    NvDataInterface,
    PortInterface,
    TriggerInterface,
    Trigger,
)


class PortInterfacePackageParser(ElementParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 3.0 <= self.version < 4.0:
            self.switcher: dict[str, Callable[[Element, ArObject], PortInterface | None]] = {
                'SENDER-RECEIVER-INTERFACE': self.parse_sender_receiver_interface,
                'CALPRM-INTERFACE': self.parse_cal_prm_interface,
                'CLIENT-SERVER-INTERFACE': self.parse_client_server_interface,
            }
        elif self.version >= 4.0:
            self.switcher: dict[str, Callable[[Element, ArObject], PortInterface | None]] = {
                'SENDER-RECEIVER-INTERFACE': self.parse_sender_receiver_interface,
                'PARAMETER-INTERFACE': self.parse_parameter_interface,
                'CLIENT-SERVER-INTERFACE': self.parse_client_server_interface,
                'MODE-SWITCH-INTERFACE': self.parse_mode_switch_interface,
                'NV-DATA-INTERFACE': self.parse_nv_data_interface,
                'TRIGGER-INTERFACE': self.parse_trigger_interface,
            }

    def get_supported_tags(self):
        return self.switcher.keys()

    def parse_element(self, xml_element: Element, parent: ArObject | None = None) -> PortInterface | None:
        parse_func = self.switcher.get(xml_element.tag)
        if parse_func is not None:
            return parse_func(xml_element, parent)
        return None

    def parse_sender_receiver_interface(
            self,
            xml_root: Element,
            parent: ArObject | None = None,
    ) -> SenderReceiverInterface | None:
        assert (xml_root.tag == 'SENDER-RECEIVER-INTERFACE')
        is_service = None
        service_kind = None
        data_elements = None
        mode_groups = None
        invalidation_policies = None
        self.push()
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'IS-SERVICE':
                is_service = self.parse_boolean_node(xml_elem)
            elif xml_elem.tag == 'SERVICE-KIND' and self.version >= 4.0:
                service_kind = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'DATA-ELEMENTS':
                data_elements = self._parse_data_elements(xml_elem)
            elif xml_elem.tag == 'MODE-GROUPS' and self.version < 4.0:
                mode_groups = self._parse_mode_groups(xml_elem)
            elif xml_elem.tag == 'INVALIDATION-POLICYS' and self.version >= 4.0:
                invalidation_policies = self._parse_invalidation_policies(xml_elem)
            else:
                self.default_handler(xml_elem)
        if self.name is None:
            self.pop()
            return None
        port_interface = SenderReceiverInterface(self.name, is_service, service_kind, parent=parent, admin_data=self.admin_data)
        if data_elements is not None:
            for data_element in data_elements:
                data_element.parent = port_interface
                port_interface.data_elements.append(data_element)
        if mode_groups is not None:
            for mode_group in mode_groups:
                mode_group.parent = port_interface
                port_interface.mode_groups.append(mode_group)
        if invalidation_policies is not None:
            for policy in invalidation_policies:
                policy.parent = port_interface
                port_interface.invalidation_policies.append(policy)
        self.pop(port_interface)
        return port_interface

    def _parse_data_elements(self, xml_root: Element) -> list[DataElement]:
        data_elements = []
        if self.version >= 4.0:
            parse_method = self.parse_variable_data_prototype
            data_elem_tag = 'VARIABLE-DATA-PROTOTYPE'
        else:
            parse_method = self._parse_data_element_prototype
            data_elem_tag = 'DATA-ELEMENT-PROTOTYPE'
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag != data_elem_tag:
                self._logger.error(f'Unexpected tag: {xml_elem.tag}')
                continue
            data_elem = parse_method(xml_elem)
            if data_elem is not None:
                data_elements.append(data_elem)
        return data_elements

    def _parse_mode_groups(self, xml_root: Element) -> list[ModeGroup]:
        assert (xml_root.tag == 'MODE-GROUPS')
        mode_groups = []
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag != 'MODE-DECLARATION-GROUP-PROTOTYPE':
                self._logger.error(f'Unexpected tag: {xml_elem.tag}')
                continue
            self.push()
            type_ref = None
            for xml_child in xml_elem.findall('./*'):
                if xml_child.tag == 'TYPE-TREF':
                    type_ref = self.parse_text_node(xml_child)
                else:
                    self.default_handler(xml_child)
            if self.name is not None and type_ref is not None:
                mode_groups.append(ModeGroup(self.name, type_ref))
            self.pop()
        return mode_groups

    def _parse_invalidation_policies(self, xml_root: Element) -> list[InvalidationPolicy]:
        assert (xml_root.tag == 'INVALIDATION-POLICYS')
        policy_list = []
        for xml_child in xml_root.findall('./*'):
            if xml_child.tag != 'INVALIDATION-POLICY':
                self._logger.error(f'Unexpected tag: {xml_child.tag}')
                continue
            invalidation_policy = self._parse_invalidation_policy(xml_child)
            if invalidation_policy is not None:
                policy_list.append(invalidation_policy)
        return policy_list

    def _parse_data_element_prototype(self, xml_root: Element) -> DataElement | None:
        assert (xml_root.tag == 'DATA-ELEMENT-PROTOTYPE')
        type_ref = None
        is_queued = False
        self.push()
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'TYPE-TREF':
                type_ref = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'IS-QUEUED':
                is_queued = self.parse_boolean_node(xml_elem)
            else:
                self.default_handler(xml_elem)
        if self.name is None or type_ref is None:
            self._logger.error('SHORT-NAME and TYPE-TREF must not be None')
            return None
        elem = DataElement(self.name, type_ref, is_queued)
        self.pop(elem)
        return elem

    def _parse_invalidation_policy(self, xml_root: Element) -> InvalidationPolicy | None:
        data_element_ref = None
        handle_invalid = None
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'DATA-ELEMENT-REF':
                data_element_ref = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'HANDLE-INVALID':
                handle_invalid = self.parse_text_node(xml_elem)
            else:
                self._logger.warning(f'Unexpected tag: {xml_elem.tag}')
        if data_element_ref is None or handle_invalid is None:
            self._logger.error('DATA-ELEMENT-REF and HANDLE-INVALID must not be None')
            return None
        return InvalidationPolicy(data_element_ref, handle_invalid)

    def parse_cal_prm_interface(self, xml_root: Element, parent: ArObject | None = None) -> ParameterInterface | None:
        assert (xml_root.tag == 'CALPRM-INTERFACE')
        xml_name = xml_root.find("./SHORT-NAME")
        if xml_name is None:
            return None
        port_interface = ParameterInterface(xml_name.text, parent=parent)
        if xml_root.find("./IS-SERVICE").text == 'true':
            port_interface.is_service = True
        for xml_elem in xml_root.findall('./CALPRM-ELEMENTS/CALPRM-ELEMENT-PROTOTYPE'):
            xml_elem_name = xml_elem.find("./SHORT-NAME")
            if xml_elem_name is not None:
                type_ref = xml_elem.find("./TYPE-TREF").text
                parameter = ParameterDataPrototype(xml_elem_name.text, type_ref, parent=port_interface)
                if has_admin_data(xml_elem):
                    parameter.admin_data = parse_admin_data_node(xml_elem.find('ADMIN-DATA'))
                if xml_elem.find('SW-DATA-DEF-PROPS'):
                    for xml_item in xml_elem.findall('SW-DATA-DEF-PROPS/SW-ADDR-METHOD-REF'):
                        parameter.sw_address_method_ref = self.parse_text_node(xml_item)
                port_interface.append(parameter)
        return port_interface

    def parse_client_server_interface(self, xml_root: Element, parent: ArObject | None = None) -> ClientServerInterface | None:
        assert (xml_root.tag == 'CLIENT-SERVER-INTERFACE')
        name = self.parse_text_node(xml_root.find('SHORT-NAME'))
        if name is None:
            return None
        port_interface = ClientServerInterface(name, parent=parent)
        if has_admin_data(xml_root):
            port_interface.admin_data = parse_admin_data_node(xml_root.find('ADMIN-DATA'))
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'DESC':
                pass  # implement later
            elif (xml_elem.tag == 'SHORT-NAME') or (xml_elem.tag == 'ADMIN-DATA'):
                continue
            elif xml_elem.tag == 'IS-SERVICE':
                if self.parse_text_node(xml_elem) == 'true':
                    port_interface.is_service = True
            elif xml_elem.tag == 'OPERATIONS':
                for xml_child_item in xml_elem.findall('./*'):
                    if ((self.version < 4.0 and xml_child_item.tag == 'OPERATION-PROTOTYPE')
                            or (self.version >= 4.0 and xml_child_item.tag == 'CLIENT-SERVER-OPERATION')):
                        operation = self._parse_operation_prototype(xml_child_item, port_interface)
                        if operation is not None:
                            port_interface.operations.append(operation)
                    else:
                        self._logger.error(f'Unexpected tag: {xml_child_item.tag}')
            elif xml_elem.tag == 'POSSIBLE-ERRORS':
                for xml_error in xml_elem.findall('APPLICATION-ERROR'):
                    application_error = self._parse_application_error(xml_error, port_interface)
                    port_interface.application_errors.append(application_error)
            elif xml_elem.tag == 'SERVICE-KIND':
                port_interface.service_kind = self.parse_text_node(xml_elem)
            else:
                self._logger.warning(f'Unexpected tag: {xml_elem.tag}')
        return port_interface

    def parse_parameter_interface(self, xml_root: Element, parent: ArObject | None = None) -> ParameterInterface | None:
        name = None
        admin_data = None
        is_service = False
        xml_parameters = None
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'SHORT-NAME':
                name = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'ADMIN-DATA':
                admin_data = self.parse_admin_data_node(xml_elem)
            elif xml_elem.tag == 'IS-SERVICE':
                if self.parse_text_node(xml_elem) == 'true':
                    is_service = True
            elif xml_elem.tag == 'PARAMETERS':
                xml_parameters = xml_elem
            else:
                self._logger.warning(f'Unexpected tag: {xml_elem.tag}')
        if name is None or xml_parameters is None:
            return None
        port_interface = ParameterInterface(name, is_service, parent, admin_data)
        for xml_child in xml_parameters.findall('./*'):
            if xml_child.tag != 'PARAMETER-DATA-PROTOTYPE':
                self._logger.error(f'Unexpected tag: {xml_child.tag}')
                continue
            parameter = self._parse_parameter_data_prototype(xml_child, port_interface)
            if parameter is not None:
                port_interface.append(parameter)
        return port_interface

    def parse_mode_switch_interface(self, xml_root: Element, parent: ArObject | None = None) -> ModeSwitchInterface | None:
        name = None
        admin_data = None
        is_service = False
        xml_mode_group = None
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'SHORT-NAME':
                name = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'ADMIN-DATA':
                admin_data = self.parse_admin_data_node(xml_elem)
            elif xml_elem.tag == 'IS-SERVICE':
                if self.parse_text_node(xml_elem) == 'true':
                    is_service = True
            elif xml_elem.tag == 'MODE-GROUP':
                xml_mode_group = xml_elem
            else:
                self._logger.warning(f'Unexpected tag: {xml_elem.tag}')
        if name is None or xml_mode_group is None:
            return None
        port_interface = ModeSwitchInterface(name, is_service, parent, admin_data)
        port_interface.mode_group = self._parse_mode_group(xml_mode_group, port_interface)
        return port_interface

    def _parse_mode_group(self, xml_mode_group: Element, parent: ArObject) -> ModeGroup:
        if self.version >= 4.0:
            assert (xml_mode_group.tag == "MODE-GROUP")
        else:
            assert (xml_mode_group.tag == "MODE-DECLARATION-GROUP-PROTOTYPE")
        name = self.parse_text_node(xml_mode_group.find('SHORT-NAME'))
        type_ref = self.parse_text_node(xml_mode_group.find('TYPE-TREF'))
        return ModeGroup(name, type_ref, parent)

    def _parse_operation_prototype(self, xml_operation: Element, parent: ClientServerInterface) -> Operation | None:
        name = None
        xml_desc = None
        xml_arguments = None
        xml_possible_error_refs = None
        for xml_elem in xml_operation.findall('./*'):
            if xml_elem.tag == 'ADMIN-DATA':
                pass  # implement later
            elif xml_elem.tag == 'SHORT-NAME':
                name = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'DESC':
                xml_desc = xml_elem
            elif xml_elem.tag == 'ARGUMENTS':
                xml_arguments = xml_elem
            elif xml_elem.tag == 'POSSIBLE-ERROR-REFS':
                xml_possible_error_refs = xml_elem
            else:
                self._logger.warning(f'Unexpected tag: {xml_elem.tag}')
        if name is None:
            return None
        operation = Operation(name, parent)
        argument_tag = 'ARGUMENT-DATA-PROTOTYPE' if self.version >= 4.0 else 'ARGUMENT-PROTOTYPE'
        if xml_desc is not None:
            self.parse_desc(xml_operation, operation)
        if xml_arguments is not None:
            for xml_child in xml_arguments.findall('./*'):
                if xml_child.tag != argument_tag:
                    self._logger.error(f'Unexpected tag: {xml_child.tag}')
                    continue
                if self.version >= 4.0:
                    argument = self._parse_operation_argument_v4(xml_child, operation)
                else:
                    argument = self._parse_operation_argument_v3(xml_child, operation)
                if argument is not None:
                    operation.arguments.append(argument)
                    argument.parent = operation
        if xml_possible_error_refs is not None:
            for xml_child in xml_possible_error_refs.findall('./*'):
                if xml_child.tag != 'POSSIBLE-ERROR-REF':
                    self._logger.error(f'Unexpected tag: {xml_child.tag}')
                    continue
                operation.error_refs.append(self.parse_text_node(xml_child))
        return operation

    def _parse_operation_argument_v3(self, xml_argument: Element, parent: ArObject) -> Argument | None:
        name = None
        type_ref = None
        direction = None
        for xml_elem in xml_argument.findall('./*'):
            if xml_elem.tag == 'SHORT-NAME':
                name = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'TYPE-TREF':
                type_ref = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'DIRECTION':
                direction = self.parse_text_node(xml_elem)
            else:
                self._logger.warning(f'Unexpected tag: {xml_elem.tag}')
        if name is None or type_ref is None or direction is None:
            self._logger.error('SHORT-NAME, TYPE-TREF and DIRECTION must have valid values')
        return Argument(name, type_ref, direction, parent=parent)

    def _parse_operation_argument_v4(self, xml_argument: Element, parent: ArObject) -> Argument | None:
        type_ref = None
        direction = None
        props_variants = None
        server_argument_impl_policy = None
        self.push()
        for xml_elem in xml_argument.findall('./*'):
            if xml_elem.tag == 'TYPE-TREF':
                type_ref = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'DIRECTION':
                direction = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'SW-DATA-DEF-PROPS':
                props_variants = self.parse_sw_data_def_props(xml_elem)
            elif xml_elem.tag == 'SERVER-ARGUMENT-IMPL-POLICY':
                server_argument_impl_policy = self.parse_text_node(xml_elem)
            else:
                self.base_handler(xml_elem)
        if self.name is None or type_ref is None or direction is None:
            self._logger.error('SHORT-NAME, TYPE-TREF and DIRECTION must have valid values')
            self.pop()
            return None
        argument = Argument(self.name, type_ref, direction, server_argument_impl_policy=server_argument_impl_policy, parent=parent)
        if props_variants is not None:
            argument.sw_calibration_access = props_variants[0].sw_calibration_access
        self.pop(argument)
        return argument

    def _parse_application_error(self, xml_elem: Element, parent: ArObject) -> ApplicationError:
        name = self.parse_text_node(xml_elem.find("./SHORT-NAME"))
        error_code = self.parse_int_node(xml_elem.find("./ERROR-CODE"))
        return ApplicationError(name, error_code, parent)

    def _parse_parameter_data_prototype(self, xml_elem: Element, parent: ArObject) -> ParameterDataPrototype | None:
        name = None
        admin_data = None
        type_ref = None
        props_variants = None
        for xml_elem in xml_elem.findall('./*'):
            if xml_elem.tag == 'SHORT-NAME':
                name = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'ADMIN-DATA':
                admin_data = self.parse_admin_data_node(xml_elem)
            elif xml_elem.tag == 'SW-DATA-DEF-PROPS':
                props_variants = self.parse_sw_data_def_props(xml_elem)
            elif xml_elem.tag == 'TYPE-TREF':
                type_ref = self.parse_text_node(xml_elem)
            else:
                self._logger.warning(f'Unexpected tag: {xml_elem.tag}')
        if name is None or type_ref is None:
            return None
        parameter = ParameterDataPrototype(name, type_ref, parent=parent, admin_data=admin_data)
        if props_variants is not None:
            parameter.sw_calibration_access = props_variants[0].sw_calibration_access
            parameter.sw_address_method_ref = props_variants[0].sw_address_method_ref
        return parameter

    def parse_nv_data_interface(self, xml_root: Element, parent: ArObject | None = None) -> NvDataInterface | None:
        assert (xml_root.tag == 'NV-DATA-INTERFACE')
        is_service = False
        service_kind = None
        nv_datas = None
        self.push()
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'IS-SERVICE':
                is_service = self.parse_boolean_node(xml_elem)
            elif xml_elem.tag == 'SERVICE-KIND' and self.version >= 4.0:
                service_kind = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'NV-DATAS':
                nv_datas = self._parse_data_elements(xml_elem)
            else:
                self.default_handler(xml_elem)
        if self.name is None:
            self.pop()
            return None
        nv_data_interface = NvDataInterface(self.name, is_service, service_kind, parent=parent, admin_data=self.admin_data)
        if nv_datas is not None:
            for nv_data in nv_datas:
                nv_data.parent = nv_data_interface
                nv_data_interface.nv_data.append(nv_data)
        self.pop(nv_data_interface)
        return nv_data_interface

    def parse_trigger_interface(self, xml_root: Element, parent: ArObject | None = None) -> TriggerInterface | None:
        is_service = False
        triggers = None
        self.push()
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'IS-SERVICE':
                is_service = self.parse_boolean_node(xml_elem)
            elif xml_elem.tag == 'TRIGGERS' and self.version >= 4.0:
                triggers = self._parse_element_list(
                    xml_elem,
                    {'TRIGGER': self._parse_trigger},
                )
            else:
                self.default_handler(xml_elem)
        if self.name is None:
            self.pop()
            return None
        trigger_interface = TriggerInterface(
            name=self.name,
            is_service=is_service,
            triggers=triggers,
            parent=parent,
            admin_data=self.admin_data,
        )
        self.pop(trigger_interface)
        return trigger_interface

    def _parse_trigger(self, xml_elem: Element) -> Trigger:
        name = self.parse_text_node(xml_elem.find('SHORT-NAME'))
        policy = self.parse_text_node(xml_elem.find('SW-IMPL-POLICY'))
        admin_data = self.parse_admin_data_node(xml_elem.find('ADMIN-DATA'))
        trigger = Trigger(name=name, sw_impl_policy=policy, admin_data=admin_data)
        return trigger


class SoftwareAddressMethodParser(ElementParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_supported_tags(self):
        return ['SW-ADDR-METHOD']

    def parse_element(self, xml_element: Element, parent: ArObject | None = None) -> SoftwareAddressMethod | None:
        if xml_element.tag == 'SW-ADDR-METHOD':
            return self.parse_sw_addr_method(xml_element)
        return None

    @staticmethod
    def parse_sw_addr_method(xml_root, parent: ArObject | None = None) -> SoftwareAddressMethod:
        assert (xml_root.tag == 'SW-ADDR-METHOD')
        name = xml_root.find("./SHORT-NAME").text
        return SoftwareAddressMethod(name, parent)
