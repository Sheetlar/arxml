from typing import Callable
from xml.etree.ElementTree import Element

from autosar import ArObject
from autosar.model.frame import (
    AnyFrame,
    PduToFrameMapping,
    CanFrame,
    FlexrayFrame,
    GenericEthernetFrame,
    Ieee1722TpFrame,
    UserDefinedEthernetFrame,
    LinEventTriggeredFrame,
    LinSporadicFrame,
    LinUnconditionalFrame,
)
from autosar.parser.parser_base import ElementParser


class FrameParser(ElementParser):
    _frame_len_tag = 'FRAME-LENGTH'
    _mappings_tag = 'PDU-TO-FRAME-MAPPINGS'
    _frame_tags = (_frame_len_tag, _mappings_tag)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.switcher: dict[str, Callable[[Element, ArObject | None], AnyFrame | None]] = {
            'CAN-FRAME': self._frame_parser(CanFrame),
            'FLEXRAY-FRAME': self._frame_parser(FlexrayFrame),
            'GENERIC-ETHERNET-FRAME': self._frame_parser(GenericEthernetFrame),
            'IEEE-1722-TP-ETHERNET-FRAME': self._parse_ieee_tp_eth_frame,
            'USER-DEFINED-ETHERNET-FRAME': self._frame_parser(UserDefinedEthernetFrame),
            'LIN-EVENT-TRIGGERED-FRAME': self._parse_lin_event_triggered_frame,
            'LIN-SPORADIC-FRAME': self._parse_lin_sporadic_frame,
            'LIN-UNCONDITIONAL-FRAME': self._frame_parser(LinUnconditionalFrame),
        }

    def get_supported_tags(self):
        return self.switcher.keys()

    def parse_element(self, xml_element: Element, parent: ArObject | None = None) -> AnyFrame | None:
        if xml_element.tag not in self.switcher:
            return None
        element_parser = self.switcher[xml_element.tag]
        return element_parser(xml_element, parent)

    def _frame_parser(self, frame_type: type[AnyFrame]) -> Callable[[Element, ArObject | None], AnyFrame]:
        def parse_frame(xml_elem: Element, parent: ArObject | None = None) -> AnyFrame:
            return frame_type(parent=parent, **self._parse_common_frame_args(xml_elem))

        return parse_frame

    def _parse_ieee_tp_eth_frame(self, xml_elem: Element, parent: ArObject | None = None) -> Ieee1722TpFrame:
        return Ieee1722TpFrame(
            relative_representation_time=self.parse_number_node(xml_elem.find('RELATIVE-REPRESENTATION-TIME')),
            stream_identifier=self.parse_int_node(xml_elem.find('STREAM-IDENTIFIER')),
            sub_type=self.parse_int_node(xml_elem.find('SUB-TYPE')),
            version=self.parse_int_node(xml_elem.find('VERSION')),
            parent=parent,
            **self._parse_common_frame_args(xml_elem),
        )

    def _parse_lin_event_triggered_frame(self, xml_elem: Element, parent: ArObject | None = None) -> LinEventTriggeredFrame:
        return LinEventTriggeredFrame(
            collision_resolving_schedule_ref=self.parse_text_node(xml_elem.find('COLLISION-RESOLVING-SCHEME-REF')),
            lin_unconditional_frame_refs=list(self.child_string_nodes(xml_elem.find('LIN-UNCONDITIONAL-FRAME-REFS'))),
            parent=parent,
            **self._parse_common_frame_args(xml_elem),
        )

    def _parse_lin_sporadic_frame(self, xml_elem: Element, parent: ArObject | None = None) -> LinSporadicFrame:
        return LinSporadicFrame(
            substituted_frame_refs=list(self.child_string_nodes(xml_elem.find('SUBSTITUTED-FRAME-REFS'))),
            parent=parent,
            **self._parse_common_frame_args(xml_elem),
        )

    def _parse_common_frame_args(self, xml_elem: Element) -> dict[str, ...]:
        element_args = self.parse_common_tags(xml_elem)
        args = {
            'frame_length': self.parse_int_node(xml_elem.find(self._frame_len_tag)),
            'pdu_to_frame_mappings': self.parse_element_list(
                xml_elem.find(self._mappings_tag),
                self._parse_pdu_to_frame_mapping,
            ),
        }
        return self.not_none_dict(args) | element_args

    def _parse_pdu_to_frame_mapping(self, xml_elem: Element) -> PduToFrameMapping:
        common_args = self.parse_common_tags(xml_elem)
        return PduToFrameMapping(
            packing_byte_order=self.parse_text_node(xml_elem.find('PACKING-BYTE-ORDER')),
            pdu_ref=self.parse_text_node(xml_elem.find('PDU-REF')),
            start_position=self.parse_int_node(xml_elem.find('START-POSITION')),
            update_indication_bit_position=self.parse_int_node(xml_elem.find('UPDATE-INDICATION-BIT-POSITION')),
            **common_args,
        )
