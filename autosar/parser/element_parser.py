from typing import TypeVar

from autosar.model.element import Element as ArElement
from autosar.parser.communication.frame import (
    CanFrameParser,
    GenericEthernetFrameParser,
    Ieee1722TpFrameParser,
    UserDefinedEthernetFrameParser,
    FlexrayFrameParser,
    LinEventTriggeredFrameParser,
    LinSporadicFrameParser,
    LinUnconditionalFrameParser,
)
from autosar.parser.parser_base import ParserSelector
from autosar.parser.system.system_parser import SystemParser
from autosar.parser.topology.clusters import EthernetClusterParser, CanClusterParser
from autosar.parser.topology.ecu_parser import EcuInstanceParser
from autosar.parser.topology.gateway import GatewayParser
from autosar.parser.topology.tcp_ip_props import EthTcpIpPropsParser

E = TypeVar('E', bound=ArElement)


class ElementParserSelector(ParserSelector[E]):
    _tag_map = {
        'SYSTEM': SystemParser,
        'CAN-CLUSTER': CanClusterParser,
        'ETHERNET-CLUSTER': EthernetClusterParser,
        'ECU-INSTANCE': EcuInstanceParser,
        'ETH-TCP-IP-PROPS': EthTcpIpPropsParser,
        'GATEWAY': GatewayParser,
        'CAN-FRAME': CanFrameParser,
        'FLEXRAY-FRAME': GenericEthernetFrameParser,
        'GENERIC-ETHERNET-FRAME': Ieee1722TpFrameParser,
        'IEEE-1722-TP-ETHERNET-FRAME': UserDefinedEthernetFrameParser,
        'USER-DEFINED-ETHERNET-FRAME': FlexrayFrameParser,
        'LIN-EVENT-TRIGGERED-FRAME': LinEventTriggeredFrameParser,
        'LIN-SPORADIC-FRAME': LinSporadicFrameParser,
        'LIN-UNCONDITIONAL-FRAME': LinUnconditionalFrameParser,
    }
