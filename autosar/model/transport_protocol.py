from dataclasses import dataclass
from typing import TypeVar, Iterable

from autosar.misc import filter_none
from autosar.model.ar_object import ArObject
from autosar.model.base import Identifiable, Referrable
from autosar.model.element import Element
from autosar.model.enums import (
    CanTpChannelModeType,
    CanTpAddressingFormatType,
    NetworkTargetAddressType,
)


class TpConnectionIdent(Referrable):
    pass


@dataclass(repr=False)
class TpConnection(ArObject):
    ident: TpConnectionIdent | None = None

    def __post_init__(self):
        if self.ident is not None:
            self.ident.parent = self


class CanTpConnection(TpConnection):
    def __init__(
            self,
            addressing_format: CanTpAddressingFormatType,
            can_tp_channel_ref: str,
            data_pdu_ref: str,
            padding_activation: bool,
            tp_sdu_ref: str,
            cancellation: bool | None = None,
            flow_control_pdu_ref: str | None = None,
            max_block_size: int | None = None,
            multicast_ref: str | None = None,
            receiver_refs: Iterable[str] | None = None,
            ta_type: NetworkTargetAddressType | None = None,
            timeout_br: float | None = None,
            timeout_bs: float | None = None,
            timeout_cr: float | None = None,
            timeout_cs: float | None = None,
            transmitter_ref: str | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.addressing_format = addressing_format
        self.can_tp_channel_ref = can_tp_channel_ref
        self.data_pdu_ref = data_pdu_ref
        self.padding_activation = padding_activation
        self.tp_sdu_ref = tp_sdu_ref
        self.cancellation = cancellation
        self.flow_control_pdu_ref = flow_control_pdu_ref
        self.max_block_size = max_block_size
        self.multicast_ref = multicast_ref
        self.receiver_refs = self.eval_children(receiver_refs)
        self.ta_type = ta_type
        self.timeout_br = timeout_br
        self.timeout_bs = timeout_bs
        self.timeout_cr = timeout_cr
        self.timeout_cs = timeout_cs
        self.transmitter_ref = transmitter_ref


class CanTpAddress(Element):
    def __init__(
            self,
            tp_address: int,
            tp_address_extension_value: int | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.tp_address = tp_address
        self.tp_address_extension_value = tp_address_extension_value


class CanTpChannel(Element):
    def __init__(
            self,
            channel_id: int | None = None,
            channel_mode: CanTpChannelModeType | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.channel_id = channel_id
        self.channel_mode = channel_mode


@dataclass(repr=False)
class CanTpEcu(ArObject):
    ecu_instance_ref: str
    cycle_time_main_function: float | None = None


class CanTpNode(Element):
    def __init__(
            self,
            connector_ref: str | None = None,
            tp_address_ref: str | None = None,
            max_fc_wait: int | None = None,
            st_min: float | None = None,
            timeout_ar: float | None = None,
            timeout_as: float | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.connector_ref = connector_ref
        self.tp_address_ref = tp_address_ref
        self.max_fc_wait = max_fc_wait
        self.st_min = st_min
        self.timeout_ar = timeout_ar
        self.timeout_as = timeout_as


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


class CanTpConfig(TpConfig):
    def __init__(
            self,
            tp_addresses: Iterable[CanTpAddress] | None = None,
            tp_channels: Iterable[CanTpChannel] | None = None,
            tp_connections: Iterable[CanTpConnection] | None = None,
            tp_ecus: Iterable[CanTpEcu] | None = None,
            tp_nodes: Iterable[CanTpNode] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.tp_addresses = self._set_parent(tp_addresses)
        self.tp_channels = self._set_parent(tp_channels)
        self.tp_connections = self._set_parent(tp_connections)
        self.tp_ecus = self.eval_children(tp_ecus)
        self.tp_nodes = self._set_parent(tp_nodes)

    @property
    def _findable_children(self) -> Iterable[ArObject]:
        yield from self.tp_addresses
        yield from self.tp_channels
        yield from filter_none(c.ident for c in self.tp_connections)
        yield from self.tp_nodes


AnyTpConfig = TypeVar('AnyTpConfig', bound=TpConfig)
