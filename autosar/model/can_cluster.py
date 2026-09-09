from dataclasses import dataclass

from autosar.model.ar_object import ArObject
from autosar.model.communication_cluster import (
    PhysicalChannel,
    CommunicationCluster,
    FrameTriggering,
)
from autosar.model.element import ElementVariants
from autosar.model.enums import CanAddressingModeType, CanFrameRxBehaviorEnum, CanFrameTxBehaviorEnum


@dataclass
class RxIdentifierRange(ArObject):
    lower_can_id: int
    upper_can_id: int


class CanFrameTriggering(FrameTriggering):
    def __init__(
            self,
            can_addressing_mode: CanAddressingModeType,
            can_frame_rx_behavior: CanFrameRxBehaviorEnum,
            can_frame_tx_behavior: CanFrameTxBehaviorEnum,
            identifier: int | None = None,
            rx_mask: int | None = None,
            tx_mask: int | None = None,
            j1939_requestable: bool = False,
            rx_identifier_range: RxIdentifierRange | None = None,
            can_xl_frame_triggering_props: None = None,
            absolutely_scheduled_timing: None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.can_addressing_mode = can_addressing_mode
        self.identifier = identifier
        self.can_frame_rx_behavior = can_frame_rx_behavior
        self.can_frame_tx_behavior = can_frame_tx_behavior
        self.rx_mask = rx_mask
        self.tx_mask = tx_mask
        self.j1939_requestable = j1939_requestable
        self.rx_identifier_range = rx_identifier_range
        self.can_xl_frame_triggering_props = can_xl_frame_triggering_props
        self.absolutely_scheduled_timing = absolutely_scheduled_timing


class CanPhysicalChannel(PhysicalChannel):
    pass


class CanCluster(CommunicationCluster):
    def __init__(
            self,
            can_fd_baudrate: int | None = None,
            can_xl_baudrate: int | None = None,
            bus_off_recovery: None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.can_fd_baudrate = can_fd_baudrate
        self.can_xl_baudrate = can_xl_baudrate
        self.bus_off_recovery = bus_off_recovery

    @property
    def physical_channel(self) -> CanPhysicalChannel:
        return self.physical_channels[0]


class CanClusterVariants(ElementVariants[CanCluster]):
    pass
