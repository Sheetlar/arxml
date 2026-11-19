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


class PduCollectionSemanticsEnum(ArEnum):
    LAST_IS_BEST = auto()
    QUEUED = auto()


class ContainedIPduCollectionSemanticsEnum(ArEnum):
    LAST_IS_BEST = auto()
    QUEUED = auto()


class DiagPduType(ArEnum):
    DIAG_REQUEST = auto()
    DIAG_RESPONSE = auto()


class SecuredPduHeaderEnum(ArEnum):
    NO_HEADER = auto()
    SECURED_PDU_HEADER_08_BIT = auto()
    SECURED_PDU_HEADER_16_BIT = auto()
    SECURED_PDU_HEADER_32_BIT = auto()


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


class EventGroupControlTypeEnum(ArEnum):
    ACTIVATION_AND_TRIGGER_UNICAST = auto()
    ACTIVATION_MULTICAST = auto()
    ACTIVATION_UNICAST = auto()
    TRIGGER_UNICAST = auto()


class ServiceVersionAcceptanceKindEnum(ArEnum):
    EXACT_OR_ANY_MINOR_VERSION = auto()
    MINIMUM_MINOR_VERSION = auto()


class CryptoServiceKeyGenerationEnum(ArEnum):
    KEY_DERIVATION = auto()
    KEY_STORAGE = auto()


class CryptoCertificateAlgorithmFamilyEnum(ArEnum):
    RSA = auto()
    ECC = auto()


class CryptoCertificateFormatEnum(ArEnum):
    X_509 = auto()
    CVC = auto()


class DataTypePolicyEnum(ArEnum):
    LEGACY = auto()
    NETWORK_REPRESENTATION_FROM_COM_SPEC = auto()
    OVERRIDE = auto()
    TRANSFORMING_I_SIGNAL = auto()
    DDS_SIGNAL = auto()
    DDS_SERVICE = auto()


class ISignalTypeEnum(ArEnum):
    ARRAY = auto()
    PRIMITIVE = auto()


class HandleOutOfRangeEnum(ArEnum):
    DEFAULT = auto()
    EXTERNAL_REPLACEMENT = auto()
    IGNORE = auto()
    INVALID = auto()
    NONE = auto()
    SATURATE = auto()


class CSTransformerErrorReactionEnum(ArEnum):
    APPLICATION_ONLY = auto()
    AUTONOMOUS = auto()


class SomeIpMessageTypeEnum(ArEnum):
    NOTIFICATION = auto()
    REQUEST = auto()
    REQUEST_NO_RETURN = auto()
    RESPONSE = auto()


class SomeIpTransformerSessionHandlingEnum(ArEnum):
    SESSION_HANDLING_ACTIVE = auto()
    SESSION_HANDLING_INACTIVE = auto()


class DataTransformationKindEnum(ArEnum):
    ASYMMETRIC_FROM_BYTE_ARRAY = auto()
    ASYMMETRIC_TO_BYTE_ARRAY = auto()
    SYMMETRIC = auto()


class TransformerClassEnum(ArEnum):
    CUSTOM = auto()
    SAFETY = auto()
    SECURITY = auto()
    SERIALIZER = auto()


class DataIdModeEnum(ArEnum):
    ALL_16_BIT = auto()
    ALTERNATING_8_BIT = auto()
    LOWER_12_BIT = auto()
    LOWER_8_BIT = auto()


class EndToEndProfileBehaviorEnum(ArEnum):
    PRE_R_4_2 = 'PRE--R-4--2'
    R_4_2 = 'R-4--2'


class AutoCollectEnum(ArEnum):
    REF_ALL = auto()
    REF_NONE = auto()
    REF_NON_STANDARD = auto()


class CanTpChannelModeType(ArEnum):
    FULL_DUPLEX_MODE = auto()
    HALF_DUPLEX_MODE = auto()


class CanTpAddressingFormatType(ArEnum):
    EXTENDED = auto()
    MIXED = auto()
    MIXED_29_BIT = auto()
    NORMALFIXED = auto()
    STANDARD = auto()


class NetworkTargetAddressType(ArEnum):
    FUNCTIONAL = auto()
    PHYSICAL = auto()
