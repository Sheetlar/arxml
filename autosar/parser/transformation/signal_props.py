from typing import TypeVar
from xml.etree.ElementTree import Element

from autosar.model.enums import (
    CSTransformerErrorReactionEnum,
    SomeIpMessageTypeEnum,
    SomeIpTransformerSessionHandlingEnum,
)
from autosar.model.transformation.dds_user_def import (
    DdsTransformationISignalPropsContent,
    DdsTransformationISignalProps,
    UserDefinedTransformationISignalPropsContent,
    UserDefinedTransformationISignalProps,
)
from autosar.model.transformation.e2e import (
    EndToEndTransformationISignalPropsContent,
    EndToEndTransformationISignalProps,
)
from autosar.model.transformation.signal import (
    DataPrototypeTransformationProps,
    TransformationISignalPropsIdent,
    TransformationISignalPropsContent,
    AbstractTransformationISignalProps,
)
from autosar.model.transformation.some_ip import (
    SomeIpTransformationISignalPropsContent,
    SomeIpTransformationISignalProps,
)
from autosar.parser.identifiable import IdentifiableParser, DescribableParser
from autosar.parser.parser_base import (
    handler,
    multiple_with_check,
    BasicParser,
    ParserSelector,
    PropertySetParser,
)
from autosar.parser.transformation.data_prototype import DataPrototypeTransformationPropsParser

TP = TypeVar('TP', bound=AbstractTransformationISignalProps)
TPC = TypeVar('TPC', bound=TransformationISignalPropsContent)


class TransformationISignalPropsIdentParser(
    IdentifiableParser[TransformationISignalPropsIdent]
):
    _returned_type = TransformationISignalPropsIdent


