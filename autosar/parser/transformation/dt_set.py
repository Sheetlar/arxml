from xml.etree.ElementTree import Element

from autosar.model.compu import CompuScale
from autosar.model.enums import TransformerClassEnum, DataTransformationKindEnum
from autosar.model.transformation.sets import (
    BufferProperties,
    TransformationDescription,
    TransformationTechnology,
    DataTransformation,
    DataTransformationSet,
)
from autosar.parser.compu_parser import CompuParser
from autosar.parser.identifiable import IdentifiableParser
from autosar.parser.parser_base import handler, multiple_with_check, multiple, BasicParser
from autosar.parser.transformation.description import TransformationDescriptionParserSelector


class BufferPropertiesParser(BasicParser[BufferProperties]):
    _returned_type = BufferProperties

    @handler('HEADER-LENGTH', required=True)
    def _parse_header_length(self, xml_element: Element) -> int:
        if (length := self._parse_int_node(xml_element)) is None:
            raise ValueError
        return length

    @handler('IN-PLACE', required=True)
    def _parse_in_place(self, xml_element: Element) -> bool:
        if (ip := self._parse_boolean_node(xml_element)) is None:
            raise ValueError
        return ip

    @handler('BUFFER-COMPUTATION')
    def _parse_buffer_computation(self, xml_element: Element) -> CompuScale | None:
        parser = CompuParser()  # TODO: Temporary solution until new parser implemented
        return parser.parse_compu_scale(xml_element)


class TransformationTechnologyParser(IdentifiableParser[TransformationTechnology]):
    _returned_type = TransformationTechnology

    @handler('PROTOCOL', required=True)
    def _parse_protocol(self, xml_element: Element) -> str:
        if (ref := self._parse_text_node(xml_element)) is None:
            raise ValueError
        return ref

    @handler('VERSION', required=True)
    def _parse_version(self, xml_element: Element) -> str:
        if (ref := self._parse_text_node(xml_element)) is None:
            raise ValueError
        return ref

    @handler('TRANSFORMER-CLASS', required=True)
    def _parse_transformer_class(self, xml_element: Element) -> TransformerClassEnum:
        if (cls := self._parse_enum_node(xml_element, TransformerClassEnum)) is None:
            raise ValueError
        return cls

    @handler('BUFFER-PROPERTIES', required=True)
    def _parse_buffer_properties(self, xml_element: Element) -> BufferProperties:
        parser = BufferPropertiesParser()
        if (bp := parser.parse_element(xml_element)) is None:
            raise ValueError
        return bp

    @handler('HAS-INTERNAL-STATE')
    def _parse_has_internal_state(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)

    @handler('NEEDS-ORIGINAL-DATA')
    def _parse_needs_original_data(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)

    @handler('TRANSFORMATION-DESCRIPTIONS')
    @multiple
    def _parse_transformation_description(self, xml_element: Element) -> TransformationDescription | None:
        parser = TransformationDescriptionParserSelector(xml_element.tag)
        return parser.parse_element(xml_element)


class DataTransformationParser(IdentifiableParser[DataTransformation]):
    _returned_type = DataTransformation

    @handler('TRANSFORMER-CHAIN-REFS', required=True)
    @multiple_with_check
    def _parse_transformer_chain(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('EXECUTE-DESPITE-DATA-UNAVAILABILITY', required=True)
    def _parse_execute_despite_data_unavailability(self, xml_element: Element) -> bool:
        if (flag := self._parse_boolean_node(xml_element)) is None:
            raise ValueError
        return flag

    @handler('DATA-TRANSFORMATION-KIND')
    def _parse_data_transformation_kind(self, xml_element: Element) -> DataTransformationKindEnum | None:
        return self._parse_enum_node(xml_element, DataTransformationKindEnum)


class DataTransformationSetParser(IdentifiableParser[DataTransformationSet]):
    _returned_type = DataTransformationSet

    @handler('DATA-TRANSFORMATIONS')
    @multiple_with_check
    def _parse_data_transformation(self, xml_element: Element) -> DataTransformation | None:
        parser = DataTransformationParser()
        return parser.parse_element(xml_element)

    @handler('TRANSFORMATION-TECHNOLOGIES', 'TRANSFORMATION-TECHNOLOGYS')
    @multiple_with_check(expected_name='TRANSFORMATION-TECHNOLOGY')
    def _parse_transformation_technology(self, xml_element: Element) -> TransformationTechnology | None:
        parser = TransformationTechnologyParser()
        return parser.parse_element(xml_element)
