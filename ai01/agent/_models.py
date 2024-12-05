
from typing import TypedDict


# AgentEventType is the Enum for the different types of Events emitted by the Agent.
class AgentsEvents(str):
    AgentConnected: str = "agentConnected"
    AgentDisconnected: str = "agentDisconnected"
    AgentSpeaking: str = "agentSpeaking"
    AgentListening: str = "agentListening"
    AgentThinking: str = "agentThinking"


# AgentEvent is the Event which is emitted by the Agent.
class AgentEventsData:
    class Connected(TypedDict):
        peer_id: str

    class Disconnected(TypedDict):
        peer_id: str

    class Speaking(TypedDict):
        peer_id: str

    class Listening(TypedDict):
        peer_id: str

    class Thinking(TypedDict):
        peer_id: str







