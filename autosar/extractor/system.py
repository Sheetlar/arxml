from itertools import chain

from autosar.extractor.data import (
    DataType,
    LinearConversion,
    RationalConversion,
)
from autosar.extractor.topology import Ecu, CanFrame, CanChannel, Signal
from autosar.model.ar_object import AnyArObject
from autosar.model.can_cluster import CanClusterVariants, CanCluster, CanPhysicalChannel, CanFrameTriggering
from autosar.model.datatype import SwBaseType, CompuMethod
from autosar.model.ecu import EcuInstance
from autosar.model.has_logger import HasLogger
from autosar.model.signal import ISignal, SystemSignal
from autosar.model.system import System


class ArxmlExtractionError(Exception):
    pass


class ExtractedSystem(HasLogger):
    _comm_clusters = (CanClusterVariants,)

    def __init__(
            self,
            ar_system: System,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.ar_system = ar_system
        self._get_fibex_elements_map()
        self._extract_ecus()
        self._build_signals()
        self._extract_topology()

    def _find(self, ref: str) -> AnyArObject | None:
        return self.ar_system.find(ref)

    def _get_fibex_elements_map(self):
        self.fibex_elements = {}
        for fe_ref in self.ar_system.fibex_element_refs:
            if (elem := self._find(fe_ref)) is None:
                self._logger.warning(f'Cannot find fibex element {fe_ref}')
                continue
            if type(elem) not in self.fibex_elements:
                self.fibex_elements[type(elem)] = []
            self.fibex_elements[type(elem)].append(elem)

    def _extract_ecus(self):
        try:
            self.ecus = tuple(
                Ecu(identifier=ecu.ref, name=ecu.name)
                for ecu in self.fibex_elements[EcuInstance]
            )
        except KeyError:
            raise ArxmlExtractionError('No ECU instances found')

    def _build_signals(self):
        try:
            signals: list[ISignal] = self.fibex_elements[ISignal]
        except KeyError:
            raise ArxmlExtractionError('No signals found')
        self._logger.debug(f'Building {len(signals)} signals')
        self._signals = []
        for signal in signals:
            match signal.data_type_policy.lower():
                case 'legacy' | 'override':
                    signal_name, _ = self._extract_signal(signal)
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
                name=signal_name,
                bit_length=signal.length,
                np_dtype=...,
            ))
        return None

    def _extract_signal(self, signal: ISignal):
        system_signal: SystemSignal = self._find(signal.system_signal_ref)
        network_data_props = signal.network_representation_props.single
        if network_data_props is None:
            self._logger.warning(f'Variable network props are not supported, skipping signal {signal.name}')
            return system_signal.name, None
        base_type: SwBaseType = self._find(network_data_props.base_type_ref)
        compu: CompuMethod = self._find(network_data_props.compu_method_ref)
        dtype = DataType(
            identifier=base_type.ref,
            name=base_type.name,
            declaration=base_type.native_declaration,
            size=base_type.size,
            encoding=base_type.type_encoding,
        )
        self._extract_compu(compu)
        return system_signal.name, ...

    def _extract_compu(self, compu: CompuMethod):
        match compu.category:
            case 'IDENTICAL':
                return None
            case 'LINEAR':
                c = compu.int_to_phys.elements[0]
                return LinearConversion(c.numerator / c.denominator, c.offset / c.denominator)
            case 'SCALE_LINEAR':
                ...
            case 'RAT_FUNC':
                c = compu.int_to_phys.elements[0]
                return RationalConversion(
                    c.compu_scale_contents.compu_rational_coeffs.compu_numerator.vs,
                    c.compu_scale_contents.compu_rational_coeffs.compu_denominator.vs,
                )
            case _: ...
        raise NotImplementedError

    def _extract_topology(self):
        clusters = chain.from_iterable(
            c for cls in self._comm_clusters
            if (c := self.fibex_elements.get(cls, None)) is not None
        )
        for cluster in clusters:
            if len(cluster) != 1:
                self._logger.warning(f'Cannot extract communication cluster {cluster.name}: Expected 1 variant, got {len(cluster)}')
                continue
            cluster, = cluster
            if isinstance(cluster, CanCluster):
                self._extract_can_cluster(cluster)
            else:
                self._logger.warning(f'Cluster {cluster.name}: Cluster extraction for type {cluster.__class__.__name__} is not supported')

    def _extract_can_cluster(self, cluster: CanCluster):
        for channel in cluster.physical_channels:
            if not isinstance(channel, CanPhysicalChannel):
                self._logger.error(f'Channel {channel.name}: Unexpected channel type: '
                                   f'Expected {CanPhysicalChannel.__name__}, got {channel.__class__.__name__}')
                continue
            frames = []
            for frame_trig in channel.frame_triggerings:
                if not isinstance(frame_trig, CanFrameTriggering):
                    self._logger.error(f'Triggering {frame_trig.name}: Unexpected triggering type: '
                                       f'Expected {CanFrameTriggering.__name__}, got {frame_trig.__class__.__name__}')
                    continue
                CanFrame(
                    identifier=frame_trig.ref,
                    name=frame_trig.name,
                    frame_id=frame_trig.identifier,
                    pdu=None,
                    providers=(p.parent.parent.ref for p in map(self._find, frame_trig.frame_ports_refs) if p.communication_direction == 'OUT'),
                    consumers=(p.parent.parent.ref for p in map(self._find, frame_trig.frame_ports_refs) if p.communication_direction == 'IN'),
                )
                frames.append(frame_trig.ref)
            cn = CanChannel(identifier=channel.ref, name=channel.name, frames=frames)
            raise RuntimeError  # dummy
