from typing import TypeVar
from xml.etree.ElementTree import Element

from autosar.model.base import DataFilter
from autosar.model.communication.pdu import (
    TimeRangeTypeTolerance,
    AbsoluteTolerance,
    RelativeTolerance,
    TimeRangeType,
    EventControlledTiming,
    CyclicTiming,
    ModeDrivenTransmissionModeCondition,
    TransmissionModeCondition,
    TransmissionModeTiming,
    TransmissionModeDeclaration,
    IPduTiming,
)
from autosar.parser.common_simple_parsers import DataFilterParser
from autosar.parser.identifiable import DescribableParser
from autosar.parser.parser_base import (
    handler,
    multiple_with_check,
    eval_children,
    single_subclass_aggr,
    BasicParser,
    ParserSelector,
)

T = TypeVar('T', bound=TimeRangeTypeTolerance)


class AbsoluteToleranceParser(BasicParser[AbsoluteTolerance]):
    _returned_type = AbsoluteTolerance

    @handler('ABSOLUTE', required=True)
    def _parse_absolute(self, xml_element: Element) -> float:
        if (t := self._parse_float_node(xml_element)) is None:
            raise ValueError
        return t


class RelativeToleranceParser(BasicParser[RelativeTolerance]):
    _returned_type = RelativeTolerance

    @handler('RELATIVE', required=True)
    def _parse_relative(self, xml_element: Element) -> int:
        if (t := self._parse_int_node(xml_element)) is None:
            raise ValueError
        return t


class TimeRangeTypeToleranceParserSelector(ParserSelector[T]):
    _tag_map = {
        'ABSOLUTE-TOLERANCE': AbsoluteToleranceParser,
        'RELATIVE-TOLERANCE': RelativeToleranceParser,
    }


class TimeRangeTypeParser(BasicParser[TimeRangeType]):
    _returned_type = TimeRangeType

    @handler('VALUE', required=True)
    def _parse_value(self, xml_element: Element) -> float:
        if (v := self._parse_float_node(xml_element)) is None:
            raise ValueError
        return v

    @handler('TOLERANCE')
    @single_subclass_aggr
    def _parse_tolerance(self, xml_element: Element) -> T | None:
        parser = TimeRangeTypeToleranceParserSelector(xml_element.tag)
        return parser.parse_element(xml_element)


class CyclicTimingParser(DescribableParser[CyclicTiming]):
    _returned_type = CyclicTiming

    @handler('TIME-PERIOD', required=True)
    def _parse_time_period(self, xml_element: Element) -> TimeRangeType:
        parser = TimeRangeTypeParser()
        if (r := parser.parse_element(xml_element)) is None:
            raise ValueError
        return r

    @handler('TIME-OFFSET')
    def _parse_time_offset(self, xml_element: Element) -> TimeRangeType | None:
        parser = TimeRangeTypeParser()
        return parser.parse_element(xml_element)


class EventControlledTimingParser(DescribableParser[EventControlledTiming]):
    _returned_type = EventControlledTiming

    @handler('NUMBER-OF-REPETITIONS', required=True)
    def _parse_number_of_repetitions(self, xml_element: Element) -> int:
        if (n := self._parse_int_node(xml_element)) is None:
            raise ValueError
        return n

    @handler('REPETITION-PERIOD')
    def _parse_repetition_period(self, xml_element: Element) -> TimeRangeType | None:
        parser = TimeRangeTypeParser()
        return parser.parse_element(xml_element)


class TransmissionModeTimingParser(BasicParser[TransmissionModeTiming]):
    _returned_type = TransmissionModeTiming

    @handler('CYCLIC-TIMING')
    def _parse_cyclic_timing(self, xml_element: Element) -> CyclicTiming | None:
        parser = CyclicTimingParser()
        return parser.parse_element(xml_element)

    @handler('EVENT-CONTROLLED-TIMING')
    def _parse_event_controlled_timing(self, xml_element: Element) -> EventControlledTiming | None:
        parser = EventControlledTimingParser()
        return parser.parse_element(xml_element)


class ModeDrivenTransmissionModeConditionParser(
    BasicParser[ModeDrivenTransmissionModeCondition]
):
    _returned_type = ModeDrivenTransmissionModeCondition

    @handler('MODE-DECLARATION-REFS', required=True)
    @eval_children
    @multiple_with_check
    def _parse_mode_declaration(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)


class TransmissionModeConditionParser(BasicParser[TransmissionModeCondition]):
    _returned_type = TransmissionModeCondition

    @handler('DATA-FILTER', required=True)
    def _parse_data_filter(self, xml_element: Element) -> DataFilter:
        parser = DataFilterParser()
        if (df := parser.parse_element(xml_element)) is None:
            raise ValueError
        return df

    @handler('I-SIGNAL-IN-I-PDU-REF', required=True)
    def _parse_i_signal_in_i_pdu(self, xml_element: Element) -> str:
        if (ref := self._parse_text_node(xml_element)) is None:
            raise ValueError
        return ref


class TransmissionModeDeclarationParser(
    BasicParser[TransmissionModeDeclaration]
):
    _returned_type = TransmissionModeDeclaration

    @handler('MODE-DRIVEN-FALSE-CONDITIONS')
    @eval_children
    @multiple_with_check(expected_name='MODE-DRIVEN-TRANSMISSION-MODE-CONDITION')
    def _parse_mode_driven_false_condition(self, xml_element: Element) -> ModeDrivenTransmissionModeCondition | None:
        parser = ModeDrivenTransmissionModeConditionParser()
        return parser.parse_element(xml_element)

    @handler('MODE-DRIVEN-TRUE-CONDITIONS')
    @eval_children
    @multiple_with_check(expected_name='MODE-DRIVEN-TRANSMISSION-MODE-CONDITION')
    def _parse_mode_driven_true_condition(self, xml_element: Element) -> ModeDrivenTransmissionModeCondition | None:
        parser = ModeDrivenTransmissionModeConditionParser()
        return parser.parse_element(xml_element)

    @handler('TRANSMISSION-MODE-CONDITIONS')
    @eval_children
    @multiple_with_check
    def _parse_transmission_mode_condition(self, xml_element: Element) -> TransmissionModeCondition | None:
        parser = TransmissionModeConditionParser()
        return parser.parse_element(xml_element)

    @handler('TRANSMISSION-MODE-FALSE-TIMING')
    def _parse_transmission_mode_false_timing(self, xml_element: Element) -> TransmissionModeTiming | None:
        parser = TransmissionModeTimingParser()
        return parser.parse_element(xml_element)

    @handler('TRANSMISSION-MODE-TRUE-TIMING')
    def _parse_transmission_mode_true_timing(self, xml_element: Element) -> TransmissionModeTiming | None:
        parser = TransmissionModeTimingParser()
        return parser.parse_element(xml_element)


class IPduTimingParser(DescribableParser[IPduTiming]):
    _returned_type = IPduTiming

    @handler('MINIMUM-DELAY')
    def _parse_minimum_delay(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('TRANSMISSION-MODE-DECLARATION')
    def _parse_transmission_mode_declaration(self, xml_element: Element) -> TransmissionModeDeclaration | None:
        parser = TransmissionModeDeclarationParser()
        return parser.parse_element(xml_element)
