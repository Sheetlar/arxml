from enum import auto

from autosar.model.base import ArEnum


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
