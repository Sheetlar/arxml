from dataclasses import dataclass
from typing import Iterable

from autosar.model.ar_object import ArObject
from autosar.model.base import Limit, Identifiable
from autosar.model.communication.do_ip import DoIpConfig
from autosar.model.element import Element
from autosar.model.topology.abstract import AnyCommunicationConnector, AnyCommunicationController


@dataclass
class ClientIdRange(ArObject):
    lower_limit: Limit | None
    upper_limit: Limit | None


class EcuPartition(Identifiable):
    def __init__(
            self,
            exec_in_user_mode: bool,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.exec_in_user_mode = exec_in_user_mode


class EcuInstance(Element):
    def __init__(
            self,
            comm_controllers: Iterable[AnyCommunicationController] | None = None,
            connectors: Iterable[AnyCommunicationConnector] | None = None,
            partitions: Iterable[EcuPartition] | None = None,
            diagnostic_address: int | None = None,
            associated_com_i_pdu_group_refs: Iterable[str] | None = None,
            associated_cp_si_group_refs: Iterable[str] | None = None,
            associated_pdu_r_i_pdu_group_refs: Iterable[str] | None = None,
            channel_synchronous_wakeup: bool | None = None,
            client_id_range: ClientIdRange | None = None,
            com_configuration_gw_time_base: float | None = None,
            com_configuration_rx_time_base: float | None = None,
            com_configuration_tx_time_base: float | None = None,
            com_enable_mdt_for_cyclic_transmission: bool | None = None,
            eth_switch_port_group_derivation: bool | None = None,
            ecu_task_proxy_refs: Iterable[str] | None = None,
            firewall_rule_refs: Iterable[str] | None = None,
            pnc_nm_request: bool | None = None,
            pnc_synchronous_wakeup: bool | None = None,
            pnc_prepare_sleep_timer: float | None = None,
            pn_reset_time: float | None = None,
            sleep_mode_supported: bool | None = None,
            tcp_ip_icmp_props_ref: str | None = None,
            tcp_ip_props_ref: str | None = None,
            v2x_supported: str | None = None,
            wake_up_over_bus_supported: bool | None = None,
            dlt_config: None = None,  # TODO: Implement
            do_ip_config: DoIpConfig | None = None,
            j1939_node: None = None,  # TODO: Implement
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.comm_controllers = self._set_parent(comm_controllers)
        self.connectors = self._set_parent(connectors)
        self.partitions = self._set_parent(partitions)
        self.diagnostic_address = diagnostic_address
        self.associated_com_i_pdu_group_refs = self.eval_children(associated_com_i_pdu_group_refs)
        self.associated_consumed_provided_service_instance_group_refs = self.eval_children(associated_cp_si_group_refs)
        self.associated_pdu_r_i_pdu_group_refs = self.eval_children(associated_pdu_r_i_pdu_group_refs)
        self.channel_synchronous_wakeup = channel_synchronous_wakeup
        self.client_id_range = client_id_range
        self.com_configuration_gw_time_base = com_configuration_gw_time_base
        self.com_configuration_rx_time_base = com_configuration_rx_time_base
        self.com_configuration_tx_time_base = com_configuration_tx_time_base
        self.com_enable_mdt_for_cyclic_transmission = com_enable_mdt_for_cyclic_transmission
        self.eth_switch_port_group_derivation = eth_switch_port_group_derivation
        self.ecu_task_proxy_refs = self.eval_children(ecu_task_proxy_refs)
        self.firewall_rule_refs = self.eval_children(firewall_rule_refs)
        self.pnc_nm_request = pnc_nm_request
        self.pnc_synchronous_wakeup = pnc_synchronous_wakeup
        self.pnc_prepare_sleep_timer = pnc_prepare_sleep_timer
        self.pn_reset_time = pn_reset_time
        self.sleep_mode_supported = sleep_mode_supported
        self.tcp_ip_icmp_props_ref = tcp_ip_icmp_props_ref
        self.tcp_ip_props_ref = tcp_ip_props_ref
        self.v2x_supported = v2x_supported
        self.wake_up_over_bus_supported = wake_up_over_bus_supported
        self.dlt_config = dlt_config
        self.do_ip_config = self._set_parent_single(do_ip_config)
        self.j1939_node = j1939_node

    @property
    def _findable_children(self) -> Iterable[ArObject]:
        yield from self.comm_controllers
        yield from self.connectors
        yield from self.partitions
        if (cfg := self.do_ip_config) is not None:
            yield from cfg.doip_interfaces
            if cfg.logic_address is not None:
                yield cfg.logic_address
