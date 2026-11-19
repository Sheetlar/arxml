from typing import TypeVar

from autosar.model.element import Element as ArElement
from autosar.parser.communication.can_tp import CanTpConfigParser
from autosar.parser.communication.do_ip import DoIpTpConfigParser
from autosar.parser.communication.ethernet import (
    SocketConnectionIPduIdentifierSetParser,
    ServiceInstanceCollectionSetParser,
    EthTpConfigParser,
    SomeIpTpConfigParser,
    SomeIpSdClientServiceInstanceConfigParser,
    SomeIpSdServerServiceInstanceConfigParser,
    SomeIpSdClientEventGroupTimingConfigParser,
    SomeIpSdServerEventGroupTimingConfigParser,
)
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
from autosar.parser.communication.pdu import (
    GeneralPurposePduParser,
    NmPduParser,
    UserDefinedPduParser,
    ContainerIPduParser,
    DcmIPduParser,
    GeneralPurposeIPduParser,
    ISignalIPduParser,
    J1939DcmIPduParser,
    J1939ProtectedIPduParser,
    MultiplexedIPduParser,
    NPduParser,
    SecuredIPduParser,
    UserDefinedIPduParser,
    ISignalIPduGroupParser,
    PdurIPduGroupParser,
    GeneralPurposeConnectionParser,
)
from autosar.parser.communication.secure_comm import (
    SecureCommunicationPropsSetParser,
    CryptoServicePrimitiveParser,
    CryptoServiceKeyParser,
    CryptoServiceQueueParser,
)
from autosar.parser.communication.signal import (
    ISignalParser,
    ISignalGroupParser,
    SystemSignalParser,
    SystemSignalGroupParser,
)
from autosar.parser.collection_parser import CollectionParser
from autosar.parser.parser_base import ParserSelector
from autosar.parser.system.system_parser import SystemParser
from autosar.parser.topology.clusters import EthernetClusterParser, CanClusterParser
from autosar.parser.topology.ecu_parser import EcuInstanceParser
from autosar.parser.topology.gateway import GatewayParser
from autosar.parser.topology.tcp_ip_props import EthTcpIpPropsParser
from autosar.parser.transformation import (
    DataTransformationSetParser,
    TransformationPropsSetParser,
    TlvDataIdDefinitionSetParser,
)
from autosar.parser.value_spec_parser import ConstantSpecificationParser

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
        'GENERAL-PURPOSE-PDU': GeneralPurposePduParser,
        'NM-PDU': NmPduParser,
        'USER-DEFINED-PDU': UserDefinedPduParser,
        'CONTAINER-I-PDU': ContainerIPduParser,
        'DCM-I-PDU': DcmIPduParser,
        'GENERAL-PURPOSE-I-PDU': GeneralPurposeIPduParser,
        'I-SIGNAL-I-PDU': ISignalIPduParser,
        'J-1939-DCM-I-PDU': J1939DcmIPduParser,
        'J-1939-I-PDU': J1939ProtectedIPduParser,
        'MULTIPLEXED-I-PDU': MultiplexedIPduParser,
        'N-PDU': NPduParser,
        'SECURED-I-PDU': SecuredIPduParser,
        'USER-DEFINED-I-PDU': UserDefinedIPduParser,
        'I-SIGNAL-I-PDU-GROUP': ISignalIPduGroupParser,
        'PDUR-I-PDU-GROUP': PdurIPduGroupParser,
        'GENERAL-PURPOSE-CONNECTION': GeneralPurposeConnectionParser,
        'SOCKET-CONNECTION-IPDU-IDENTIFIER-SET': SocketConnectionIPduIdentifierSetParser,
        'SERVICE-INSTANCE-COLLECTION-SET': ServiceInstanceCollectionSetParser,
        'SOMEIP-SD-CLIENT-SERVICE-INSTANCE-CONFIG': SomeIpSdClientServiceInstanceConfigParser,
        'SOMEIP-SD-SERVER-SERVICE-INSTANCE-CONFIG': SomeIpSdServerServiceInstanceConfigParser,
        'SOMEIP-SD-CLIENT-EVENT-GROUP-TIMING-CONFIG': SomeIpSdClientEventGroupTimingConfigParser,
        'SOMEIP-SD-SERVER-EVENT-GROUP-TIMING-CONFIG': SomeIpSdServerEventGroupTimingConfigParser,
        'I-SIGNAL': ISignalParser,
        'I-SIGNAL-GROUP': ISignalGroupParser,
        'SYSTEM-SIGNAL': SystemSignalParser,
        'SYSTEM-SIGNAL-GROUP': SystemSignalGroupParser,
        'SECURE-COMMUNICATION-PROPS-SET-PARSER': SecureCommunicationPropsSetParser,
        'CRYPTO-SERVICE-PRIMITIVE-PARSER': CryptoServicePrimitiveParser,
        'CRYPTO-SERVICE-KEY-PARSER': CryptoServiceKeyParser,
        'CRYPTO-SERVICE-QUEUE-PARSER': CryptoServiceQueueParser,
        'CAN-TP-CONFIG': CanTpConfigParser,
        'DO-IP-TP-CONFIG': DoIpTpConfigParser,
        'ETH-TP-CONFIG': EthTpConfigParser,
        'SOMEIP-TP-CONFIG': SomeIpTpConfigParser,
        'DATA-TRANSFORMATION-SET': DataTransformationSetParser,
        'TRANSFORMATION-PROPS-SET': TransformationPropsSetParser,
        'TLV-DATA-ID-DEFINITION-SET': TlvDataIdDefinitionSetParser,
        'COLLECTION': CollectionParser,
        'CONSTANT-SPECIFICATION': ConstantSpecificationParser,
    }
