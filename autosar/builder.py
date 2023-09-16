from typing import Mapping, Sequence

from autosar.ar_object import ArObject
from autosar.base import InvalidDataTypeRef
from autosar.constant import TextValue, NumericalValue, RecordValueAR4, ArrayValueAR4
from autosar.datatype import ImplementationDataType, ApplicationPrimitiveDataType
from autosar.has_logger import HasLogger


class ValueBuilder(HasLogger):
    """
    Builds AUTOSAR 4 value specifications from python data
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value = None

    def build_from_data_type(
            self,
            data_type: ImplementationDataType | ApplicationPrimitiveDataType,
            raw_value: str | int | float | Mapping | Sequence,
            name: str | None = None,
            ws=None,
            parent: ArObject | None = None,
    ):
        assert (data_type is not None)
        if ws is None:
            ws = data_type.root_ws()
            assert (ws is not None)
        return self._create_from_data_type_internal(ws, name, data_type, raw_value, parent)

    def build(self, label: str, value: str | int | float | Mapping | Sequence):
        return self._create_value_internal(label, value)

    def _create_from_data_type_internal(
            self,
            ws,
            label: str | None,
            data_type: ImplementationDataType | ApplicationPrimitiveDataType,
            raw_value: str | int | float | Mapping | Sequence,
            parent: ArObject | None = None,
    ):
        if isinstance(data_type, (ImplementationDataType, ApplicationPrimitiveDataType)):
            value = None
            data_constraint = None
            variant_props = data_type.variant_props[0]
            if variant_props is not None:
                if variant_props.data_constraint_ref is not None:
                    data_constraint = ws.find(variant_props.data_constraint_ref)
                    if data_constraint is None:
                        raise ValueError(f'{data_type.name}: Invalid DataConstraint reference: {variant_props.data_constraint_ref}')
                if variant_props.compu_method_ref is not None:
                    compu_method = ws.find(variant_props.compu_method_ref)
                    if compu_method is None:
                        raise ValueError(f'{data_type.name}: Invalid CompuMethod reference: {variant_props.compu_method_ref}')
                    if compu_method.category == 'TEXTTABLE':
                        # TODO: check textValue value here
                        value = TextValue(label, str(raw_value))
                    else:
                        # TODO: check rawValue here
                        value = NumericalValue(label, raw_value)
            if value is None:
                if data_type.category == 'VALUE':
                    if isinstance(raw_value, str):
                        value = TextValue(label, raw_value)
                    else:
                        if data_constraint is not None:
                            data_constraint.checkValue(raw_value)
                        value = NumericalValue(label, raw_value)
                elif data_type.category == 'ARRAY':
                    value = self._create_array_value_from_type_internal(ws, label, data_type, raw_value, parent)
                elif data_type.category == 'STRUCTURE':
                    value = self._create_record_value_from_type_internal(ws, label, data_type, raw_value, parent)
                elif data_type.category == 'TYPE_REFERENCE':
                    referenced_type_ref = data_type.get_type_reference()
                    referenced_type = ws.find(referenced_type_ref)
                    if referenced_type is None:
                        raise ValueError(f'Invalid reference: {referenced_type_ref}')
                    value = self._create_from_data_type_internal(ws, label, referenced_type, raw_value, parent)
                else:
                    raise NotImplementedError(data_type.category)
        else:
            raise NotImplementedError(type(data_type))
        return value

    def _create_record_value_from_type_internal(
            self,
            ws,
            label: str | None,
            data_type: ImplementationDataType | ApplicationPrimitiveDataType,
            init_value: str | int | float | Mapping | Sequence,
            parent: ArObject | None = None,
    ):
        value = RecordValueAR4(label, data_type.ref, parent)
        if isinstance(init_value, Mapping):
            a = set()  # datatype elements
            b = set()  # initvalue elements
            for sub_elem in data_type.sub_elements:
                a.add(sub_elem.name)
            for key in init_value.keys():
                b.add(key)
            extra_keys = b - a
            if len(extra_keys) > 0:
                label_str = f'{label}: ' if label is not None else ''
                raise ValueError(f'{label_str}Unknown items in initializer: {", ".join(extra_keys)}')

            for elem in data_type.sub_elements:
                if elem.name in init_value:
                    v = init_value[elem.name]
                    child_props = elem.variant_props[0]
                    if child_props.implementation_type_ref is not None:
                        child_type_ref = child_props.implementation_type_ref
                    else:
                        raise NotImplementedError(f'Could not deduce the type of element "{elem.name}"')
                    child_type = ws.find(child_type_ref)
                    if child_type is None:
                        raise InvalidDataTypeRef(str(child_type_ref))
                    child_value = self._create_from_data_type_internal(ws, elem.name, child_type, v, value)
                    assert (child_value is not None)
                    value.elements.append(child_value)
                else:
                    name_str = f'{elem.name}: ' if elem.name is not None else ''
                    raise ValueError(f'{name_str}Missing initValue field: {elem.name}')
        else:
            raise ValueError('initValue must be a dict')
        return value

    def _create_array_value_from_type_internal(
            self,
            ws,
            label: str | None,
            data_type: ImplementationDataType | ApplicationPrimitiveDataType,
            init_value: str | int | float | Mapping | Sequence,
            parent: ArObject | None = None,
    ):
        value = ArrayValueAR4(label, data_type.ref, None, parent)
        type_array_length = data_type.sub_elements[0].array_size
        if not isinstance(type_array_length, int):
            raise ValueError('dataType has no valid array length')
        if isinstance(init_value, Sequence):
            if isinstance(init_value, str):
                init_value = list(init_value)
                if len(init_value) < type_array_length:
                    # pad with zeros until length matches
                    init_value += [0] * (type_array_length - len(init_value))
                    assert (len(init_value) == type_array_length)
            if len(init_value) > type_array_length:
                self._logger.warning(f'{label}: Excess array init values detected. Expected length={type_array_length}, got {len(init_value)} items')
            if len(init_value) < type_array_length:
                self._logger.warning(f'{label}: Not enough array init values. Expected length={type_array_length}, got {len(init_value)} items')
            i = 0
            child_type_ref = data_type.sub_elements[0].variant_props[0].implementation_type_ref
            child_type = ws.find(child_type_ref)
            if child_type is None:
                raise InvalidDataTypeRef(str(child_type_ref))
            for v in init_value:
                inner_value = self._create_from_data_type_internal(ws, None, child_type, v, None)
                if inner_value is not None:
                    value.elements.append(inner_value)
                else:
                    raise RuntimeError(f'Failed to build value for "{v}"')
                i += 1
                if i >= type_array_length:
                    break
        return value

    def _create_value_internal(self, label: str | None, value: str | int | float | Mapping | Sequence):
        if isinstance(value, str):
            return TextValue(label, value)
        elif isinstance(value, (int, float)):
            return NumericalValue(label, value)
        elif isinstance(value, Mapping):
            record_value = RecordValueAR4(label)
            for key in value.keys():
                inner_value = value[key]
                child_value = self._create_value_internal(key, inner_value)
                if child_value is not None:
                    record_value.elements.append(child_value)
                else:
                    raise RuntimeError(f'Failed to build init-value for "{inner_value}"')
            return record_value
        elif isinstance(value, Sequence):
            array_value = ArrayValueAR4(label)
            for inner_value in value:
                child_value = self._create_value_internal(None, inner_value)
                if child_value is not None:
                    array_value.elements.append(child_value)
                else:
                    raise RuntimeError(f'Failed to build init-value for "{inner_value}"')
            return array_value
        else:
            raise NotImplementedError(type(value))
