from itertools import chain
from typing import Iterable

from autosar.model.ar_object import ArObject
from autosar.model.element import Element


class FrameTriggering(Element):
    def __init__(
            self,
            frame_ref: str,
            frame_ports_refs: list[str] | None = None,
            pdu_triggerings_refs: list[str] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if frame_ports_refs is None:
            frame_ports_refs = []
        if pdu_triggerings_refs is None:
            pdu_triggerings_refs = []
        self.frame_ref = frame_ref
        self.frame_ports_refs = frame_ports_refs
        self.pdu_triggerings_refs = pdu_triggerings_refs


class ISignalTriggering(Element):
    def __init__(
            self,
            i_signal_ref: str | None = None,
            i_signal_group_ref: str | None = None,
            i_signal_port_refs: list[str] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if i_signal_port_refs is None:
            i_signal_port_refs = []
        self.i_signal_ref = i_signal_ref
        self.i_signal_group_ref = i_signal_group_ref
        self.i_signal_port_refs = i_signal_port_refs


class TriggerIPduSendCondition(ArObject):
    def __init__(
            self,
            mode_declaration_refs: list[str],
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.mode_declaration_refs = mode_declaration_refs


class PduTriggering(Element):
    def __init__(
            self,
            i_pdu_ref: str,
            i_pdu_port_refs: list[str] | None = None,
            i_signal_triggering_refs: list[str] | None = None,
            sec_oc_crypto_mapping_ref: str | None = None,
            trigger_i_pdu_send_conditions: list[TriggerIPduSendCondition] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if i_pdu_port_refs is None:
            i_pdu_port_refs = []
        if i_signal_triggering_refs is None:
            i_signal_triggering_refs = []
        if trigger_i_pdu_send_conditions is None:
            trigger_i_pdu_send_conditions = []
        self.i_pdu_ref = i_pdu_ref
        self.i_pdu_port_refs = i_pdu_port_refs
        self.i_signal_triggering_refs = i_signal_triggering_refs
        self.sec_oc_crypto_mapping_ref = sec_oc_crypto_mapping_ref
        self.trigger_i_pdu_send_conditions = trigger_i_pdu_send_conditions


class PhysicalChannel(Element):
    def __init__(
            self,
            comm_connectors_refs: list[str] | None = None,
            frame_triggerings: Iterable[FrameTriggering] | None = None,
            i_signal_triggerings: Iterable[ISignalTriggering] | None = None,
            pdu_triggerings: Iterable[PduTriggering] | None = None,
            managed_physical_channels_refs: list[str] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.comm_connectors_refs = comm_connectors_refs
        self.frame_triggerings = self._set_parent(frame_triggerings)
        self.i_signal_triggerings = self._set_parent(i_signal_triggerings)
        self.pdu_triggerings = self._set_parent(pdu_triggerings)
        self.managed_physical_channels_refs = managed_physical_channels_refs

    def find(self, ref: str, role: str | None = None) -> Element | None:
        name, _, more = ref.partition('/')
        # noinspection PyTypeChecker
        referrables = chain(self.frame_triggerings, self.i_signal_triggerings, self.pdu_triggerings)
        for element in referrables:
            if element.name == name:
                if more == '':
                    return element
                return element.find(more, role)
        return None


class CommunicationCluster(Element):
    def __init__(
            self,
            baudrate: int | None = None,
            protocol_name: str | None = None,
            protocol_version: str | None = None,
            physical_channels: Iterable[PhysicalChannel] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.baudrate = baudrate
        self.protocol_name = protocol_name
        self.protocol_version = protocol_version
        self.physical_channels = self._set_parent(physical_channels)

    def find(self, ref: str, role: str | None = None) -> Element | None:
        name, _, more = ref.partition('/')
        for channel in self.physical_channels:
            if channel.name == name:
                if more == '':
                    return channel
                return channel.find(more, role)
        return None
