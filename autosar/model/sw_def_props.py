from dataclasses import dataclass

from autosar.model.ar_object import ArObject, ArObjectWithParent
from autosar.model.atp_variation import PropertySet


@dataclass(repr=False)
class SwPointerTargetProps(ArObject):
    target_category: str | None = None
    sw_data_def_props: 'SwDataDefProps | None' = None
    function_pointer_signature_ref: str | None = None


@dataclass(repr=False)
class SwDataDefPropsContent(ArObjectWithParent):
    base_type_ref: str | None = None
    implementation_type_ref: str | None = None
    sw_address_method_ref: str | None = None
    # sw_calibration_access: SwCalibrationAccessEnum | None = None
    # sw_impl_policy: SwImplPolicyEnum | None = None
    sw_pointer_target_props: SwPointerTargetProps | None = None
    sw_record_layout_ref: str | None = None
    compu_method_ref: str | None = None
    data_constraint_ref: str | None = None
    unit_ref: str | None = None
    # TODO: More params


class SwDataDefProps(PropertySet[SwDataDefPropsContent]):
    pass
