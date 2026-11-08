from autosar.model.topology.abstract import CommunicationConnector, CommunicationControllerContent, CommunicationController


class UserDefinedCommunicationConnector(CommunicationConnector):
    pass


class UserDefinedCommunicationControllerContent(CommunicationControllerContent):
    pass


class UserDefinedCommunicationController(
    CommunicationController[UserDefinedCommunicationControllerContent]
):
    pass
