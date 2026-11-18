from typing import TypeVar
from xml.etree.ElementTree import Element

from autosar.model.enums import EthernetMacLayerTypeEnum
from autosar.model.topology.abstract import (
    CommunicationControllerContent,
    CommunicationController,
)
from autosar.model.topology.can import (
    CanCommunicationControllerContent,
    CanCommunicationController,
    CanCommunicationControllerAttributes,
)
from autosar.model.topology.ethernet import (
    EthernetCommunicationControllerContent,
    EthernetCommunicationController,
    CouplingPort,
)
from autosar.model.topology.flexray import (
    FlexrayCommunicationControllerContent,
    FlexrayCommunicationController,
)
from autosar.model.topology.lin import LinMasterContent, LinSlaveContent, LinMaster, LinSlave
from autosar.model.topology.user_defined import (
    UserDefinedCommunicationControllerContent,
    UserDefinedCommunicationController,
)
from autosar.parser.topology.can import CanCommunicationControllerAttributesParserSelector
from autosar.parser.topology.ethernet.coupling_port import CouplingPortParser
from autosar.parser.identifiable import IdentifiableParser
from autosar.parser.parser_base import (
    handler,
    multiple_with_check,
    BasicParser,
    PropertySetParser,
    ParserSelector,
)

CC = TypeVar('CC', bound=CommunicationController)
CCC = TypeVar('CCC', bound=CommunicationControllerContent)


class CommunicationControllerContentParser(BasicParser[CCC]):
    @handler('WAKE-UP-BY-CONTROLLER-SUPPORTED')
    def _parse_wake_up_by_controller_supported(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)


class CanCommunicationControllerContentParser(
    CommunicationControllerContentParser[CanCommunicationControllerContent]
):
    _returned_type = CanCommunicationControllerContent

    @handler('CAN-CONTROLLER-ATTRIBUTES')
    def _parse_can_controller_attributes(self, xml_element: Element) -> CanCommunicationControllerAttributes | None:
        parser = CanCommunicationControllerAttributesParserSelector(xml_element.tag)
        return parser.parse_element(xml_element)


class EthernetCommunicationControllerContentParser(
    CommunicationControllerContentParser[EthernetCommunicationControllerContent]
):
    _returned_type = EthernetCommunicationControllerContent

    @handler('CAN-XL-CONFIG-REF')
    def _parse_can_xl_config(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('COUPLING-PORTS')
    @multiple_with_check
    def _parse_coupling_port(self, xml_element: Element) -> CouplingPort | None:
        parser = CouplingPortParser()
        return parser.parse_element(xml_element)

    @handler('MAC-LAYER-TYPE')
    def _parse_mac_layer_type(self, xml_element: Element) -> EthernetMacLayerTypeEnum | None:
        return self._parse_enum_node(xml_element, EthernetMacLayerTypeEnum)

    @handler('MAC-UNICAST-ADDRESS')
    def _parse_mac_unicast_address(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('MAXIMUM-RECEIVE-BUFFER-LENGTH')
    def _parse_maximum_receive_buffer_length(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('MAXIMUM-TRANSMIT-BUFFER-LENGTH')
    def _parse_maximum_transmit_buffer_length(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('SLAVE-ACT-AS-PASSIVE-COMMUNICATION-SLAVE')
    def _parse_slave_act_as_passive_communication_slave(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)

    @handler('SLAVE-QUALIFIED-UNEXPECTED-LINK-DOWN-TIME')
    def _parse_slave_qualified_unexpected_link_down_time(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)


class FlexrayCommunicationControllerContentParser(
    CommunicationControllerContentParser[FlexrayCommunicationControllerContent]
):
    _returned_type = FlexrayCommunicationControllerContent


class LinMasterContentParser(
    CommunicationControllerContentParser[LinMasterContent]
):
    _returned_type = LinMasterContent


class LinSlaveContentParser(
    CommunicationControllerContentParser[LinSlaveContent]
):
    _returned_type = LinSlaveContent


class UserDefinedCommunicationControllerContentParser(
    CommunicationControllerContentParser[UserDefinedCommunicationControllerContent]
):
    _returned_type = UserDefinedCommunicationControllerContent


class CommunicationControllerParser(IdentifiableParser[CC], PropertySetParser[CC, CCC]):
    """Abstract"""


class CanControllerParser(
    CommunicationControllerParser[
        CanCommunicationController,
        CanCommunicationControllerContent,
    ]
):
    _returned_type = CanCommunicationController
    _variant_parser_type = CanCommunicationControllerContentParser
    _tag = 'CAN-COMMUNICATION-CONTROLLER'


class EthernetControllerParser(
    CommunicationControllerParser[
        EthernetCommunicationController,
        EthernetCommunicationControllerContent,
    ]
):
    _returned_type = EthernetCommunicationController
    _variant_parser_type = EthernetCommunicationControllerContentParser
    _tag = 'ETHERNET-COMMUNICATION-CONTROLLER'


class FlexrayControllerParser(
    CommunicationControllerParser[
        FlexrayCommunicationController,
        FlexrayCommunicationControllerContent,
    ]
):
    _returned_type = FlexrayCommunicationController
    _variant_parser_type = FlexrayCommunicationControllerContentParser
    _tag = 'FLEXRAY-COMMUNICATION-CONTROLLER'


class LinMasterParser(
    CommunicationControllerParser[
        LinMaster,
        LinMasterContent,
    ]
):
    _returned_type = LinMaster
    _variant_parser_type = LinMasterContentParser
    _tag = 'LIN-MASTER-CONTROLLER'


class LinSlaveParser(
    CommunicationControllerParser[
        LinSlave,
        LinSlaveContent,
    ]
):
    _returned_type = LinSlave
    _variant_parser_type = LinSlaveContentParser
    _tag = 'LIN-SLAVE-CONTROLLER'


class UserDefinedControllerParser(
    CommunicationControllerParser[
        UserDefinedCommunicationController,
        UserDefinedCommunicationControllerContent,
    ]
):
    _returned_type = UserDefinedCommunicationController
    _variant_parser_type = UserDefinedCommunicationControllerContentParser
    _tag = 'USER-DEFINED-COMMUNICATION-CONTROLLER'


class CommunicationControllerParserSelector(ParserSelector):
    _tag_map = {
        'CAN-COMMUNICATION-CONTROLLER': CanControllerParser,
        'ETHERNET-COMMUNICATION-CONTROLLER': EthernetControllerParser,
        'FLEXRAY-COMMUNICATION-CONTROLLER': FlexrayControllerParser,
        'LIN-MASTER-CONTROLLER': LinMasterParser,
        'LIN-SLAVE-CONTROLLER': LinSlaveParser,
        'USER-DEFINED-COMMUNICATION-CONTROLLER': UserDefinedControllerParser,
    }
