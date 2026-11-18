from xml.etree.ElementTree import Element

from autosar.model.transformation.dds_user_def import UserDefinedTransformationProps
from autosar.model.transformation.sets import TransformationProps, TransformationPropsSet
from autosar.model.transformation.some_ip import SomeIpTransformationProps
from autosar.parser.identifiable import IdentifiableParser
from autosar.parser.parser_base import handler, multiple, ParserSelector


class SomeIpTransformationPropsParser(
    IdentifiableParser[SomeIpTransformationProps]
):
    _returned_type = SomeIpTransformationProps

    @handler('ALIGNMENT')
    def _parse_alignment(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('SIZE-OF-ARRAY-LENGTH-FIELD')
    def _parse_size_of_array_length_field(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('SIZE-OF-STRING-LENGTH-FIELD')
    def _parse_size_of_string_length_field(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('SIZE-OF-STRUCT-LENGTH-FIELD')
    def _parse_size_of_struct_length_field(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('SIZE-OF-UNION-LENGTH-FIELD')
    def _parse_size_of_union_length_field(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)


class UserDefinedTransformationPropsParser(
    IdentifiableParser[UserDefinedTransformationProps]
):
    _returned_type = UserDefinedTransformationProps


class TransformationPropsParserSelector(ParserSelector[TransformationProps]):
    _tag_map = {
        'SOMEIP-TRANSFORMATION-PROPS': SomeIpTransformationPropsParser,
        'USER-DEFINED-TRANSFORMATION-PROPS': UserDefinedTransformationPropsParser,
    }


class TransformationPropsSetParser(IdentifiableParser[TransformationPropsSet]):
    _returned_type = TransformationPropsSet

    @handler('TRANSFORMATION-PROPSS', param='transformation_props')
    @multiple
    def _parse_transformation_props(self, xml_element: Element) -> TransformationProps | None:
        parser = TransformationPropsParserSelector(xml_element.tag)
        return parser.parse_element(xml_element)
