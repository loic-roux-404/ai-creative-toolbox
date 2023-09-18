from enum import Enum
from typing import Any, List

from pydantic import BaseModel


class Role(str, Enum):
    ASSISTANT = "assistant"
    SYSTEM = "system"
    USER = "user"


class Message(BaseModel):
    role: Role
    content: str


class MessageMapper:
    @staticmethod
    def deserialize(deserialized_message: dict[str, Any]) -> Message:
        return Message(**deserialized_message)

    @staticmethod
    def serialize_messages(messages: List[Message]):
        return [message.model_dump() for message in messages]
