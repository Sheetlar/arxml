from typing import Iterable

from autosar.misc import filter_none
from autosar.model.ar_object import ArObject

from autosar.model.communication.frame import Frame
from autosar.model.communication.tp import TpConnection, TpConfig


class GenericEthernetFrame(Frame):
    pass


class Ieee1722TpFrame(Frame):
    def __init__(
            self,
            relative_representation_time: float | None = None,
            stream_identifier: int | None = None,
            sub_type: int | None = None,
            version: int | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.relative_representation_time = relative_representation_time
        self.stream_identifier = stream_identifier
        self.sub_type = sub_type
        self.version = version


class UserDefinedEthernetFrame(Frame):
    pass


class EthTpConnection(TpConnection):
    def __init__(
            self,
            tp_sdu_refs: Iterable[str] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.tp_sdu_refs = self.eval_children(tp_sdu_refs)


class EthTpConfig(TpConfig):
    def __init__(
            self,
            tp_connections: Iterable[EthTpConnection] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.tp_connections = self._set_parent(tp_connections)

    @property
    def _findable_children(self) -> Iterable[ArObject]:
        yield from filter_none(c.ident for c in self.tp_connections)
