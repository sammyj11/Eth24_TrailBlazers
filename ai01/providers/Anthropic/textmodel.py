import asyncio
import logging
import threading
from typing import Optional, List

logger = logging.getLogger(__name__)

class TextModelBuffer:
    """
    A thread-safe buffer for storing text output from the model.
    Designed to mimic the behavior of streaming text tokens or chunks.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._buffer: List[str] = []
        self._closed = False

    def enqueue_text(self, text: str):
        """
        Add text to the buffer.
        """
        with self._lock:
            self._buffer.append(text)

    def recv(self) -> Optional[str]:
        """
        Retrieve and remove the next available text from the buffer.
        If the buffer is empty and not closed, return None.
        If closed and empty, return None.
        """
        with self._lock:
            if self._buffer:
                return self._buffer.pop(0)
            return None

    def flush(self):
        """
        Clear the buffer.
        """
        with self._lock:
            self._buffer.clear()

    def close(self):
        """
        Mark the buffer as closed. No more text will be enqueued.
        """
        with self._lock:
            self._closed = True


class TextModel:
    """
    A simple class to handle streaming text responses.
    This can be integrated with the Anthropic API streaming responses.
    """

    def __init__(self):
        self.buffer = TextModelBuffer()
        self._active = True

    def __repr__(self) -> str:
        return f"<TextModel active={self._active}>"

    @property
    def active(self):
        return self._active

    def enqueue_text(self, text: str):
        """
        Enqueue new text tokens or chunks received from the model.
        This is typically called when receiving partial responses from Anthropic.
        """
        if not self._active:
            logger.warning("Attempted to enqueue text on an inactive TextModel.")
            return
        self.buffer.enqueue_text(text)

    def flush_text(self):
        """
        Flush all queued text.
        """
        self.buffer.flush()

    async def recv(self) -> Optional[str]:
        """
        Asynchronously retrieve the next available piece of text from the buffer.
        If no text is immediately available, this will wait briefly before returning.
        If the model becomes inactive or the buffer remains empty, eventually returns None.
        """
        while self._active:
            chunk = self.buffer.recv()
            if chunk is not None:
                return chunk
            # If none available, wait a bit and retry
            await asyncio.sleep(0.05)
        return None

    def stop(self):
        """
        Mark the model as inactive and close the buffer.
        """
        self._active = False
        self.buffer.close()
