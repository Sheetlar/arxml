from xml.etree.ElementTree import Element

from autosar.model.sw_def_props import SwDataDefProps, SwDataDefPropsContent, SwPointerTargetProps
from autosar.parser.parser_base import (
    handler,
    not_implemented_handler,
    BasicParser,
    PropertySetParser,
)


class SwPointerTargetPropsParser(BasicParser[SwPointerTargetProps]):
    _returned_type = SwPointerTargetProps

    @handler('TARGET-CATEGORY')
    def _parse_target_category(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('SW-DATA-DEF-PROPS')
    def _parse_sw_data_def_props(self, xml_element: Element) -> SwDataDefProps | None:
        parser = SwDataDefPropsParser()
        return parser.parse_element(xml_element)

    @handler('FUNCTION-POINTER-SIGNATURE-REF')
    def _parse_function_pointer_signature(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)


class SwDataDefPropsContentParser(BasicParser[SwDataDefPropsContent]):
    _returned_type = SwDataDefPropsContent

    @handler('BASE-TYPE-REF')
    def _parse_base_type(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('IMPLEMENTATION-TYPE-REF')
    def _parse_implementation_type(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('SW-ADDRESS-METHOD-REF')
    def _parse_sw_address_method(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @not_implemented_handler('SW-CALIBRATION-ACCESS')
    def _parse_sw_calibration_access(self, xml_element: Element):  # -> SwCalibrationAccessEnum | None:
        return  # self._parse_enum_node(xml_element, SwCalibrationAccessEnum)

    @not_implemented_handler('SW-IMPL-POLICY')
    def _parse_sw_impl_policy(self, xml_element: Element):  # -> SwImplPolicyEnum | None:
        return  # self._parse_enum_node(xml_element, SwImplPolicyEnum)

    @handler('SW-POINTER-TARGET-PROPS')
    def _parse_sw_pointer_target_props(self, xml_element: Element) -> SwPointerTargetProps | None:
        parser = SwPointerTargetPropsParser()
        return parser.parse_element(xml_element)

    @handler('SW-RECORD-LAYOUT-REF')
    def _parse_sw_record_layout(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('COMPU-METHOD-REF')
    def _parse_compu_method(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('DATA-CONSTRAINT-REF')
    def _parse_data_constraint(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('UNIT-REF')
    def _parse_unit(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)


class SwDataDefPropsParser(PropertySetParser[SwDataDefProps, SwDataDefPropsContent]):
    _returned_type = SwDataDefProps
    _variant_parser_type = SwDataDefPropsContentParser
    _tag = 'SW-DATA-DEF-PROPS'
