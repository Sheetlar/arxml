from enum import auto, StrEnum
from typing import TypeVar


class ArEnum(StrEnum):
    # noinspection PyMethodParameters
    def _generate_next_value_(name, start, count, last_values):
        return name.removeprefix('_').replace('_', '-').upper()


SomeEnum = TypeVar('SomeEnum', bound=ArEnum)


class IntervalTypeEnum(ArEnum):
    CLOSED = auto()
    OPEN = auto()


class ByteOrderEnum(ArEnum):
    MOST_SIGNIFICANT_BYTE_FIRST = auto()
    MOST_SIGNIFICANT_BYTE_LAST = auto()
    OPAQUE = auto()


class ContainerIPduTriggerEnum(ArEnum):
    DEFAULT_TRIGGER = auto()
    FIRST_CONTAINED_TRIGGER = auto()


class ContainerIPduHeaderTypeEnum(ArEnum):
    LONG_HEADER = auto()
    SHORT_HEADER = auto()
    NO_HEADER = auto()


class RxAcceptContainedIPduEnum(ArEnum):
    ACCEPT_ALL = auto()
    ACCEPT_CONFIGURED = auto()


class ContainedIPduCollectionSemanticsEnum(ArEnum):
    LAST_IS_BEST = auto()
    QUEUED = auto()


class PduCollectionTriggerEnum(ArEnum):
    ALWAYS = auto()
    NEVER = auto()


class TransferPropertyEnum(ArEnum):
    PENDING = auto()
    TRIGGERED = auto()
    TRIGGERED_ON_CHANGE = auto()
    TRIGGERED_ON_CHANGE_WITHOUT_REPETITION = auto()
    TRIGGERED_WITHOUT_REPETITION = auto()


class TriggerMode(ArEnum):
    DYNAMIC_PART_TRIGGER = auto()
    NONE = auto()
    STATIC_OR_DYNAMIC_PART_TRIGGER = auto()
    STATIC_PART_TRIGGER = auto()


class CanAddressingModeType(ArEnum):
    EXTENDED = auto()
    STANDARD = auto()


class CanFrameRxBehaviorEnum(ArEnum):
    ANY = auto()
    CAN_20 = auto()
    CAN_FD = auto()


class CanFrameTxBehaviorEnum(ArEnum):
    CAN_20 = auto()
    CAN_FD = auto()


class CommunicationDirectionType(ArEnum):
    IN = auto()
    OUT = auto()


class Ipv4AddressSourceEnum(ArEnum):
    AUTO_IP = auto()
    AUTO_IP_DOIP = auto()
    DHCPV_4 = auto()
    FIXED = auto()


class IpAddressKeepEnum(ArEnum):
    FORGET = auto()
    STORE_PERSISTENTLY = auto()


class Ipv6AddressSourceEnum(ArEnum):
    DHCPV_6 = auto()
    FIXED = auto()
    LINK_LOCAL = auto()
    LINK_LOCAL_DOIP = auto()
    ROUTER_ADVERTISEMENT = auto()


class UdpChecksumCalculationEnum(ArEnum):
    UDP_CHECKSUM_ENABLED = auto()
    UDP_CHECKSUM_DISABLED = auto()


class TcpRoleEnum(ArEnum):
    CONNECT = auto()
    LISTEN = auto()


class TlsVersionEnum(ArEnum):
    TLS_12 = auto()
    TLS_13 = auto()


class MappingDirectionEnum(ArEnum):
    BIDIRECTIONAL = auto()
    FIRST_TO_SECOND = auto()
    SECOND_TO_FIRST = auto()


class PncGatewayTypeEnum(ArEnum):
    ACTIVE = auto()
    NONE = auto()
    PASSIVE = auto()


class IPduSignalProcessingEnum(ArEnum):
    DEFERRED = auto()
    IMMEDIATE = auto()


class HandleInvalidEnum(ArEnum):
    DONT_INVALIDATE = auto()
    EXTERNAL_REPLACEMENT = auto()
    KEEP = auto()
    REPLACE = auto()


class DataFilterTypeEnum(ArEnum):
    ALWAYS = auto()
    MASKED_NEW_DIFFERS_MASKED_OLD = auto()
    MASKED_NEW_DIFFERS_X = auto()
    MASKED_NEW_EQUALS_X = auto()
    NEVER = auto()
    NEW_IS_OUTSIDE = auto()
    NEW_IS_WITHIN = auto()
    ONE_EVERY_N = auto()


class EthernetMacLayerTypeEnum(ArEnum):
    X_MII = auto()
    XG_MII = auto()
    XXG_MII = auto()


class EthernetPhysicalLayerTypeEnum(ArEnum):
    _100BASE_TX = auto()
    _1000BASE_T = auto()
    _100BASE_T1 = auto()
    _1000BASE_T1 = auto()
    IEEE802_11P = auto()
    _10BASE_T1S = auto()
    _2500BASE_T1 = auto()
    _5000BASE_T1 = auto()
    _10000BASE_T1 = auto()


class EthernetConnectionNegotiationEnum(ArEnum):
    AUTO = auto()
    MASTER = auto()
    SLAVE = auto()


class EthernetSwitchVlanIngressTagEnum(ArEnum):
    DROP_UNTAGGED = auto()
    FORWARD_AS_IS = auto()


class EthernetSwitchVlanEgressTaggingEnum(ArEnum):
    NOT_SENT = auto()
    SENT_TAGGED = auto()
    SENT_UNTAGGED = auto()


class CouplingPortRoleEnum(ArEnum):
    HOST_PORT = auto()
    UP_LINK_PORT = auto()
    STANDARD_PORT = auto()


class MacSecRoleEnum(ArEnum):
    PEER = auto()
    KEY_SERVER = auto()


class MacSecFailPermissiveModeEnum(ArEnum):
    NEVER = auto()
    TIMEOUT = auto()


class CouplingPortRatePolicyActionEnum(ArEnum):
    DROP_FRAME = auto()
    BLOCK_SOURCE = auto()


class EthernetCouplingPortSchedulerEnum(ArEnum):
    STRICT_PRIORITY = auto()
    ENHANCED_TRAFFIC_SHAPER = auto()


class EthernetCouplingPortPreemptionEnum(ArEnum):
    EXPRESS = auto()
    PREEMPTABLE = auto()
