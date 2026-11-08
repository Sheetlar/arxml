from abc import ABC

from autosar.extractor.conversion import (
    AnyConversion,
    LinearConversion,
    NumericConversion,
    ConversionInterval,
    NumericAndMapConversion,
    ConstantConversion,
    RationalConversion,
    MapConversion,
    BitfieldConversion,
)
from autosar.extractor.data import Signal, DataType, Unit
from autosar.extractor.system.extractor_base import AbstractExtractor, ArxmlExtractionError
from autosar.model.compu import CompuScaleRationalFormula, CompuScaleConstantContents
from autosar.model.datatype import SwBaseType, CompuMethod, Unit as ArUnit
from autosar.model.signal import ISignal, SystemSignal, ISignalGroup, SystemSignalGroup


class SignalExtractionModule(AbstractExtractor, ABC):
    def _build_signal_groups(self):
        self._signal_groups = []
        try:
            groups: list[ISignalGroup] = self.fibex_elements[ISignalGroup]
        except KeyError:
            self._logger.debug('No signal groups found')
            return None
        return groups  # TODO: Handle groups

    def _build_signals(self):
        try:
            signals: list[ISignal] = self.fibex_elements[ISignal]
        except KeyError:
            raise ArxmlExtractionError('No signals found')
        self._logger.debug(f'Building {len(signals)} signals')
        self._signals: list[Signal] = []
        for signal in signals:
            match signal.data_type_policy.lower():
                case 'legacy' | 'override':
                    signal_name, dt, compu, unit = self._extract_simple_signal(signal)
                case 'network-representation-from-com-spec':
                    self._logger.warning(f'ComSpec is not supported, signal {signal.name} will be ignored')
                    continue
                case 'transforming-i-signal':
                    self._logger.warning(f'ComSpec is not supported, signal {signal.name} will be ignored')
                    continue
                case _:
                    self._logger.warning(f'Signal {signal.name} has unknown type policy {signal.data_type_policy}, ignoring')
                    continue

            self._signals.append(Signal(
                identifier=signal.ref,
                alias=signal.system_signal_ref,
                name=signal_name,
                bit_length=signal.length,
                dtype=dt,
                conversion=compu,
                unit=unit,
            ))

    def _extract_simple_signal(self, signal: ISignal):
        system_signal: SystemSignal = self._find(signal.system_signal_ref)
        net_props = signal.network_representation_props.single
        phys_props = system_signal.physical_props.single
        if net_props is None or phys_props is None:
            self._logger.warning(f'Variable network props are not supported, skipping signal {signal.name}')
            return system_signal.name, None, None, None
        base_type: SwBaseType = self._find(net_props.base_type_ref)
        compu: CompuMethod = self._find(phys_props.compu_method_ref)
        try:
            unit_ref = system_signal.physical_props.single.unit_ref or compu.unit_ref
        except AttributeError:
            unit_ref = compu.unit_ref
        dtype = DataType(
            name=base_type.name,
            declaration=base_type.native_declaration,
            size=base_type.size,
            encoding=base_type.type_encoding,
            is_array=signal.i_signal_type.lower() == 'array',
        )
        conversion = self._extract_compu(compu)
        unit = self._extract_unit(unit_ref)
        return system_signal.name, dtype, conversion, unit

    def _extract_unit(self, unit_ref: str | None) -> Unit | None:
        if unit_ref is None:
            return None
        unit: ArUnit | None = self._find(unit_ref)
        if unit is None:
            return None
        return Unit(
            symbol=unit.display_name,
            unit_factor=unit.factor,
            unit_offset=unit.offset,
        )

    def _extract_compu(self, compu: CompuMethod) -> AnyConversion | None:
        match compu.category:
            case 'IDENTICAL':
                return None
            case 'LINEAR':
                c = compu.int_to_phys.elements[0]
                return LinearConversion(c.numerator / c.denominator, c.offset / c.denominator)
            case 'SCALE_LINEAR':
                return NumericConversion((
                    ConversionInterval(
                        min=scale.lower_limit,
                        max=scale.upper_limit,
                        convertion=LinearConversion(scale.numerator / scale.denominator, scale.offset / scale.denominator),
                    )
                    for scale in compu.int_to_phys.elements
                ))
            case 'SCALE_LINEAR_AND_TEXTTABLE':
                return NumericAndMapConversion(
                    numeric_intervals=(
                        ConversionInterval(
                            min=scale.lower_limit,
                            max=scale.upper_limit,
                            convertion=LinearConversion(scale.numerator / scale.denominator, scale.offset / scale.denominator),
                        )
                        for scale in compu.int_to_phys.elements
                        if isinstance(scale.compu_scale_contents, CompuScaleRationalFormula)
                    ),
                    map_intervals=(
                        ConversionInterval(
                            min=scale.lower_limit,
                            max=scale.upper_limit,
                            convertion=ConstantConversion(scale.text_value),
                        )
                        for scale in compu.int_to_phys.elements
                        if isinstance(scale.compu_scale_contents, CompuScaleConstantContents)
                    ),
                )
            case 'RAT_FUNC':
                c = compu.int_to_phys.elements[0]
                return RationalConversion(
                    c.compu_scale_contents.compu_rational_coeffs.compu_numerator.vs,
                    c.compu_scale_contents.compu_rational_coeffs.compu_denominator.vs,
                )
            case 'SCALE_RAT_FUNC':
                return NumericConversion((
                    ConversionInterval(
                        min=scale.lower_limit,
                        max=scale.upper_limit,
                        convertion=RationalConversion(
                            scale.compu_scale_contents.compu_rational_coeffs.compu_numerator.vs,
                            scale.compu_scale_contents.compu_rational_coeffs.compu_denominator.vs,
                        )
                    )
                    for scale in compu.int_to_phys.elements
                ))
            case 'SCALE_RATIONAL_AND_TEXTTABLE':
                return NumericAndMapConversion(
                    numeric_intervals=(
                        ConversionInterval(
                            min=scale.lower_limit,
                            max=scale.upper_limit,
                            convertion=RationalConversion(
                                scale.compu_scale_contents.compu_rational_coeffs.compu_numerator.vs,
                                scale.compu_scale_contents.compu_rational_coeffs.compu_denominator.vs,
                            )
                        )
                        for scale in compu.int_to_phys.elements
                        if isinstance(scale.compu_scale_contents, CompuScaleRationalFormula)
                    ),
                    map_intervals=(
                        ConversionInterval(
                            min=scale.lower_limit,
                            max=scale.upper_limit,
                            convertion=ConstantConversion(scale.text_value),
                        )
                        for scale in compu.int_to_phys.elements
                        if isinstance(scale.compu_scale_contents, CompuScaleConstantContents)
                    ),
                )
            case 'TEXTTABLE':
                return MapConversion((
                    ConversionInterval(
                        min=scale.lower_limit,
                        max=scale.upper_limit,
                        convertion=ConstantConversion(scale.text_value),
                    )
                    for scale in compu.int_to_phys.elements
                ))
            case 'TAB_NOINTP':
                return MapConversion((
                    ConversionInterval(
                        min=scale.lower_limit,
                        max=scale.upper_limit,
                        convertion=ConstantConversion(scale.compu_scale_contents.compu_const.compu_const_content_type.v),
                    )
                    for scale in compu.int_to_phys.elements
                ))
            case 'BITFIELD_TEXTTABLE':
                return BitfieldConversion((
                    (
                        scale.mask,
                        ConversionInterval(
                            min=scale.lower_limit,
                            max=scale.upper_limit,
                            convertion=ConstantConversion(scale.text_value),
                        ),
                    )
                    for scale in compu.int_to_phys.elements
                ))
            case _:
                self._logger.warning(f'Unexpected CompuMethod category "{compu.category}", defaulting to IDENTICAL')
                return None
