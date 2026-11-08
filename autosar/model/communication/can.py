from dataclasses import dataclass

from autosar.model.ar_object import ArObject
from autosar.model.communication.frame import Frame, FrameTriggering
from autosar.model.enums import CanAddressingModeType, CanFrameRxBehaviorEnum, CanFrameTxBehaviorEnum


@dataclass
class RxIdentifierRange(ArObject):
    lower_can_id: int
    upper_can_id: int


class CanFrame(Frame):
    pass


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
