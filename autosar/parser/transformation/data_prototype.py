from xml.etree.ElementTree import Element

from autosar.model.instance_ref import (
    DataPrototypeInClientServerInterfaceInstanceRef,
    DataPrototypeInSenderReceiverInterfaceInstanceRef,
)
from autosar.model.sw_def_props import SwDataDefProps
from autosar.model.transformation.signal import (
    DataPrototypeReference,
    DataPrototypeInPortInterfaceRef,
    ImplementationDataTypeElementInPortInterfaceRef,
    DataPrototypeTransformationPropsIdent,
    DataPrototypeTransformationProps,
)
from autosar.parser.identifiable import IdentifiableParser
from autosar.parser.instance_ref_parser import (
    DataPrototypeInClientServerInterfaceInstRefParser,
    DataPrototypeInSenderReceiverInterfaceInstRefParser,
)
from autosar.parser.parser_base import (
    handler,
    multiple_with_check,
    single_subclass_aggr,
    BasicParser,
    ParserSelector,
)
from autosar.parser.sw_def_props import SwDataDefPropsParser


class DataPrototypeInPortInterfaceRefParser(
    BasicParser[DataPrototypeInPortInterfaceRef]
):
    _returned_type = DataPrototypeInPortInterfaceRef

    @handler(
        'DATA-PROTOTYPE-IN-CLIENT-SERVER-INTERFACE-IREF',
        param='data_prototype_in_client_server_interface',
    )
    def _parse_data_prototype_in_client_server_interface(
            self,
            xml_element: Element,
    ) -> DataPrototypeInClientServerInterfaceInstanceRef | None:
        parser = DataPrototypeInClientServerInterfaceInstRefParser()
        return parser.parse_element(xml_element)

    @handler(
        'DATA-PROTOTYPE-IN-SENDER-RECEIVER-INTERFACE-IREF',
        param='data_prototype_in_sender_receiver_interface',
    )
    def _parse_data_prototype_in_sender_receiver_interface(
            self,
            xml_element: Element,
    ) -> DataPrototypeInSenderReceiverInterfaceInstanceRef | None:
        parser = DataPrototypeInSenderReceiverInterfaceInstRefParser()
        return parser.parse_element(xml_element)


class ImplementationDataTypeElementInPortInterfaceRefParser(
    BasicParser[ImplementationDataTypeElementInPortInterfaceRef]
):
    _returned_type = ImplementationDataTypeElementInPortInterfaceRef

    @handler('ROOT-DATA-PROTOTYPE-REF')
    def _parse_root_data_prototype_ref(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('CONTEXT-IMPLEMENTATION-DATA-ELEMENT-REFS')
    @multiple_with_check
    def _parse_context_implementation_data_element(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('TARGET-IMPLEMENTATION-DATA-TYPE-ELEMENT-REF')
    def _parse_target_implementation_data_type_element_ref(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)


class DataPrototypeReferenceParserSelector(ParserSelector[DataPrototypeReference]):
    _tag_map = {
        'DATA-PROTOTYPE-IN-PORT-INTERFACE-REF': DataPrototypeInPortInterfaceRefParser,
        'IMPLEMENTATION-DATA-TYPE-ELEMENT-IN-PORT-INTERFACE-REF': ImplementationDataTypeElementInPortInterfaceRefParser,
    }


class DataPrototypeTransformationPropsIdentParser(
    IdentifiableParser[DataPrototypeTransformationPropsIdent]
):
    _returned_type = DataPrototypeTransformationPropsIdent


class DataPrototypeTransformationPropsParser(
    BasicParser[DataPrototypeTransformationProps]
):
    _returned_type = DataPrototypeTransformationProps

    @handler('DATA-PROTOTYPE-IN-PORT-INTERFACE-REF')
    @single_subclass_aggr
    def _parse_data_prototype_in_port_interface_ref(
            self,
            xml_element: Element,
    ) -> DataPrototypeReference | None:
        parser = DataPrototypeReferenceParserSelector(xml_element.tag)
        return parser.parse_element(xml_element)

    @handler('NETWORK-REPRESENTATION-PROPS')
    def _parse_network_representation_props(self, xml_element: Element) -> SwDataDefProps | None:
        parser = SwDataDefPropsParser()
        return parser.parse_element(xml_element)

    @handler('TRANSFORMATION-PROPS-REF')
    def _parse_transformation_props_ref(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('IDENT')
    def _parse_ident(self, xml_element: Element) -> DataPrototypeTransformationPropsIdent | None:
        parser = DataPrototypeTransformationPropsIdentParser()
        return parser.parse_element(xml_element)
