from abc import ABC
from itertools import chain

from autosar.extractor.system.extractor_base import AbstractExtractor
from autosar.extractor.topology import CanCluster, CanFrame
from autosar.extractor.transport import Pdu
from autosar.misc import not_none
from autosar.model.can_cluster import CanClusterVariants, CanFrameTriggering, CanCluster as ArCanCluster
from autosar.model.enums import CommunicationDirectionType, CanAddressingModeType
from autosar.model.frame import CanFrame as ArCanFrame


class TopologyExtractionModule(AbstractExtractor, ABC):
    _supported_cluster_types = (CanClusterVariants,)

    def _extract_topology(self):
        self.clusters: list[CanCluster] = []
        clusters = chain.from_iterable(
            c for cls in self._supported_cluster_types
            if (c := self.fibex_elements.get(cls, None)) is not None
        )
        for cluster in clusters:
            if len(cluster) != 1:
                self._logger.warning(f'Cannot extract communication cluster {cluster.name}: Expected 1 variant, got {len(cluster)}')
                continue
            cluster, = cluster
            match cluster:
                case ArCanCluster():
                    self._extract_can_cluster(cluster)
                case _:
                    self._logger.warning(f'Cluster {cluster.name}: Cluster extraction for type {cluster.__class__.__name__} is not supported')

    def _extract_can_cluster(self, ar_cluster: ArCanCluster):
        frame_trig: list[CanFrameTriggering] = ar_cluster.physical_channel.frame_triggerings
        frames = filter(not_none, map(self._extract_can_frame, frame_trig))
        cluster = CanCluster(
            identifier=ar_cluster.ref,
            name=ar_cluster.name,
            frames=frames,
        )
        self.clusters.append(cluster)

    def _extract_can_frame(self, frame_trig: CanFrameTriggering) -> CanFrame | None:
        def get_pdu_ref() -> Pdu | None:
            if len(ar_frame.pdu_to_frame_mappings) == 0:
                return None
            mapping = ar_frame.pdu_to_frame_mappings[0]  # [constr_3036]
            try:
                return Pdu.get(mapping.pdu_ref)
            except KeyError:
                self._logger.warning(f'Unknown PDU {mapping.pdu_ref} for frame {ar_frame.name}')
                return None

        ar_frame: ArCanFrame = self._find(frame_trig.frame_ref)
        if frame_trig.identifier is None:
            self._logger.warning(f'Frame identifier not provided for frame {ar_frame.name}, ignoring')
            return None
        frame = CanFrame(
            identifier=frame_trig.ref,
            name=ar_frame.name,
            frame_id=frame_trig.identifier,
            size=ar_frame.frame_length,
            pdu=get_pdu_ref(),
            providers=(
                p.parent.parent.ref
                for p in map(self._find, frame_trig.frame_ports_refs)
                if p.communication_direction is CommunicationDirectionType.OUT
            ),
            consumers=(
                p.parent.parent.ref
                for p in map(self._find, frame_trig.frame_ports_refs)
                if p.communication_direction is CommunicationDirectionType.IN
            ),
            extended_addressing=frame_trig.can_addressing_mode is CanAddressingModeType.EXTENDED,
        )
        return frame
