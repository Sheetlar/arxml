from xml.etree.ElementTree import Element

from autosar.model.enums import ByteOrderEnum, DataIdModeEnum, EndToEndProfileBehaviorEnum
from autosar.model.transformation.dds_user_def import (
    DdsTransformationDescription,
    UserDefinedTransformationDescription,
)
from autosar.model.transformation.e2e import EndToEndTransformationDescription
from autosar.model.transformation.sets import TransformationDescription
from autosar.model.transformation.some_ip import SomeIpTransformationDescription
from autosar.parser.identifiable import DescribableParser
from autosar.parser.parser_base import handler, ParserSelector


class DdsTransformationDescriptionParser(
    DescribableParser[DdsTransformationDescription]
):
    _returned_type = DdsTransformationDescription


class EndToEndTransformationDescriptionParser(
    DescribableParser[EndToEndTransformationDescription]
):
    _returned_type = EndToEndTransformationDescription

    @handler('PROFILE-NAME', required=True)
    def _parse_profile_name(self, xml_element: Element) -> str:
        if (name := self._parse_text_node(xml_element)) is None:
            raise ValueError
        return name

    @handler('DATA-ID-MODE')
    def _parse_data_id_mode(self, xml_element: Element) -> DataIdModeEnum | None:
        return self._parse_enum_node(xml_element, DataIdModeEnum)

    @handler('COUNTER-OFFSET')
    def _parse_counter_offset(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('CRC-OFFSET')
    def _parse_crc_offset(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('DATA-ID-NIBBLE-OFFSET')
    def _parse_data_id_nibble_offset(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('OFFSET')
    def _parse_offset(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('CLEAR-FROM-VALID-TO-INVALID')
    def _parse_clear_from_valid_to_invalid(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)

    @handler('E-2-E-PROFILE-COMPATIBILITY-PROPS-REF', param='e2e_profile_compatibility_props_ref')
    def _parse_e2e_profile_compatibility_props(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('MAX-DELTA-COUNTER')
    def _parse_max_delta_counter(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('MAX-ERROR-STATE-INIT')
    def _parse_max_error_state_init(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('MAX-ERROR-STATE-INVALID')
    def _parse_max_error_state_invalid(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('MAX-ERROR-STATE-VALID')
    def _parse_max_error_state_valid(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('MAX-NO-NEW-OR-REPEATED-DATA')
    def _parse_max_no_new_or_repeated_data(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('MIN-OK-STATE-INIT')
    def _parse_min_ok_state_init(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('MIN-OK-STATE-INVALID')
    def _parse_min_ok_state_invalid(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('MIN-OK-STATE-VALID')
    def _parse_min_ok_state_valid(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('PROFILE-BEHAVIOR')
    def _parse_profile_behavior(self, xml_element: Element) -> EndToEndProfileBehaviorEnum | None:
        return self._parse_enum_node(xml_element, EndToEndProfileBehaviorEnum)

    @handler('SYNC-COUNTER-INIT')
    def _parse_sync_counter_init(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('UPPER-HEADER-BITS-TO-SHIFT')
    def _parse_upper_header_bits_to_shift(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('WINDOW-SIZE-INIT')
    def _parse_window_size_init(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('WINDOW-SIZE-INVALID')
    def _parse_window_size_invalid(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('WINDOW-SIZE-VALID')
    def _parse_window_size_valid(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)


class SomeIpTransformationDescriptionParser(
    DescribableParser[SomeIpTransformationDescription]
):
    _returned_type = SomeIpTransformationDescription

    @handler('INTERFACE-VERSION', required=True)
    def _parse_interface_version(self, xml_element: Element) -> int:
        if (ver := self._parse_int_node(xml_element)) is None:
            raise ValueError
        return ver

    @handler('BYTE-ORDER')
    def _parse_byte_order(self, xml_element: Element) -> ByteOrderEnum | None:
        return self._parse_enum_node(xml_element, ByteOrderEnum)

    @handler('ALIGNMENT')
    def _parse_alignment(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)


class UserDefinedTransformationDescriptionParser(
    DescribableParser[UserDefinedTransformationDescription]
):
    _returned_type = UserDefinedTransformationDescription


class TransformationDescriptionParserSelector(ParserSelector[TransformationDescription]):
    _tag_map = {
        'DDS-TRANSFORMATION-DESCRIPTION': DdsTransformationDescriptionParser,
        'END-TO-END-TRANSFORMATION-DESCRIPTION': EndToEndTransformationDescriptionParser,
        'SOMEIP-TRANSFORMATION-DESCRIPTION': SomeIpTransformationDescriptionParser,
        'USER-DEFINED-TRANSFORMATION-DESCRIPTION': UserDefinedTransformationDescriptionParser,
    }
