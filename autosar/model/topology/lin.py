from dataclasses import dataclass
from typing import Iterable, TypeVar

from autosar.misc import not_none
from autosar.model.ar_object import ArObject, ArObjectWithParent
from autosar.model.base import Referrable
from autosar.model.topology.abstract import (
    CommunicationControllerContent,
    CommunicationController,
    CommunicationConnector,
)


@dataclass
class LinConfigurableFrame(ArObject):
    frame_ref: str
    message_id: int | None = None


@dataclass
class LinOrderedConfigurableFrame(ArObject):
    frame_ref: str
    index: int


@dataclass
class LinErrorResponse(ArObject):
    response_error_ref: str | None = None


class LinSlaveConfigIdent(Referrable):
    pass


class LinSlaveConfig(ArObjectWithParent):
    def __init__(
            self,
            configured_nad: int | None = None,
            function_id: int | None = None,
            ident: LinSlaveConfigIdent | None = None,
            initial_nad: int | None = None,
            lin_configurable_frames: Iterable[LinConfigurableFrame] | None = None,
            lin_error_response: LinErrorResponse | None = None,
            lin_ordered_configurable_frames: Iterable[LinOrderedConfigurableFrame] | None = None,
            protocol_version: str | None = None,
            supplier_id: int | None = None,
            variant_id: int | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if ident is not None:
            ident.parent = self
        self.configured_nad = configured_nad
        self.function_id = function_id
        self.ident = ident
        self.initial_nad = initial_nad
        self.lin_configurable_frames = self.eval_children(lin_configurable_frames)
        self.lin_error_response = lin_error_response
        self.lin_ordered_configurable_frames = self.eval_children(lin_ordered_configurable_frames)
        self.protocol_version = protocol_version
        self.supplier_id = supplier_id
        self.variant_id = variant_id


class LinCommunicationControllerContent(CommunicationControllerContent):
    def __init__(
            self,
            protocol_version: str,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.protocol_version = protocol_version


class LinMasterContent(LinCommunicationControllerContent):
    def __init__(
            self,
            lin_slaves: Iterable[LinSlaveConfig] | None = None,
            time_base: float | None = None,
            time_base_jitter: float | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.lin_slaves = self._set_parent(lin_slaves)
        self.time_base = time_base
        self.time_base_jitter = time_base_jitter


class LinSlaveContent(LinCommunicationControllerContent):
    def __init__(
            self,
            assigned_nad: bool | None = None,
            configured_nad: int | None = None,
            function_id: int | None = None,
            initial_nad: int | None = None,
            lin_error_response: LinErrorResponse | None = None,
            nas_timeout: float | None = None,
            supplier_id: int | None = None,
            variant_id: int | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.assigned_nad = assigned_nad
        self.configured_nad = configured_nad
        self.function_id = function_id
        self.initial_nad = initial_nad
        self.lin_error_response = lin_error_response
        self.nas_timeout = nas_timeout
        self.supplier_id = supplier_id
        self.variant_id = variant_id


LinCCC = TypeVar('LinCCC', bound=LinCommunicationControllerContent)


class LinCommunicationController(CommunicationController[LinCCC]):
    pass


class LinMaster(LinCommunicationController[LinMasterContent]):
    @property
    def _findable_children(self) -> Iterable[ArObject]:
        for v in self.variants:
            yield from filter(not_none, (s.ident for s in v.lin_slaves))


class LinSlave(LinCommunicationController[LinSlaveContent]):
    pass


class LinCommunicationConnector(CommunicationConnector):
    def __init__(
            self,
            lin_configurable_frames: Iterable[LinConfigurableFrame] | None = None,
            lin_ordered_configurable_frames: Iterable[LinOrderedConfigurableFrame] | None = None,
            schedule_change_next_time_base: bool | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.lin_configurable_frames = self.eval_children(lin_configurable_frames)
        self.lin_ordered_configurable_frames = self.eval_children(lin_ordered_configurable_frames)
        self.schedule_change_next_time_base = schedule_change_next_time_base
