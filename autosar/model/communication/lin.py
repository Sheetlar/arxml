from typing import Iterable

from autosar.model.communication.frame import Frame


class LinEventTriggeredFrame(Frame):
    def __init__(
            self,
            collision_resolving_schedule_ref: str | None = None,
            lin_unconditional_frame_refs: Iterable[str] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.collision_resolving_schedule_ref = collision_resolving_schedule_ref
        self.lin_unconditional_frame_refs = self.eval_children(lin_unconditional_frame_refs)


class LinSporadicFrame(Frame):
    def __init__(
            self,
            substituted_frame_refs: Iterable[str] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.substituted_frame_refs = self.eval_children(substituted_frame_refs)


class LinUnconditionalFrame(Frame):
    pass
