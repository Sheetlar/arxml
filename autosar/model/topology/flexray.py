from dataclasses import dataclass
from typing import Iterable

from autosar.model.ar_object import ArObject
from autosar.model.topology.abstract import (
    CommunicationControllerContent,
    CommunicationController,
    CommunicationConnector,
)


@dataclass
class FlexrayFifoRange(ArObject):
    range_max: int
    range_min: int


@dataclass
class FlexrayFifoConfiguration(ArObject):
    admit_without_message_id: bool
    base_cycle: int
    cycle_repetition: int
    fifo_depth: int
    fifo_range: list[FlexrayFifoRange]
    msg_id_mask: int
    msg_id_match: int
    channel_ref: str | None = None


class FlexrayCommunicationControllerContent(CommunicationControllerContent):
    def __init__(
            self,
            accepted_startup_range: int | None = None,
            allow_halt_due_to_clock: bool | None = None,
            allow_passive_to_active: int | None = None,
            cluster_drift_damping: int | None = None,
            decoding_correction: int | None = None,
            delay_compensation_a: int | None = None,
            delay_compensation_b: int | None = None,
            external_sync: bool | None = None,
            extern_offset_correction: int | None = None,
            extern_rate_correction: int | None = None,
            fall_back_internal: bool | None = None,
            flexray_fifo: Iterable[FlexrayFifoConfiguration] | None = None,
            key_slot_id: int | None = None,
            key_slot_only_enabled: bool | None = None,
            key_slot_used_for_start_up: bool | None = None,
            key_slot_used_for_sync: bool | None = None,
            latest_t_x: int | None = None,
            listen_timeout: int | None = None,
            macro_initial_offset_a: int | None = None,
            macro_initial_offset_b: int | None = None,
            maximum_dynamic_payload_length: int | None = None,
            micro_initial_offset_a: int | None = None,
            micro_initial_offset_b: int | None = None,
            micro_per_cycle: int | None = None,
            microtick_duration: float | None = None,
            nm_vector_early_update: bool | None = None,
            offset_correction_out: int | None = None,
            rate_correction_out: int | None = None,
            samples_per_microtick: int | None = None,
            second_key_slot_id: int | None = None,
            two_key_slot_mode: bool | None = None,
            wake_up_pattern: int | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.accepted_startup_range = accepted_startup_range
        self.allow_halt_due_to_clock = allow_halt_due_to_clock
        self.allow_passive_to_active = allow_passive_to_active
        self.cluster_drift_damping = cluster_drift_damping
        self.decoding_correction = decoding_correction
        self.delay_compensation_a = delay_compensation_a
        self.delay_compensation_b = delay_compensation_b
        self.external_sync = external_sync
        self.extern_offset_correction = extern_offset_correction
        self.extern_rate_correction = extern_rate_correction
        self.fall_back_internal = fall_back_internal
        self.flexray_fifo = self.eval_children(flexray_fifo)
        self.key_slot_id = key_slot_id
        self.key_slot_only_enabled = key_slot_only_enabled
        self.key_slot_used_for_start_up = key_slot_used_for_start_up
        self.key_slot_used_for_sync = key_slot_used_for_sync
        self.latest_t_x = latest_t_x
        self.listen_timeout = listen_timeout
        self.macro_initial_offset_a = macro_initial_offset_a
        self.macro_initial_offset_b = macro_initial_offset_b
        self.maximum_dynamic_payload_length = maximum_dynamic_payload_length
        self.micro_initial_offset_a = micro_initial_offset_a
        self.micro_initial_offset_b = micro_initial_offset_b
        self.micro_per_cycle = micro_per_cycle
        self.microtick_duration = microtick_duration
        self.nm_vector_early_update = nm_vector_early_update
        self.offset_correction_out = offset_correction_out
        self.rate_correction_out = rate_correction_out
        self.samples_per_microtick = samples_per_microtick
        self.second_key_slot_id = second_key_slot_id
        self.two_key_slot_mode = two_key_slot_mode
        self.wake_up_pattern = wake_up_pattern


class FlexrayCommunicationController(
    CommunicationController[FlexrayCommunicationControllerContent]
):
    pass


class FlexrayCommunicationConnector(CommunicationConnector):
    def __init__(
            self,
            nm_ready_sleep_time: float | None = None,
            wake_up_channel: bool | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.nm_ready_sleep_time = nm_ready_sleep_time
        self.wake_up_channel = wake_up_channel