class TransformationISignalPropsContentParser(BasicParser[TPC]):
    @handler('TRANSFORMER-REF')
    def _parse_transformer(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('CS-ERROR-REACTION')
    def _parse_cs_error_reaction(self, xml_element: Element) -> CSTransformerErrorReactionEnum | None:
        return self._parse_enum_node(xml_element, CSTransformerErrorReactionEnum)

    @handler('DATA-PROTOTYPE-TRANSFORMATION-PROPSS', param='data_prototype_transformation_props')
    @multiple_with_check
    def _parse_data_prototype_props(self, xml_element: Element) -> DataPrototypeTransformationProps | None:
        parser = DataPrototypeTransformationPropsParser()
        return parser.parse_element(xml_element)

    @handler('IDENT')
    def _parse_ident(self, xml_element: Element) -> TransformationISignalPropsIdent | None:
        parser = TransformationISignalPropsIdentParser()
        return parser.parse_element(xml_element)


class DdsTransformationISignalPropsContentParser(
    TransformationISignalPropsContentParser[DdsTransformationISignalPropsContent]
):
    _returned_type = DdsTransformationISignalPropsContent


class EndToEndTransformationISignalPropsContentParser(
    TransformationISignalPropsContentParser[EndToEndTransformationISignalPropsContent]
):
    _returned_type = EndToEndTransformationISignalPropsContent

    @handler('DATA-IDS')
    @multiple_with_check
    def _parse_data_id(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('DATA-LENGTH')
    def _parse_data_length(self, xml_element: Element) -> int:
        return self._parse_int_node(xml_element) or 0

    @handler('MAX-DATA-LENGTH')
    def _parse_max_data_length(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('MIN-DATA-LENGTH')
    def _parse_min_data_length(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('SOURCE-ID')
    def _parse_source_id(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)


class SomeIpTransformationISignalPropsContentParser(
    TransformationISignalPropsContentParser[SomeIpTransformationISignalPropsContent]
):
    _returned_type = SomeIpTransformationISignalPropsContent

    @handler('MESSAGE-TYPE')
    def _parse_message_type(self, xml_element: Element) -> SomeIpMessageTypeEnum | None:
        return self._parse_enum_node(xml_element, SomeIpMessageTypeEnum)

    @handler('INTERFACE-VERSION')
    def _parse_interface_version(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('IS-DYNAMIC-LENGTH-FIELD-SIZE')
    def _parse_is_dynamic_length_field_size(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)

    @handler('SESSION-HANDLING-SR')
    def _parse_session_handling_sr(self, xml_element: Element) -> SomeIpTransformerSessionHandlingEnum | None:
        return self._parse_enum_node(xml_element, SomeIpTransformerSessionHandlingEnum)

    @handler('SIZE-OF-ARRAY-LENGTH-FIELDS')
    def _parse_size_of_array_length_fields(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('SIZE-OF-STRING-LENGTH-FIELDS')
    def _parse_size_of_string_length_fields(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('SIZE-OF-STRUCT-LENGTH-FIELDS')
    def _parse_size_of_struct_length_fields(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('SIZE-OF-UNION-LENGTH-FIELDS')
    def _parse_size_of_union_length_fields(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('TLV-DATA-ID-DEFINITION-REFS')
    @multiple_with_check
    def _parse_tlv_data_id_definition(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('IMPLEMENTS-LEGACY-STRING-SERIALIZATION', 'IMPLEMENTS-SOMEIP-STRING-HANDLING')
    def _parse_implements_legacy_string_serialization(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)


class UserDefinedTransformationISignalPropsContentParser(
    TransformationISignalPropsContentParser[UserDefinedTransformationISignalPropsContent]
):
    _returned_type = UserDefinedTransformationISignalPropsContent


class TransformationISignalPropsParser(DescribableParser[TP], PropertySetParser[TP, TPC]):
    """Abstract"""


class DdsTransformationISignalPropsParser(
    TransformationISignalPropsParser[
        DdsTransformationISignalProps,
        DdsTransformationISignalPropsContent,
    ]
):
    _returned_type = DdsTransformationISignalProps
    _variant_parser_type = DdsTransformationISignalPropsContentParser
    _tag = 'DDS-TRANSFORMATION-I-SIGNAL-PROPS'


class EndToEndTransformationISignalPropsParser(
    TransformationISignalPropsParser[
        EndToEndTransformationISignalProps,
        EndToEndTransformationISignalPropsContent,
    ]
):
    _returned_type = EndToEndTransformationISignalProps
    _variant_parser_type = EndToEndTransformationISignalPropsContentParser
    _tag = 'END-TO-END-TRANSFORMATION-I-SIGNAL-PROPS'


class SomeIpTransformationISignalPropsParser(
    TransformationISignalPropsParser[
        SomeIpTransformationISignalProps,
        SomeIpTransformationISignalPropsContent,
    ]
):
    _returned_type = SomeIpTransformationISignalProps
    _variant_parser_type = SomeIpTransformationISignalPropsContentParser
    _tag = 'SOMEIP-TRANSFORMATION-I-SIGNAL-PROPS'


class UserDefinedTransformationISignalPropsParser(
    TransformationISignalPropsParser[
        UserDefinedTransformationISignalProps,
        UserDefinedTransformationISignalPropsContent,
    ]
):
    _returned_type = UserDefinedTransformationISignalProps
    _variant_parser_type = UserDefinedTransformationISignalPropsContentParser
    _tag = 'USER-DEFINED-TRANSFORMATION-I-SIGNAL-PROPS'


class TransformationISignalPropsParserSelector(ParserSelector[TP]):
    _tag_map = {
        'DDS-TRANSFORMATION-I-SIGNAL-PROPS': DdsTransformationISignalPropsParser,
        'END-TO-END-TRANSFORMATION-I-SIGNAL-PROPS': EndToEndTransformationISignalPropsParser,
        'SOMEIP-TRANSFORMATION-I-SIGNAL-PROPS': SomeIpTransformationISignalPropsParser,
        'USER-DEFINED-TRANSFORMATION-I-SIGNAL-PROPS': UserDefinedTransformationISignalPropsParser,
    }
