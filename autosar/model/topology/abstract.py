from typing import TypeVar, Iterable, Generic

from autosar.model.ar_object import ArObject, ArObjectWithParent
from autosar.model.atp_variation import PropertySet
from autosar.model.base import Identifiable, DataFilter
from autosar.model.communication.communication_cluster import ISignalTriggering, PduTriggering
from autosar.model.communication.frame import FrameTriggering
from autosar.model.element import Element
from autosar.model.enums import CommunicationDirectionType, PncGatewayTypeEnum, IPduSignalProcessingEnum, HandleInvalidEnum


class CommConnectorPort(Identifiable):
    def __init__(
            self,
            communication_direction: CommunicationDirectionType,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.communication_direction = communication_direction


class FramePort(CommConnectorPort):
    pass


class IPduPort(CommConnectorPort):
    def __init__(
            self,
            i_pdu_signal_processing: IPduSignalProcessingEnum | None = None,
            timestamp_rx_acceptance_window: float | None = None,
            rx_security_verification: bool | None = None,
            use_auth_data_freshness: bool | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.i_pdu_signal_processing = i_pdu_signal_processing
        self.timestamp_rx_acceptance_window = timestamp_rx_acceptance_window
        self.rx_security_verification = rx_security_verification
        self.use_auth_data_freshness = use_auth_data_freshness


class ISignalPort(CommConnectorPort):
    def __init__(
            self,
            data_filter: DataFilter | None = None,
            handle_invalid: HandleInvalidEnum | None = None,
            first_timeout: float | None = None,
            timeout: float | None = None,
            dds_qos_profile_ref: str | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.data_filter = data_filter
        self.handle_invalid = handle_invalid or HandleInvalidEnum.DONT_INVALIDATE
        self.first_timeout = first_timeout
        self.timeout = timeout
        self.dds_qos_profile_ref = dds_qos_profile_ref


AnyCommPort = TypeVar('AnyCommPort', bound=CommConnectorPort)


class CommunicationConnector(Identifiable):
    def __init__(
            self,
            comm_controller_ref: str,
            ecu_comm_port_instances: Iterable[AnyCommPort] | None = None,
            create_ecu_wakeup_source: bool | None = None,
            dynamic_pnc_to_channel_mapping_enabled: bool | None = None,
            explicit_wakeup_channel_refs: Iterable[str] | None = None,
            explicit_wakeup_pnc_refs: Iterable[str] | None = None,
            pnc_filter_array_masks: Iterable[int] | None = None,
            pnc_gateway_type: PncGatewayTypeEnum | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.comm_controller_ref = comm_controller_ref
        self.ecu_comm_port_instances = self._set_parent(ecu_comm_port_instances)
        self.create_ecu_wakeup_source = create_ecu_wakeup_source
        self.dynamic_pnc_to_channel_mapping_enabled = dynamic_pnc_to_channel_mapping_enabled
        self.explicit_wakeup_channel_refs = self.eval_children(explicit_wakeup_channel_refs)
        self.explicit_wakeup_pnc_refs = self.eval_children(explicit_wakeup_pnc_refs)
        self.pnc_filter_array_masks = self.eval_children(pnc_filter_array_masks)
        self.pnc_gateway_type = pnc_gateway_type

    @property
    def _findable_children(self) -> Iterable[ArObject]:
        yield from self.ecu_comm_port_instances


AnyCommunicationConnector = TypeVar('AnyCommunicationConnector', bound=CommunicationConnector)


class CommunicationControllerContent(ArObjectWithParent):
    def __init__(
            self,
            wake_up_by_controller_supported: bool | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.wake_up_by_controller_supported = wake_up_by_controller_supported


CCC = TypeVar('CCC', bound=CommunicationControllerContent)


class CommunicationController(Identifiable, PropertySet[CCC]):
    """Abstract"""


AnyCommunicationController = TypeVar('AnyCommunicationController', bound=CommunicationController)


class PhysicalChannel(Identifiable):
    def __init__(
            self,
            comm_connectors_refs: Iterable[str] | None = None,
            frame_triggerings: Iterable[FrameTriggering] | None = None,
            i_signal_triggerings: Iterable[ISignalTriggering] | None = None,
            pdu_triggerings: Iterable[PduTriggering] | None = None,
            managed_physical_channels_refs: Iterable[str] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.comm_connectors_refs = self.eval_children(comm_connectors_refs)
        self.frame_triggerings = self._set_parent(frame_triggerings)
        self.i_signal_triggerings = self._set_parent(i_signal_triggerings)
        self.pdu_triggerings = self._set_parent(pdu_triggerings)
        self.managed_physical_channels_refs = self.eval_children(managed_physical_channels_refs)

    @property
    def _findable_children(self) -> Iterable[ArObject]:
        yield from self.frame_triggerings
        yield from self.i_signal_triggerings
        yield from self.pdu_triggerings


PC = TypeVar('PC', bound=PhysicalChannel)


class CommunicationClusterContent(ArObjectWithParent, Generic[PC]):
    def __init__(
            self,
            baudrate: int | None = None,
            protocol_name: str | None = None,
            protocol_version: str | None = None,
            physical_channels: Iterable[PC] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.baudrate = baudrate
        self.protocol_name = protocol_name
        self.protocol_version = protocol_version
        self.physical_channels: list[PC] = self._set_parent(physical_channels)


CC = TypeVar('CC', bound=CommunicationClusterContent)


class CommunicationCluster(Element, PropertySet[CC]):
    def _findable_children(self) -> Iterable[ArObject]:
        for v in self.variants:
            yield from v.physical_channels
