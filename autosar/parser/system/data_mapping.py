from typing import TypeVar
from xml.etree.ElementTree import Element

from autosar.model.system import (
    DataMapping,
    ClientServerToSignalMapping,
    SenderReceiverCompositeElementToSignalMapping,
    SenderReceiverToSignalGroupMapping,
    SenderReceiverToSignalMapping,
    TriggerToSignalMapping,
    AnySenderRecCompositeTypeMapping,
    TextTableMapping,
)
from autosar.model.instance_ref import (
    OperationInSystemInstanceRef,
    VariableDataPrototypeInSystemInstanceRef,
    TriggerInSystemInstanceRef,
)
from autosar.parser.instance_ref_parser import (
    OperationInSystemInstRefParser,
    VariableDataPrototypeInSystemInstRefParser,
    TriggerInSystemInstRefParser,
)
from autosar.parser.parser_base import (
    handler,
    not_implemented_handler,
    single_subclass_aggr,
    BasicParser,
    ParserSelector,
)
from autosar.parser.system.type_mapping import SenderRecCompositeTypeMappingParserSelector, TextTableMappingParser

DM = TypeVar('DM', bound=DataMapping)


class DataMappingParser(BasicParser[DM]):
    @not_implemented_handler('INTRODUCTION')
    def _parse_introduction(self, xml_element: Element):
        ...


class ClientServerToSignalMappingParser(DataMappingParser[ClientServerToSignalMapping]):
    _returned_type = ClientServerToSignalMapping

    @handler('CALL-SIGNAL-REF', required=True)
    def _parse_call_signal(self, xml_element: Element) -> str:
        ref = self._parse_text_node(xml_element)
        if ref is None:
            raise ValueError
        return ref

    @handler('CLIENT-SERVER-OPERATION-IREF', param='client_server_operation_instance_ref', required=True)
    def _parse_client_server_operation(self, xml_element: Element) -> OperationInSystemInstanceRef:
        parser = OperationInSystemInstRefParser()
        inst_ref = parser.parse_element(xml_element)
        if inst_ref is None:
            raise ValueError
        return inst_ref

    @handler('RETURN-SIGNAL-REF', required=True)
    def _parse_return_signal(self, xml_element: Element) -> str:
        ref = self._parse_text_node(xml_element)
        if ref is None:
            raise ValueError
        return ref


class SenderReceiverCompositeElementToSignalMappingParser(DataMappingParser[SenderReceiverCompositeElementToSignalMapping]):
    _returned_type = SenderReceiverCompositeElementToSignalMapping

    @handler('SYSTEM-SIGNAL-REF', required=True)
    def _parse_system_signal(self, xml_element: Element) -> str:
        ref = self._parse_text_node(xml_element)
        if ref is None:
            raise ValueError
        return ref

    @handler('TYPE-MAPPING', required=True)
    @single_subclass_aggr
    def _parse_type_mapping(self, xml_element: Element) -> AnySenderRecCompositeTypeMapping:
        parser = SenderRecCompositeTypeMappingParserSelector(xml_element.tag)
        mapping = parser.parse_element(xml_element)
        if mapping is None:
            raise ValueError
        return mapping

    @handler('DATA-ELEMENT-IREF', param='data_element_instance_ref')
    def _parse_data_element(self, xml_element: Element) -> VariableDataPrototypeInSystemInstanceRef | None:
        parser = VariableDataPrototypeInSystemInstRefParser()
        return parser.parse_element(xml_element)


class SenderReceiverToSignalGroupMappingParser(DataMappingParser[SenderReceiverToSignalGroupMapping]):
    _returned_type = SenderReceiverToSignalGroupMapping

    @handler('SIGNAL-GROUP-REF', required=True)
    def _parse_signal_group(self, xml_element: Element) -> str:
        ref = self._parse_text_node(xml_element)
        if ref is None:
            raise ValueError
        return ref

    @handler('TYPE-MAPPING', required=True)
    @single_subclass_aggr
    def _parse_type_mapping(self, xml_element: Element) -> AnySenderRecCompositeTypeMapping:
        parser = SenderRecCompositeTypeMappingParserSelector(xml_element.tag)
        mapping = parser.parse_element(xml_element)
        if mapping is None:
            raise ValueError
        return mapping

    @handler('DATA-ELEMENT-IREF', param='data_element_instance_ref', required=True)
    def _parse_data_element(self, xml_element: Element) -> VariableDataPrototypeInSystemInstanceRef:
        parser = VariableDataPrototypeInSystemInstRefParser()
        inst_ref = parser.parse_element(xml_element)
        if inst_ref is None:
            raise ValueError
        return inst_ref


class SenderReceiverToSignalMappingParser(DataMappingParser[SenderReceiverToSignalMapping]):
    _returned_type = SenderReceiverToSignalMapping

    @handler('SYSTEM-SIGNAL-REF', required=True)
    def _parse_system_signal(self, xml_element: Element) -> str:
        ref = self._parse_text_node(xml_element)
        if ref is None:
            raise ValueError
        return ref

    @handler('DATA-ELEMENT-IREF', param='data_element_instance_ref', required=True)
    def _parse_data_element(self, xml_element: Element) -> VariableDataPrototypeInSystemInstanceRef:
        parser = VariableDataPrototypeInSystemInstRefParser()
        inst_ref = parser.parse_element(xml_element)
        if inst_ref is None:
            raise ValueError
        return inst_ref

    @handler('SENDER-TO-SIGNAL-TEXT-TABLE-MAPPING')
    def _parse_sender_to_signal_text_table_mapping(self, xml_element: Element) -> TextTableMapping | None:
        parser = TextTableMappingParser()
        return parser.parse_element(xml_element)

    @handler('SIGNAL-TO-RECEIVER-TEXT-TABLE-MAPPING')
    def _parse_signal_to_receiver_text_table_mapping(self, xml_element: Element) -> TextTableMapping | None:
        parser = TextTableMappingParser()
        return parser.parse_element(xml_element)


class TriggerToSignalMappingParser(DataMappingParser[TriggerToSignalMapping]):
    _returned_type = TriggerToSignalMapping

    @handler('SYSTEM-SIGNAL-REF', required=True)
    def _parse_system_signal(self, xml_element: Element) -> str:
        ref = self._parse_text_node(xml_element)
        if ref is None:
            raise ValueError
        return ref

    @handler('TRIGGER-IREF', param='trigger_instance_ref', required=True)
    def _parse_data_element(self, xml_element: Element) -> TriggerInSystemInstanceRef:
        parser = TriggerInSystemInstRefParser()
        inst_ref = parser.parse_element(xml_element)
        if inst_ref is None:
            raise ValueError
        return inst_ref


class DataMappingParserSelector(ParserSelector[DM]):
    _tag_map = {
        'CLIENT-SERVER-TO-SIGNAL-MAPPING': ClientServerToSignalMappingParser,
        'SENDER-RECEIVER-COMPOSITE-ELEMENT-TO-SIGNAL-MAPPING': SenderReceiverCompositeElementToSignalMappingParser,
        'SENDER-RECEIVER-TO-SIGNAL-GROUP-MAPPING': SenderReceiverToSignalGroupMappingParser,
        'SENDER-RECEIVER-TO-SIGNAL-MAPPING': SenderReceiverToSignalMappingParser,
        'TRIGGER-TO-SIGNAL-MAPPING': TriggerToSignalMappingParser,
    }
