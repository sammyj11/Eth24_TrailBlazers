from __future__ import annotations

from typing import Literal, Union, Optional
from typing_extensions import NotRequired, TypedDict

# Anthropic Models
AnthropicModels = Literal[
    "claude-3-opus-20240229",
    "claude-3-sonnet-20240229",
    "claude-3-haiku-20240307",
    "claude-2.1",
    "claude-2.0"
]
"""
Available Anthropic models for text generation
"""

Role = Literal["assistant", "user"]
"""
Role is used to specify the role of the speaker in the conversation.
"""

FinishReason = Literal["end_turn", "max_tokens", "stop_sequence"]
"""
Reasons why a response might end in Anthropic's API
"""

# Anthropic's content block types
ContentType = Literal["text", "image"]
"""
Content types supported by Anthropic's API
"""

class ContentBlock(TypedDict):
    type: ContentType
    text: NotRequired[str]
    source: NotRequired[dict]

class Message(TypedDict):
    id: str
    role: Role
    content: list[ContentBlock]
    model: AnthropicModels
    stop_sequence: Optional[str]
    stop_reason: Optional[FinishReason]
    usage: NotRequired[Usage]

class StreamingMessage(TypedDict):
    type: Literal["message_start", "content_block_start", "content_block_delta", "content_block_stop", "message_delta", "message_stop"]
    message: NotRequired[Message]
    delta: NotRequired[ContentBlock]
    index: NotRequired[int]

# Tool/Function calling support
class FunctionCall(TypedDict):
    name: str
    arguments: str

class Tool(TypedDict):
    type: Literal["function"]
    function: dict

class Usage(TypedDict):
    input_tokens: int
    output_tokens: int

class Error(TypedDict):
    type: str
    message: str
    code: NotRequired[str]

# Messages API request types
class MessageRequest(TypedDict):
    model: AnthropicModels
    messages: list[Message]
    system: NotRequired[str]
    max_tokens: NotRequired[int]
    metadata: NotRequired[dict]
    stop_sequences: NotRequired[list[str]]
    stream: NotRequired[bool]
    temperature: NotRequired[float]
    top_p: NotRequired[float]
    top_k: NotRequired[int]
    tools: NotRequired[list[Tool]]
    
class MessageResponse(TypedDict):
    id: str
    type: Literal["message"]
    role: Literal["assistant"]
    content: list[ContentBlock]
    model: str
    stop_reason: Optional[FinishReason]
    stop_sequence: Optional[str]
    usage: Usage

# Anthropic specific error types
class APIError(TypedDict):
    type: Literal[
        "invalid_request_error",
        "authentication_error",
        "permission_error",
        "not_found_error",
        "rate_limit_error",
        "api_error"
    ]
    message: str
    code: NotRequired[str]