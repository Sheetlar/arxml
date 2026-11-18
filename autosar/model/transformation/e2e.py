from typing import Iterable

from autosar.model.enums import DataIdModeEnum, EndToEndProfileBehaviorEnum
from autosar.model.transformation.signal import (
    TransformationISignalPropsContent,
    AbstractTransformationISignalProps,
)
from autosar.model.transformation.sets import AbstractTransformationDescription


class EndToEndTransformationISignalPropsContent(TransformationISignalPropsContent):
    def __init__(
            self,
            data_ids: Iterable[int] | None = None,
            data_length: int = 0,
            max_data_length: int | None = None,
            min_data_length: int | None = None,
            source_id: int | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.data_ids = self.eval_children(data_ids)
        self.data_length = data_length
        self.max_data_length = max_data_length
        self.min_data_length = min_data_length
        self.source_id = source_id


class EndToEndTransformationISignalProps(
    AbstractTransformationISignalProps[EndToEndTransformationISignalPropsContent]
):
    pass


class EndToEndTransformationDescription(AbstractTransformationDescription):
    def __init__(
            self,
            profile_name: str,
            data_id_mode: DataIdModeEnum | None = None,
            counter_offset: int | None = None,
            crc_offset: int | None = None,
            data_id_nibble_offset: int | None = None,
            offset: int | None = None,
            clear_from_valid_to_invalid: bool | None = None,
            e2e_profile_compatibility_props_ref: str | None = None,
            max_delta_counter: int | None = None,
            max_error_state_init: int | None = None,
            max_error_state_invalid: int | None = None,
            max_error_state_valid: int | None = None,
            max_no_new_or_repeated_data: int | None = None,
            min_ok_state_init: int | None = None,
            min_ok_state_invalid: int | None = None,
            min_ok_state_valid: int | None = None,
            profile_behavior: EndToEndProfileBehaviorEnum | None = None,
            sync_counter_init: int | None = None,
            upper_header_bits_to_shift: int | None = None,
            window_size_init: int | None = None,
            window_size_invalid: int | None = None,
            window_size_valid: int | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.profile_name = profile_name
        self.data_id_mode = data_id_mode
        self.counter_offset = counter_offset
        self.crc_offset = crc_offset
        self.data_id_nibble_offset = data_id_nibble_offset
        self.offset = offset
        self.clear_from_valid_to_invalid = clear_from_valid_to_invalid
        self.e2e_profile_compatibility_props_ref = e2e_profile_compatibility_props_ref
        self.max_delta_counter = max_delta_counter
        self.max_error_state_init = max_error_state_init
        self.max_error_state_invalid = max_error_state_invalid
        self.max_error_state_valid = max_error_state_valid
        self.max_no_new_or_repeated_data = max_no_new_or_repeated_data
        self.min_ok_state_init = min_ok_state_init
        self.min_ok_state_invalid = min_ok_state_invalid
        self.min_ok_state_valid = min_ok_state_valid
        self.profile_behavior = profile_behavior
        self.sync_counter_init = sync_counter_init
        self.upper_header_bits_to_shift = upper_header_bits_to_shift
        self.window_size_init = window_size_init
        self.window_size_invalid = window_size_invalid
        self.window_size_valid = window_size_valid
