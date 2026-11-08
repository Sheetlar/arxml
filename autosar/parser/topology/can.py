from typing import TypeVar
from xml.etree.ElementTree import Element

from autosar.model.topology.can import (
    AbstractCanCommunicationControllerAttributes,
    CanControllerConfiguration,
    CanControllerConfigurationRequirements,
    CanControllerFdConfiguration,
    CanControllerFdConfigurationRequirements,
    CanControllerXlConfiguration,
    CanControllerXlConfigurationRequirements,
)
from autosar.parser.parser_base import (
    handler,
    BasicParserWithoutParent,
    ParserSelector,
)

A = TypeVar('A', bound=AbstractCanCommunicationControllerAttributes)


class CanControllerFdConfigurationParser(
    BasicParserWithoutParent[CanControllerFdConfiguration]
):
    _returned_type = CanControllerFdConfiguration

    @handler('TX-BIT-RATE-SWITCH')
    def _parse_tx_bit_rate_switch(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)

    @handler('PADDING-VALUE')
    def _parse_padding_value(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('PROP-SEG')
    def _parse_prop_seg(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('SYNC-JUMP-WIDTH')
    def _parse_sync_jump_width(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('TIME-SEG-1')
    def _parse_time_seg_1(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('TIME-SEG-2')
    def _parse_time_seg_2(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('SSP-OFFSET')
    def _parse_ssp_offset(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)


class CanControllerFdConfigurationRequirementsParser(
    BasicParserWithoutParent[CanControllerFdConfigurationRequirements]
):
    _returned_type = CanControllerFdConfigurationRequirements

    @handler('TX-BIT-RATE-SWITCH')
    def _parse_tx_bit_rate_switch(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)

    @handler('PADDING-VALUE')
    def _parse_padding_value(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('MAX-SYNC-JUMP-WIDTH')
    def _parse_max_sync_jump_width(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('MIN-SYNC-JUMP-WIDTH')
    def _parse_min_sync_jump_width(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('MAX-SAMPLE-POINT')
    def _parse_max_sample_point(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('MIN-SAMPLE-POINT')
    def _parse_min_sample_point(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('MAX-NUMBER-OF-TIME-QUANTA-PER-BIT')
    def _parse_max_number_of_time_quanta_per_bit(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('MIN-NUMBER-OF-TIME-QUANTA-PER-BIT')
    def _parse_min_number_of_time_quanta_per_bit(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('MAX-TRCV-DELAY-COMPENSATION-OFFSET')
    def _parse_max_trcv_delay_compensation_offset(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('MIN-TRCV-DELAY-COMPENSATION-OFFSET')
    def _parse_min_trcv_delay_compensation_offset(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)


class CanControllerXlConfigurationParser(
    BasicParserWithoutParent[CanControllerXlConfiguration]
):
    _returned_type = CanControllerXlConfiguration

    @handler('ERROR-SIGNALING-ENABLED', required=True)
    def _parse_error_signaling_enabled(self, xml_element: Element) -> bool:
        if (flag := self._parse_boolean_node(xml_element)) is None:
            raise ValueError
        return flag

    @handler('TRCV-PWM-MODE-ENABLED', required=True)
    def _parse_trcv_pwm_mode_enabled(self, xml_element: Element) -> bool:
        if (flag := self._parse_boolean_node(xml_element)) is None:
            raise ValueError
        return flag

    @handler('PROP-SEG', required=True)
    def _parse_prop_seg(self, xml_element: Element) -> int:
        if (ps := self._parse_int_node(xml_element)) is None:
            raise ValueError
        return ps

    @handler('SYNC-JUMP-WIDTH', required=True)
    def _parse_sync_jump_width(self, xml_element: Element) -> int:
        if (sjw := self._parse_int_node(xml_element)) is None:
            raise ValueError
        return sjw

    @handler('TIME-SEG-1', required=True)
    def _parse_time_seg_1(self, xml_element: Element) -> int:
        if (ts := self._parse_int_node(xml_element)) is None:
            raise ValueError
        return ts

    @handler('TIME-SEG-2', required=True)
    def _parse_time_seg_2(self, xml_element: Element) -> int:
        if (ts := self._parse_int_node(xml_element)) is None:
            raise ValueError
        return ts

    @handler('PWM-L')
    def _parse_pwm_l(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('PWM-O')
    def _parse_pwm_o(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('PWM-S')
    def _parse_pwm_s(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('SSP-OFFSET')
    def _parse_ssp_offset(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)


class CanControllerXlConfigurationRequirementsParser(
    BasicParserWithoutParent[CanControllerXlConfigurationRequirements]
):
    _returned_type = CanControllerXlConfigurationRequirements

    @handler('ERROR-SIGNALING-ENABLED')
    def _parse_error_signaling_enabled(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)

    @handler('TRCV-PWM-MODE-ENABLED')
    def _parse_trcv_pwm_mode_enabled(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)

    @handler('MAX-SYNC-JUMP-WIDTH')
    def _parse_max_sync_jump_width(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('MIN-SYNC-JUMP-WIDTH')
    def _parse_min_sync_jump_width(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('MAX-SAMPLE-POINT')
    def _parse_max_sample_point(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('MIN-SAMPLE-POINT')
    def _parse_min_sample_point(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('MAX-NUMBER-OF-TIME-QUANTA-PER-BIT')
    def _parse_max_number_of_time_quanta_per_bit(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('MIN-NUMBER-OF-TIME-QUANTA-PER-BIT')
    def _parse_min_number_of_time_quanta_per_bit(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('MAX-PWM-L')
    def _parse_max_pwm_l(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('MIN-PWM-L')
    def _parse_min_pwm_l(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('MAX-PWM-O')
    def _parse_max_pwm_o(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('MIN-PWM-O')
    def _parse_min_pwm_o(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('MAX-PWM-S')
    def _parse_max_pwm_s(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('MIN-PWM-S')
    def _parse_min_pwm_s(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('MAX-TRCV-DELAY-COMPENSATION-OFFSET')
    def _parse_max_trcv_delay_compensation_offset(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('MIN-TRCV-DELAY-COMPENSATION-OFFSET')
    def _parse_min_trcv_delay_compensation_offset(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)


class AbstractCanCommunicationControllerAttributesParser(BasicParserWithoutParent[A]):
    @handler('CAN-CONTROLLER-FD-ATTRIBUTES')
    def _parse_(self, xml_element: Element) -> CanControllerFdConfiguration | None:
        parser = CanControllerFdConfigurationParser()
        return parser.parse_element(xml_element)

    @handler('CAN-CONTROLLER-FD-REQUIREMENTS')
    def _parse_(self, xml_element: Element) -> CanControllerFdConfigurationRequirements | None:
        parser = CanControllerFdConfigurationRequirementsParser()
        return parser.parse_element(xml_element)

    @handler('CAN-CONTROLLER-XL-ATTRIBUTES')
    def _parse_(self, xml_element: Element) -> CanControllerXlConfiguration | None:
        parser = CanControllerXlConfigurationParser()
        return parser.parse_element(xml_element)

    @handler('CAN-CONTROLLER-XL-REQUIREMENTS')
    def _parse_(self, xml_element: Element) -> CanControllerXlConfigurationRequirements | None:
        parser = CanControllerXlConfigurationRequirementsParser()
        return parser.parse_element(xml_element)


class CanControllerConfigurationParser(
    AbstractCanCommunicationControllerAttributesParser[CanControllerConfiguration]
):
    _returned_type = CanControllerConfiguration

    @handler('SYNC-JUMP-WIDTH')
    def _parse_sync_jump_width(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('TIME-SEG-1')
    def _parse_time_seg_1(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('TIME-SEG-2')
    def _parse_time_seg_2(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)


class CanControllerConfigurationRequirementsParser(
    AbstractCanCommunicationControllerAttributesParser[CanControllerConfigurationRequirements]
):
    _returned_type = CanControllerConfigurationRequirements

    @handler('MAX-SYNC-JUMP-WIDTH')
    def _parse_max_sync_jump_width(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('MIN-SYNC-JUMP-WIDTH')
    def _parse_min_sync_jump_width(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('MAX-SAMPLE-POINT')
    def _parse_max_sample_point(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('MIN-SAMPLE-POINT')
    def _parse_min_sample_point(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('MAX-NUMBER-OF-TIME-QUANTA-PER-BIT')
    def _parse_max_number_of_time_quanta_per_bit(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('MIN-NUMBER-OF-TIME-QUANTA-PER-BIT')
    def _parse_min_number_of_time_quanta_per_bit(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)


class CanCommunicationControllerAttributesParserSelector(ParserSelector[A]):
    _tag_map = {
        'CAN-CONTROLLER-CONFIGURATION': CanControllerConfigurationParser,
        'CAN-CONTROLLER-CONFIGURATION-REQUIREMENTS': CanControllerConfigurationRequirementsParser,
    }
