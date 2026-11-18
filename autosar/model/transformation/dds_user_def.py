from autosar.model.transformation.signal import (
    TransformationISignalPropsContent,
    AbstractTransformationISignalProps,
)
from autosar.model.transformation.sets import (
    AbstractTransformationDescription,
    AbstractTransformationProps,
)


class DdsTransformationISignalPropsContent(TransformationISignalPropsContent):
    pass


class DdsTransformationISignalProps(
    AbstractTransformationISignalProps[DdsTransformationISignalPropsContent]
):
    pass


class DdsTransformationDescription(AbstractTransformationDescription):
    pass


class UserDefinedTransformationISignalPropsContent(TransformationISignalPropsContent):
    pass


class UserDefinedTransformationISignalProps(
    AbstractTransformationISignalProps[UserDefinedTransformationISignalPropsContent]
):
    pass


class UserDefinedTransformationDescription(AbstractTransformationDescription):
    pass


class UserDefinedTransformationProps(AbstractTransformationProps):
    pass
