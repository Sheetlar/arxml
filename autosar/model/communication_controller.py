from typing import Iterable, TypeVar

from autosar import ArObject
from autosar.model.element import Element


class CouplingPort(Element):
    def __init__(
            self,
            mac_multicast_address: str | None = None,
            default_vlan_ref: str | None = None,
            vlan_modifier_ref: str | None = None,
            coupling_port_role: str | None = None,
            connection_negotiation_behavior: str | None = None,
            mac_layer_type: str | None = None,
            physical_layer_type: str | None = None,
            receive_activity: str | None = None,
            pnc_mapping_refs: list[str] | None = None,
            wakeup_sleep_on_dataline_setup_ref: str | None = None,
            coupling_port_details: None = None,  # TODO: Implement
            plca_props: None = None,  # TODO: Implement
            vlan_membership: Iterable | None = None,  # TODO: Implement
            mac_sec_props: Iterable | None = None,  # TODO: Implement
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if pnc_mapping_refs is None:
            pnc_mapping_refs = []
        self.mac_multicast_address = mac_multicast_address
        self.default_vlan_ref = default_vlan_ref
        self.vlan_membership = vlan_membership
        self.vlan_modifier_ref = vlan_modifier_ref
        self.coupling_port_role = coupling_port_role
        self.connection_negotiation_behavior = connection_negotiation_behavior
        self.mac_layer_type = mac_layer_type
        self.physical_layer_type = physical_layer_type
        self.receive_activity = receive_activity
        self.pnc_mapping_refs = pnc_mapping_refs
        self.wakeup_sleep_on_dataline_setup_ref = wakeup_sleep_on_dataline_setup_ref
        self.coupling_port_details = coupling_port_details
        self.plca_props = plca_props
        self.mac_sec_props = mac_sec_props


class AbstractCanCommunicationControllerAttributes(ArObject):
    ...  # TODO: Implement


CanCommunicationControllerAttributes = TypeVar(
    'CanCommunicationControllerAttributes',
    bound=AbstractCanCommunicationControllerAttributes,
)


class CommunicationController(Element):
    def __init__(
            self,
            wake_up_by_controller_supported: bool | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.wake_up_by_controller_supported = wake_up_by_controller_supported


class CanCommunicationController(CommunicationController):
    def __init__(
            self,
            can_controller_attributes: CanCommunicationControllerAttributes | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.can_controller_attributes = can_controller_attributes


class EthernetCommunicationController(CommunicationController):
    def __init__(
            self,
            mac_unicast_address: str | None = None,
            coupling_ports: Iterable[CouplingPort] | None = None,
            max_receive_buffer_length: int | None = None,
            max_transmit_buffer_length: int | None = None,
            mac_layer_type: str | None = None,
            can_xl_config_ref: str | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.mac_unicast_address = mac_unicast_address
        self.coupling_ports = self._set_parent(coupling_ports)
        self.max_receive_buffer_length = max_receive_buffer_length
        self.max_transmit_buffer_length = max_transmit_buffer_length
        self.mac_layer_type = mac_layer_type
        self.can_xl_config_ref = can_xl_config_ref
        self._find_sets = [self.coupling_ports]
