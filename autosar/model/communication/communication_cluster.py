from typing import Iterable

from autosar.model.ar_object import ArObject
from autosar.model.element import Element


class ISignalTriggering(Element):
    def __init__(
            self,
            i_signal_ref: str | None = None,
            i_signal_group_ref: str | None = None,
            i_signal_port_refs: Iterable[str] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.i_signal_ref = i_signal_ref
        self.i_signal_group_ref = i_signal_group_ref
        self.i_signal_port_refs = self.eval_children(i_signal_port_refs)


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
            i_pdu_port_refs: Iterable[str] | None = None,
            i_signal_triggering_refs: Iterable[str] | None = None,
            sec_oc_crypto_mapping_ref: str | None = None,
            sec_oc_crypto_service_mapping_refs: Iterable[str] | None = None,
            trigger_i_pdu_send_conditions: Iterable[TriggerIPduSendCondition] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.i_pdu_ref = i_pdu_ref
        self.i_pdu_port_refs = self.eval_children(i_pdu_port_refs)
        self.i_signal_triggering_refs = self.eval_children(i_signal_triggering_refs)
        self.sec_oc_crypto_mapping_ref = sec_oc_crypto_mapping_ref
        self.sec_oc_crypto_service_mapping_refs = self.eval_children(sec_oc_crypto_service_mapping_refs)
        self.trigger_i_pdu_send_conditions = self.eval_children(trigger_i_pdu_send_conditions)
