import asyncio
import logging
import os

from dotenv import load_dotenv

from ai01.agent import Agent, AgentEvent, AgentEventType, AgentOptions
from ai01.providers.openai import AudioTrack
from ai01.providers.openai.realtime import (
    RealTimeModel,
    RealTimeModelOptions,
    ServerEvent,
)
from ai01.rtc import HuddleClientOptions, Role, RoomEvents, RoomEventsType, RTCOptions

load_dotenv()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Chatbot")


async def main():
    try:
        # Huddle01 API Key
        huddle_api_key = os.getenv("HUDDLE_API_KEY")

        # Huddle01 Project ID
        huddle_project_id = os.getenv("HUDDLE_PROJECT_ID")

        # OpenAI API Key
        openai_api_key = os.getenv("OPENAI_API_KEY")

        if not huddle_api_key or not huddle_project_id or not openai_api_key:
            raise ValueError("Required Environment Variables are not set")

        # RTCOptions is the configuration for the RTC
        rtcOptions = RTCOptions(
            api_key=huddle_api_key,
            project_id=huddle_project_id,
            room_id="DAAO",
            role=Role.HOST,
            metadata={"displayName": "Agent"},
            huddle_client_options=HuddleClientOptions(
                autoConsume=True, volatileMessaging=False
            ),
        )

        # Agent is the Peer which is going to connect to the Room 
        agent = Agent(
            options=AgentOptions(rtc_options=rtcOptions, audio_track=AudioTrack()),
        )

        # RealTimeModel is the Model which is going to be used by the Agent
        llm = RealTimeModel(
            agent=agent,
            options=RealTimeModelOptions(
                oai_api_key=openai_api_key,
            ),
        )

        # Join the dRTC Network, which creates a Room instance for the Agent to Join.
        room = await agent.join()

        # Room Events
        @room.on(RoomEventsType.RoomJoined)
        def on_room_joined(data: RoomEvents.RoomJoined):
            print("Room Joined")

        @room.on(RoomEventsType.NewPeerJoined)
        def on_new_remote_peer(data: RoomEvents.NewPeerJoined):
            logger.info(f"New Remote Peer: {data['remote_peer']}")

        @room.on(RoomEventsType.RemotePeerLeft)
        def on_peer_left(data):
            logger.info(f"Peer Left: {data['peer_id']}")

        @room.on(RoomEventsType.RoomClosed)
        def on_room_closed():
            logger.info("Room Closed")

        @room.on(RoomEventsType.RemoteProducerAdded)
        def on_remote_producer_added(data: RoomEvents.RemoteProducerAdded):
            logger.info(f"Remote Producer Added: {data['producer_id']}")

        @room.on(RoomEventsType.RemoteProducerClosed)
        def on_remote_producer_closed(data: RoomEvents.RemoteProducerClosed):
            logger.info(f"Remote Producer Closed: {data['producer_id']}")

        @room.on(RoomEventsType.RemoteConsumerAdded)
        def on_remote_consumer_added(data: RoomEvents.RemoteConsumerAdded):
            logger.info(f"Remote Consumer Added: {data['consumer_id']}")

        @room.on(RoomEventsType.RemoteConsumerClosed)
        def on_remote_consumer_closed(data: RoomEvents.RemoteConsumerClosed):
            logger.info(f"Remote Consumer Closed: {data['consumer_id']}")

        @room.on(RoomEventsType.RemoteConsumerPaused)
        def on_remote_consumer_paused(data: RoomEvents.RemoteConsumerPaused):
            logger.info(f"Remote Consumer Paused: {data['consumer_id']}")

        @room.on(RoomEventsType.RemoteConsumerResumed)
        def on_remote_consumer_resumed(data: RoomEvents.RemoteConsumerResumed):
            logger.info(f"Remote Consumer Resumed: {data['consumer_id']}")


        # Agent Events
        @agent.on(AgentEventType.AgentConnected)
        def on_agent_connected(data: AgentEvent.Connected):
            logger.info(f"Agent Connected: {data['peer_id']}")

        @agent.on(AgentEventType.AgentDisconnected)
        def on_agent_disconnected(data: AgentEvent.Disconnected):
            logger.info(f"Agent Disconnected: {data['peer_id']}")

        @agent.on(AgentEventType.AgentSpeaking)
        def on_agent_speaking(data: AgentEvent.Speaking):
            logger.info(f"Agent Speaking: {data['peer_id']}")

        @agent.on(AgentEventType.AgentListening)
        def on_agent_listening(data: AgentEvent.Listening):
            logger.info(f"Agent Listening: {data['peer_id']}")

        @agent.on(AgentEventType.AgentThinking)
        def on_agent_thinking(data: AgentEvent.Thinking):
            logger.info(f"Agent Thinking: {data['peer_id']}")

        # LLM Events
        @llm.on("test")
        def on_test(data: ServerEvent.ConversationItemCreated):
            pass


        # Connect to the LLM to the Room
        await llm.connect()

        # Connect the Agent to the Room
        await agent.connect()

        # @agent.on(RoomEvents.NewDataMessage)
        # def on_new_data_message(data: AgentEvent.NewDataMessage):
        #     print(f"New Data Message: {data['peer_id']} - {data['message']}")

        # Force the program to run indefinitely
        await asyncio.Future()
    except KeyboardInterrupt:
        print("Exiting...")

    except Exception as e:
        print(e)


if __name__ == "__main__":
    asyncio.run(main())
