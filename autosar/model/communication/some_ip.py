from typing import Iterable

from autosar.model.ar_object import ArObject
from autosar.model.base import Referrable
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
