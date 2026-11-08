from dataclasses import dataclass
from typing import TypeVar

from autosar.model.ar_object import ArObject
from autosar.model.topology.abstract import (
    CommunicationControllerContent,
    CommunicationController,
    CommunicationConnector,
    PhysicalChannel,
    CommunicationClusterContent,
    CommunicationCluster,
)


@dataclass
class CanControllerFdConfiguration(ArObject):
    tx_bit_rate_switch: bool | None = None
    padding_value: int | None = None
    prop_seg: int | None = None
    sync_jump_width: int | None = None
    time_seg_1: int | None = None
    time_seg_2: int | None = None
    ssp_offset: int | None = None


@dataclass
class CanControllerFdConfigurationRequirements(ArObject):
    tx_bit_rate_switch: bool | None = None
    padding_value: int | None = None
    max_sync_jump_width: float | None = None
    min_sync_jump_width: float | None = None
    max_sample_point: float | None = None
    min_sample_point: float | None = None
    max_number_of_time_quanta_per_bit: int | None = None
    min_number_of_time_quanta_per_bit: int | None = None
    max_trcv_delay_compensation_offset: float | None = None
    min_trcv_delay_compensation_offset: float | None = None


@dataclass
class CanControllerXlConfiguration(ArObject):
    error_signaling_enabled: bool
    trcv_pwm_mode_enabled: bool
    prop_seg: int
    sync_jump_width: int
    time_seg_1: int
    time_seg_2: int
    pwm_l: int | None = None
    pwm_o: int | None = None
    pwm_s: int | None = None
    ssp_offset: int | None = None


@dataclass
class CanControllerXlConfigurationRequirements(ArObject):
    error_signaling_enabled: bool | None = None
    trcv_pwm_mode_enabled: bool | None = None
    max_sync_jump_width: float | None = None
    min_sync_jump_width: float | None = None
    max_sample_point: float | None = None
    min_sample_point: float | None = None
    max_number_of_time_quanta_per_bit: int | None = None
    min_number_of_time_quanta_per_bit: int | None = None
    max_pwm_l: int | None = None
    min_pwm_l: int | None = None
    max_pwm_o: int | None = None
    min_pwm_o: int | None = None
    max_pwm_s: int | None = None
    min_pwm_s: int | None = None
    max_trcv_delay_compensation_offset: float | None = None
    min_trcv_delay_compensation_offset: float | None = None


@dataclass
class AbstractCanCommunicationControllerAttributes(ArObject):
    can_controller_fd_attributes: CanControllerFdConfiguration | None = None
    can_controller_fd_requirements: CanControllerFdConfigurationRequirements | None = None
    can_controller_xl_attributes: CanControllerXlConfiguration | None = None
    can_controller_xl_requirements: CanControllerXlConfigurationRequirements | None = None


@dataclass
class CanControllerConfiguration(AbstractCanCommunicationControllerAttributes):
    sync_jump_width: int | None = None
    time_seg_1: int | None = None
    time_seg_2: int | None = None


@dataclass
class CanControllerConfigurationRequirements(AbstractCanCommunicationControllerAttributes):
    max_sync_jump_width: float | None = None
    min_sync_jump_width: float | None = None
    max_sample_point: float | None = None
    min_sample_point: float | None = None
    max_number_of_time_quanta_per_bit: int | None = None
    min_number_of_time_quanta_per_bit: int | None = None


CanCommunicationControllerAttributes = TypeVar(
    'CanCommunicationControllerAttributes',
    bound=AbstractCanCommunicationControllerAttributes,
)


class CanCommunicationControllerContent(CommunicationControllerContent):
    def __init__(
            self,
            can_controller_attributes: CanCommunicationControllerAttributes | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.can_controller_attributes = can_controller_attributes


class CanCommunicationController(
    CommunicationController[CanCommunicationControllerContent]
):
    pass


class CanCommunicationConnector(CommunicationConnector):
    def __init__(
            self,
            pnc_wakeup_can_id: int | None = None,
            pnc_wakeup_can_id_mask: int | None = None,
            pnc_wakeup_data_mask: int | None = None,
            pnc_wakeup_dlc: int | None = None,
            pnc_wakeup_can_id_extended: bool | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.pnc_wakeup_can_id = pnc_wakeup_can_id
        self.pnc_wakeup_can_id_mask = pnc_wakeup_can_id_mask
        self.pnc_wakeup_data_mask = pnc_wakeup_data_mask
        self.pnc_wakeup_dlc = pnc_wakeup_dlc
        self.pnc_wakeup_can_id_extended = pnc_wakeup_can_id_extended


class CanPhysicalChannel(PhysicalChannel):
    pass


class CanClusterContent(CommunicationClusterContent[CanPhysicalChannel]):
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


class CanCluster(CommunicationCluster[CanClusterContent]):
    pass
