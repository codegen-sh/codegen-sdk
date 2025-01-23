from enum import IntFlag, auto
from typing import TypedDict

from typing_extensions import ReadOnly

from codegen.sdk.writer_decorators import apidoc


@apidoc
class MessageType(IntFlag):
    """Destination of the message

    Attributes:
        CODEGEN: Rendered in the diff preview
        GITHUB: Posted as a comment on the PR
        SLACK: Sent over slack
    """

    CODEGEN = auto()
    GITHUB = auto()
    SLACK = auto()


@apidoc
class FlagKwargs(TypedDict, total=False):
    message: ReadOnly[str | None]
    message_type: ReadOnly[MessageType]
    message_recipient: ReadOnly[str | None]
