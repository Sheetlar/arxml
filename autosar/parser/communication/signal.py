from xml.etree.ElementTree import Element

from autosar.model.communication.signal import (
    SystemSignal,
    SystemSignalGroup,
    ISignal,
    ISignalGroup,
    ISignalProps,
)
from autosar.model.enums import DataTypePolicyEnum, ISignalTypeEnum, HandleOutOfRangeEnum
from autosar.model.sw_def_props import SwDataDefProps
from autosar.model.transformation.signal import TransformationISignalProps
from autosar.model.value_spec import ValueSpecification
from autosar.parser.identifiable import IdentifiableParser
from autosar.parser.parser_base import (
    handler,
    multiple_with_check,
    multiple,
    ref_variation,
    single_subclass_aggr,
    BasicParser,
)
from autosar.parser.sw_def_props import SwDataDefPropsParser
from autosar.parser.transformation.signal_props import TransformationISignalPropsParserSelector
from autosar.parser.value_spec_parser import ValueSpecificationParserSelector


class ISignalPropsParser(BasicParser[ISignalProps]):
    _returned_type = ISignalProps

    @handler('HANDLE-OUT-OF-RANGE')
    def _parse_handle_out_of_range(self, xml_element: Element) -> HandleOutOfRangeEnum | None:
        return self._parse_enum_node(xml_element, HandleOutOfRangeEnum)


class ISignalParser(IdentifiableParser[ISignal]):
    _returned_type = ISignal

    @handler('SYSTEM-SIGNAL-REF', required=True)
    def _parse_system_signal(self, xml_element: Element) -> str:
        if (ref := self._parse_text_node(xml_element)) is None:
            raise ValueError
        return ref

    @handler('LENGTH', required=True)
    def _parse_length(self, xml_element: Element) -> int:
        if (length := self._parse_int_node(xml_element)) is None:
            raise ValueError
        return length

    @handler('DATA-TYPE-POLICY', required=True)
    def _parse_data_type_policy(self, xml_element: Element) -> DataTypePolicyEnum:
        if (policy := self._parse_enum_node(xml_element, DataTypePolicyEnum)) is None:
            raise ValueError
        return policy

    @handler('I-SIGNAL-TYPE')
    def _parse_i_signal_type(self, xml_element: Element) -> ISignalTypeEnum | None:
        return self._parse_enum_node(xml_element, ISignalTypeEnum)

    @handler('I-SIGNAL-PROPS')
    def _parse_i_signal_props(self, xml_element: Element) -> ISignalProps | None:
        parser = ISignalPropsParser()
        return parser.parse_element(xml_element)

    @handler('DATA-TRANSFORMATIONS', param='data_transformation_refs')
    @ref_variation
    def _parse_data_transformation(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('INIT-VALUE')
    @single_subclass_aggr
    def _parse_init_value(self, xml_element: Element) -> ValueSpecification | None:
        parser = ValueSpecificationParserSelector(xml_element.tag)
        return parser.parse_element(xml_element)

    @handler('NETWORK-REPRESENTATION-PROPS')
    def _parse_network_representation_props(self, xml_element: Element) -> SwDataDefProps | None:
        parser = SwDataDefPropsParser()
        return parser.parse_element(xml_element)

    @handler('RECEPTION-DEFAULT-VALUES')
    @multiple
    def _parse_reception_default_value(self, xml_element: Element) -> ValueSpecification | None:
        parser = ValueSpecificationParserSelector(xml_element.tag)
        return parser.parse_element(xml_element)

    @handler('TIMEOUT-SUBSTITUTION-VALUE')
    @single_subclass_aggr
    def _parse_timeout_substitution_value(self, xml_element: Element) -> ValueSpecification | None:
        parser = ValueSpecificationParserSelector(xml_element.tag)
        return parser.parse_element(xml_element)

    @handler('TRANSFORMATION-I-SIGNAL-PROPSS', param='transformation_i_signal_props')
    @multiple
    def _parse_transformation_i_signal_props(self, xml_element: Element) -> TransformationISignalProps | None:
        parser = TransformationISignalPropsParserSelector(xml_element.tag)
        return parser.parse_element(xml_element)


class ISignalGroupParser(IdentifiableParser[ISignalGroup]):
    _returned_type = ISignalGroup

    @handler('SYSTEM-SIGNAL-GROUP-REF', required=True)
    def _parse_system_signal_group(self, xml_element: Element) -> str:
        if (ref := self._parse_text_node(xml_element)) is None:
            raise ValueError
        return ref

    @handler('I-SIGNAL-REFS')
    @multiple_with_check
    def _parse_i_signal(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('COM-BASED-SIGNAL-GROUP-TRANSFORMATIONS', param='com_based_sg_transform_refs')
    @ref_variation(element_name='DATA-TRANSFORMATION')
    def _parse_com_based_signal_group_transformation(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('TRANSFORMATION-I-SIGNAL-PROPSS', param='transformation_i_signal_props')
    @multiple
    def _parse_transformation_i_signal_props(self, xml_element: Element) -> TransformationISignalProps | None:
        parser = TransformationISignalPropsParserSelector(xml_element.tag)
        return parser.parse_element(xml_element)


class SystemSignalParser(IdentifiableParser[SystemSignal]):
    _returned_type = SystemSignal

    @handler('DYNAMIC-LENGTH')
    def _parse_dynamic_length(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)

    @handler('PHYSICAL-PROPS')
    def _parse_physical_props(self, xml_element: Element) -> SwDataDefProps | None:
        parser = SwDataDefPropsParser()
        return parser.parse_element(xml_element)


class SystemSignalGroupParser(IdentifiableParser[SystemSignalGroup]):
    _returned_type = SystemSignalGroup

    @handler('SYSTEM-SIGNAL-REFS')
    @multiple_with_check
    def _parse_system_signal(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('TRANSFORMING-SYSTEM-SIGNAL-REF')
    def _parse_transforming_system_signal(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)
