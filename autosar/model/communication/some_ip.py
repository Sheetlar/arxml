from dataclasses import dataclass, field
from typing import Iterable

from autosar.model.ar_object import ArObject
from autosar.model.base import Referrable, Identifiable
from autosar.model.communication.tp import TpConfig
from autosar.model.element import Element
from autosar.model.enums import PduCollectionSemanticsEnum, PduCollectionTriggerEnum


class SoConIPduIdentifier(Referrable):
    def __init__(
            self,
            header_id: int | None = None,
            pdu_triggering_ref: str | None = None,
            pdu_collection_pdu_timeout: float | None = None,
            pdu_collection_semantics: PduCollectionSemanticsEnum | None = None,
            pdu_collection_trigger: PduCollectionTriggerEnum | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.header_id = header_id
        self.pdu_triggering_ref = pdu_triggering_ref
        self.pdu_collection_pdu_timeout = pdu_collection_pdu_timeout
        self.pdu_collection_semantics = pdu_collection_semantics
        self.pdu_collection_trigger = pdu_collection_trigger


class SocketConnectionIPduIdentifierSet(Element):
    def __init__(
            self,
            i_pdu_identifiers: Iterable[SoConIPduIdentifier] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.i_pdu_identifiers = self._set_parent(i_pdu_identifiers)

    @property
    def _findable_children(self) -> Iterable[ArObject]:
        yield from self.i_pdu_identifiers


class SomeIpTpChannel(Identifiable):
    def __init__(
            self,
            burst_size: int | None = None,
            rx_timeout_time: float | None = None,
            separation_time: float | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.burst_size = burst_size
        self.rx_timeout_time = rx_timeout_time
        self.separation_time = separation_time


@dataclass(repr=False)
class SomeIpTpConnection(ArObject):
    tp_channel_ref: str | None = None
    tp_sdu_ref: str | None = None
    transport_pdu_ref: str | None = None
    tp_concurrent_processing_sdu_refs: list[str] = field(default_factory=list)


class SomeIpTpConfig(TpConfig):
    def __init__(
            self,
            tp_channels: Iterable[SomeIpTpChannel] | None = None,  # name
            tp_connections: Iterable[SomeIpTpConnection] | None = None,  # name
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.tp_channels = self._set_parent(tp_channels)
        self.tp_connections = self.eval_children(tp_connections)
