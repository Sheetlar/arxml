from dataclasses import dataclass
from typing import TypeVar

from autosar.model.ar_object import ArObject
from autosar.model.base import Identifiable, Referrable
from autosar.model.element import Element


class TpConnectionIdent(Referrable):
    pass


@dataclass(repr=False)
class TpConnection(ArObject):
    ident: TpConnectionIdent | None = None

    def __post_init__(self):
        if self.ident is not None:
            self.ident.parent = self


class TpAddress(Identifiable):
    def __init__(
            self,
            tp_address: int,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.tp_address = tp_address


class TpConfig(Element):
    def __init__(
            self,
            communication_cluster_ref: str,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.communication_cluster_ref = communication_cluster_ref


AnyTpConfig = TypeVar('AnyTpConfig', bound=TpConfig)
