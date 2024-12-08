import logging
from typing import List
from . import _api

logger = logging.getLogger(__name__)

class Conversation:
    def __init__(self, id: str):
        self.id = id
        """
        Conversation ID.
        """
        self._logger = logger.getChild("Conversation")
        """
        Logger for the Conversation.
        """
        self._messages: List[_api.Message] = []
        self._last_user_message_index = -1
        """
        Keeps track of the last processed user message index, so we can know if a new user message is available.
        """

        self._active = True
        """
        Indicates if the Conversation is still active.
        """

    def __str__(self):
        return f"Conversation ID: {self.id}"
    
    def __repr__(self):
        return f"Conversation ID: {self.id}"
    
    @property
    def logger(self):
        return self._logger
    
    @property
    def active(self):
        return self._active

    @property
    def messages(self) -> List[_api.Message]:
        return self._messages

    @property
    def has_new_user_message(self) -> bool:
        """
        Check if there is a new user message since the last time we processed one.
        """
        # Find the index of the last user message.
        last_user_idx = -1
        for i, msg in enumerate(self._messages):
            if msg["role"] == "user":
                last_user_idx = i
        return last_user_idx > self._last_user_message_index

    def mark_user_message_consumed(self):
        """
        Mark the latest user message as processed.
        """
        for i in reversed(range(len(self._messages))):
            if self._messages[i]["role"] == "user":
                self._last_user_message_index = i
                break

    def add_message(self, msg: _api.Message):
        """
        Add a message to the conversation. 
        Message should conform to the _api.Message type (i.e., have an id, role, content, etc.)
        """
        self._messages.append(msg)
        self.logger.info(f"Message added to conversation {self.id}: {msg['role']} - {msg['content']}")

    def stop(self):
        """
        Stop the Conversation.
        """
        self._active = False
