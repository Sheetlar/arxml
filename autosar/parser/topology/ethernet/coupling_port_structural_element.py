from typing import TypeVar
from xml.etree.ElementTree import Element

from autosar.model.enums import (
    EthernetCouplingPortPreemptionEnum,
    EthernetCouplingPortSchedulerEnum,
)
from autosar.model.topology.ethernet import (
    CouplingPortShaper,
    CouplingPortAsynchronousTrafficShaper,
    CouplingPortCreditBasedShaper,
    CouplingPortEnhancedTrafficShaper,
    CouplingPortStructuralElement,
    CouplingPortFifo,
    CouplingPortScheduler,
)
from autosar.parser.identifiable import IdentifiableParser
from autosar.parser.parser_base import (
    handler,
    multiple_with_check,
    single_subclass_aggr,
    ParserSelector,
)

SE = TypeVar('SE', bound=CouplingPortStructuralElement)


class CouplingPortAsynchronousTrafficShaperParser(
    IdentifiableParser[CouplingPortAsynchronousTrafficShaper]
):
    _returned_type = CouplingPortAsynchronousTrafficShaper

    @handler('COMMITTED-BURST-SIZE')
    def _parse_committed_burst_size(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('COMMITTED-INFORMATION-RATE')
    def _parse_committed_information_rate(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('TRAFFIC-SHAPER-GROUP-REF')
    def _parse_traffic_shaper_group(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)


class CouplingPortCreditBasedShaperParser(
    IdentifiableParser[CouplingPortCreditBasedShaper]
):
    _returned_type = CouplingPortCreditBasedShaper

    @handler('IDLE-SLOPE')
    def _parse_idle_slope(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('LOWER-BOUNDARY')
    def _parse_lower_boundary(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('UPPER-BOUNDARY')
    def _parse_upper_boundary(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)


class CouplingPortEnhancedTrafficShaperParser(
    IdentifiableParser[CouplingPortEnhancedTrafficShaper]
):
    _returned_type = CouplingPortEnhancedTrafficShaper

    @handler('ETS-AVAILABLE-BANDWIDTH-IN-PERCENT')
    def _parse_ets_available_bandwidth_in_percent(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('ETS-AVAILABLE-BANDWIDTH-IN-WEIGHT-VALUE')
    def _parse_ets_available_bandwidth_in_weight_value(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)


class CouplingPortShaperParserSelector(ParserSelector[CouplingPortShaper]):
    _tag_map = {
        'COUPLING-PORT-ASYNCHRONOUS-TRAFFIC-SHAPER': CouplingPortAsynchronousTrafficShaperParser,
        'COUPLING-PORT-CREDIT-BASED-SHAPER': CouplingPortCreditBasedShaperParser,
        'COUPLING-PORT-ENHANCED-TRAFFIC-SHAPER': CouplingPortEnhancedTrafficShaperParser,
    }


class CouplingPortFifoParser(IdentifiableParser[CouplingPortFifo]):
    _returned_type = CouplingPortFifo

    @handler('ASSIGNED-TRAFFIC-CLASSES', 'ASSIGNED-TRAFFIC-CLASSES')
    @multiple_with_check(expected_name='ASSIGNED-TRAFFIC-CLASS')
    def _parse_assigned_traffic_class(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('MINIMUM-FIFO-LENGTH')
    def _parse_minimum_fifo_length(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('SHAPER')
    @single_subclass_aggr
    def _parse_shaper(self, xml_element: Element) -> CouplingPortShaper | None:
        parser = CouplingPortShaperParserSelector(xml_element.tag)
        return parser.parse_element(xml_element)

    @handler('TRAFFIC-CLASS-PREEMPTION-SUPPORT')
    def _parse_traffic_class_preemption_support(
            self,
            xml_element: Element,
    ) -> EthernetCouplingPortPreemptionEnum | None:
        return self._parse_enum_node(xml_element, EthernetCouplingPortPreemptionEnum)


class CouplingPortSchedulerParser(IdentifiableParser[CouplingPortScheduler]):
    _returned_type = CouplingPortScheduler

    @handler('PORT-SCHEDULER')
    def _parse_port_scheduler(self, xml_element: Element) -> EthernetCouplingPortSchedulerEnum | None:
        return self._parse_enum_node(xml_element, EthernetCouplingPortSchedulerEnum)

    @handler('PREDECESSOR-REFS')
    @multiple_with_check
    def _parse_predecessor(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)


class CouplingPortStructuralElementParserSelector(ParserSelector[SE]):
    _tag_map = {
        'CouplingPortFifo': CouplingPortFifoParser,
        'CouplingPortScheduler': CouplingPortSchedulerParser,
    }
