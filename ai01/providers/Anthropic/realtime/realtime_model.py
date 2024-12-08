import asyncio
import logging
import uuid
from typing import Optional

from pydantic import BaseModel

from ai01.agent import Agent, AgentsEvents
from ai01.utils.socket import SocketClient  # If not needed, you can remove this import
from ....utils.emitter import EnhancedEventEmitter

from . import _api
from .conversation import Conversation

import anthropic

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RealTimeModelOptions(BaseModel):
    """
    RealTimeModelOptions is the configuration for the Anthropic-based RealTimeModel.
    """

    anthropic_api_key: str
    """
    Anthropic API Key.
    """

    model: _api.AnthropicModels = "claude-2.0"
    """
    The Anthropic model to be used.
    """

    instructions: str = ""
    """
    Instructions (system prompt) given to the model.
    """

    temperature: float = 0.8
    """
    Temperature for sampling.
    """

    max_tokens: int = 128
    """
    Maximum number of tokens to generate in the response.
    """

    loop: Optional[asyncio.AbstractEventLoop] = None
    """
    Loop is the Event Loop to be used for the RealTimeModel, defaults to the current Event Loop.
    """

    stop_sequences: list[str] = []
    """
    Stop sequences for the Anthropic completion.
    """

    top_p: float = 1.0
    """
    Nucleus sampling parameter.
    """

    top_k: int = 1
    """
    Top-k sampling parameter.
    """

    class Config:
        arbitrary_types_allowed = True


class RealTimeModel(EnhancedEventEmitter):
    def __init__(self, agent: Agent, options: RealTimeModelOptions):
        # Agent is the instance which is interacting with the RealTimeModel.
        self.agent = agent
        self._opts = options

        self._logger = logger.getChild(f"AnthropicRealTimeModel-{self._opts.model}")

        self._conversation: Conversation = Conversation(id=str(uuid.uuid4()))
        self.loop = options.loop or asyncio.get_event_loop()

        self._anthropic_client = anthropic.Client(api_key=self._opts.anthropic_api_key)

        # Task that handles streaming completions
        self._stream_task: Optional[asyncio.Task] = None

    def __str__(self):
        return f"AnthropicRealTimeModel: {self._opts.model}"

    def __repr__(self):
        return f"AnthropicRealTimeModel: {self._opts.model}"

    @property
    def conversation(self):
        return self._conversation

    async def connect(self):
        """
        For Anthropic, there's no persistent WebSocket connection to open.
        This method can prepare any needed state.
        """
        self._logger.info("Anthropic model ready for streaming.")
        # In Anthropic integration, connect might just be a no-op.
        # We can still start a background task if needed.
        self._stream_task = asyncio.create_task(self._main(), name="AnthropicModelMain")

    def _build_prompt(self):
        """
        Build the prompt for Anthropic from instructions and conversation.
        Anthropic’s models often use the "Anthropic completion format".

        We'll follow the recommended prompt format:
        \n\nHuman: <user_message>\n\nAssistant: <assistant_message>
        with a system prompt at the start.
        """
        # The conversation might store messages with roles.
        # We'll produce something like:
        # [System: {instructions}]
        # Human: ...
        # Assistant: ...
        # etc.
        # Typically, Anthropic suggests a format like:
        # "\n\nHuman: {user_message}\n\nAssistant: "
        # The system can be integrated as an initial human message or just a prefix.

        prompt_parts = []
        # System prompt as a special prefix or as a "Human" role specifying instructions.
        if self._opts.instructions.strip():
            prompt_parts.append(f"{anthropic.HUMAN_PROMPT} {self._opts.instructions.strip()}{anthropic.AI_PROMPT}")

        for msg in self.conversation.messages:
            if msg.role == "user":
                # Human message
                user_text = " ".join([block.get("text", "") for block in msg.content if block.get("type") == "text"])
                prompt_parts.append(f"{anthropic.HUMAN_PROMPT} {user_text}")
            else:
                # Assistant message
                assistant_text = " ".join([block.get("text", "") for block in msg.content if block.get("type") == "text"])
                prompt_parts.append(f"{anthropic.AI_PROMPT} {assistant_text}")

        # End with AI prompt to get the assistant's completion
        full_prompt = "".join(prompt_parts) + anthropic.AI_PROMPT
        return full_prompt

    async def _main(self):
        """
        Continuously wait for a new user message or trigger and then request a new completion.
        """
        self._logger.info("Starting main loop for Anthropic streaming responses.")

        while True:
            # Wait for something (e.g., a new user message or a trigger).
            # Depending on your architecture, you may have a condition here or
            # just handle "on demand" requests.

            # For demonstration, we assume we react to some event externally or
            # the agent triggers a completion request.

            # Sleep to avoid busy loop.
            await asyncio.sleep(0.1)

            # Check if there's a "completion needed" flag or if we do on every user message.
            # This logic depends on how your Agent and Conversation classes work.
            # Suppose we have a way to know when the user has finished speaking or provided input:
            if self.conversation.has_new_user_message:
                # Construct prompt and send to Anthropics
                prompt = self._build_prompt()
                await self._stream_completion(prompt)
                self.conversation.mark_user_message_consumed()

    async def _stream_completion(self, prompt: str):
        self._logger.info("Sending request to Anthropic completions API.")

        # Use the anthropic client to stream the response.
        # The anthropic-python client returns a generator when stream=True.
        # We'll iterate over it and handle tokens as they come in.

        try:
            response = self._anthropic_client.completions.create(
                prompt=prompt,
                model=self._opts.model,
                max_tokens_to_sample=self._opts.max_tokens,
                stop_sequences=self._opts.stop_sequences,
                temperature=self._opts.temperature,
                top_p=self._opts.top_p,
                top_k=self._opts.top_k,
                stream=True
            )

            # response is a generator yielding tokens as they come in.
            # We'll accumulate them into a message.
            content_blocks = []
            text_buffer = ""

            async for token_data in response:
                token = token_data.get("completion", "")
                if token:
                    self.agent.emit(AgentsEvents.Speaking)
                    text_buffer += token
                    # We can emit partial text to the agent if desired.
                    # Once done, finalize.

            if text_buffer.strip():
                # Add the final assistant message to the conversation
                message_id = str(uuid.uuid4())
                content_block = {"type": "text", "text": text_buffer}
                new_msg: _api.Message = {
                    "id": message_id,
                    "role": "assistant",
                    "content": [content_block],
                    "model": self._opts.model,
                    "stop_sequence": None,
                    "stop_reason": None
                }
                self.conversation.add_message(new_msg)
                self.agent.emit(AgentsEvents.Response, text_buffer.strip())

            self._logger.info("Anthropic completion streaming done.")

        except Exception as e:
            self._logger.error(f"Error streaming from Anthropic: {e}")

    async def send_user_message(self, user_text: str):
        """
        Called externally when a user message arrives.
        We add it to the conversation and the main loop will eventually trigger a completion.
        """
        message_id = str(uuid.uuid4())
        content_block = {"type": "text", "text": user_text}
        new_msg: _api.Message = {
            "id": message_id,
            "role": "user",
            "content": [content_block],
            "model": self._opts.model,
            "stop_sequence": None,
            "stop_reason": None
        }
        self.conversation.add_message(new_msg)
        # The main loop will detect a new user message and process it.
