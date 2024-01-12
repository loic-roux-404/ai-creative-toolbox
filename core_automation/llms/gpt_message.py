from enum import Enum
from typing import Any, List

from pydantic import BaseModel

from .gpt_token_utils import token_count


class Role(str, Enum):
    ASSISTANT = "assistant"
    SYSTEM = "system"
    USER = "user"


class Message(BaseModel):
    content: str
    role: Role

    def tokens_count(self, model: str) -> int:
        return token_count(model, self.content) + len(str(self.role)) + 4

    class Config:
        use_enum_values = True


class MessageMapper:
    @staticmethod
    def deserialize(deserialized_message: dict[str, Any]) -> Message:
        return Message(**deserialized_message)

    @staticmethod
    def serialize_messages(messages: List[Message]):
        return [message.model_dump() for message in messages]
