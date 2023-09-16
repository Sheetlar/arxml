from dataclasses import dataclass
from typing import Iterable

from autosar.ar_object import ArObject
from autosar.element import Element


class SomeIpTPChannel(Element):
    def __init__(
            self,
            separation_time: int | float | str | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.separation_time = separation_time


@dataclass
class SomeIpConnection(ArObject):
    separation_time: int | float | str | None = None
    tp_channel_ref: str | None = None
    tp_sdu_ref: str | None = None
    transport_pdu_ref: str | None = None


class SomeIpConfig(Element):
    def __init__(
            self,
            communication_cluster_ref: str | None = None,
            tp_channels: Iterable[SomeIpTPChannel] | None = None,
            tp_connections: list[SomeIpConnection] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.communication_cluster_ref = communication_cluster_ref
        self.tp_channels = self._set_parent(tp_channels)
        if tp_connections is None:
            tp_connections = []
        self.tp_connections = tp_connections
