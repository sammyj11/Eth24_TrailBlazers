import asyncio
import logging
import os

from dotenv import load_dotenv

from ai01.agent import Agent, AgentOptions, AgentsEvents
# from ai01.providers.openai import AudioTrack
from ai01.providers.Anthropic.textmodel import TextModel

from ai01.providers.Anthropic.realtime.realtime_model import RealTimeModel, RealTimeModelOptions
from ai01.rtc import (
    HuddleClientOptions,
    ProduceOptions,
    Role,
    RoomEvents,
    RoomEventsData,
    RTCOptions,
)

from prompt import bot_prompt

load_dotenv()

import requests
import json

def create_huddle_room():
    url = "https://api.huddle01.com/api/v1/create-room"
    
    headers = {
        "x-api-key": "ak_gUgjnRb9yCbHgQZs",  # Your Huddle01 API key
        "Content-Type": "application/json"
    }
    
    # Optional body parameters
    # payload = {
    #     "title": "AI Agent Room",
    #     "description": "Room for AI agent interaction",
    #     "roomLock": False
    # }
    
    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()  # Raises an HTTPError if the response status is 4XX/5XX
        
        room_data = response.json()
        room_id = room_data['data']['roomId']
        print(f"Room created successfully! Room ID: {room_id}")
        return room_id
        
    except requests.exceptions.RequestException as e:
        print(f"Error creating room: {e}")
        return None

# Use it in your main function
room_id = create_huddle_room()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Chatbot")


async def main():
    try:
        # Huddle01 API Key
        huddle_api_key = os.getenv("HUDDLE_API_KEY")
        huddle_api_key="ak_gUgjnRb9yCbHgQZs"

        # Huddle01 Project ID
        huddle_project_id = os.getenv("HUDDLE_PROJECT_ID")
        huddle_project_id="pi_WYxyQg6Cq6nEkdPs"

        # OpenAI API Key
        openai_api_key = os.getenv("OPENAI_API_KEY")
        openai_api_key="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"
        anthropic_api_key="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"

        if not huddle_api_key or not huddle_project_id or not anthropic_api_key:
            raise ValueError("Required Environment Variables are not set")

        # RTCOptions is the configuration for the RTC
        rtcOptions = RTCOptions(
            api_key=huddle_api_key,
            project_id=huddle_project_id,
            room_id=room_id,
            role=Role.HOST,
            metadata={"displayName": "Agent"},
            huddle_client_options=HuddleClientOptions(
                autoConsume=True, volatileMessaging=False
            ),
        )

        _lock = asyncio.Lock()

        # Agent is the Peer which is going to connect to the Room 
        # breakpoint()

        agent = Agent(
            options=AgentOptions(rtc_options=rtcOptions, text_track=TextModel(), _lock=_lock),
        )

        # breakpoint()

        # RealTimeModel is the Model which is going to be used by the Agent
        llm = RealTimeModel(
            agent=agent,
            options = RealTimeModelOptions(
    anthropic_api_key=anthropic_api_key,
    model='claude-2.0',
    instructions=bot_prompt,
    temperature=0.7,
    max_tokens=1500,
    stop_sequences=["\nHuman:", "\nAssistant:"],
    top_p=0.9,
    top_k=50
),
        )

        # Join the dRTC Network, which creates a Room instance for the Agent to Join.
        room = await agent.join()

        breakpoint()

        # Room Events
        # @room.on(RoomEvents.RoomJoined)
        # def on_room_joined():
        #     logger.info("Room Joined")

        # @room.on(RoomEvents.NewPeerJoined)
        # def on_new_remote_peer(data: RoomEventsData.NewPeerJoined):
        #     logger.info(f"New Remote Peer: {data['remote_peer']}")

        # @room.on(RoomEvents.RemotePeerLeft)
        # def on_peer_left(data: RoomEventsData.RemotePeerLeft):
        #     logger.info(f"Peer Left: {data['remote_peer_id']}")

        # @room.on(RoomEvents.RoomClosed)
        # def on_room_closed(data: RoomEventsData.RoomClosed):
        #     logger.info("Room Closed")

        # @room.on(RoomEvents.RemoteProducerAdded)
        # def on_remote_producer_added(data: RoomEventsData.RemoteProducerAdded):
        #     logger.info(f"Remote Producer Added: {data['producer_id']}")

        # @room.on(RoomEvents.RemoteProducerClosed)
        # def on_remote_producer_closed(data: RoomEventsData.RemoteProducerClosed):
        #     logger.info(f"Remote Producer Closed: {data['producer_id']}")

        

        @room.on(RoomEvents.NewConsumerAdded)
        def on_remote_consumer_added(data: RoomEventsData.NewConsumerAdded):
            logger.info(f"Remote Consumer Added: {data}")

            if data['kind'] == 'audio':
                track = data['consumer'].track

                if track is None:
                    logger.error("Consumer Track is None, This should never happen.")
                    return

                llm.conversation.add_track(data['consumer_id'], track)
            
        # @room.on(RoomEvents.ConsumerClosed)
        # def on_remote_consumer_closed(data: RoomEventsData.ConsumerClosed):
        #     logger.info(f"Remote Consumer Closed: {data['consumer_id']}")

        # @room.on(RoomEvents.ConsumerPaused)
        # def on_remote_consumer_paused(data: RoomEventsData.ConsumerPaused):
        #     logger.info(f"Remote Consumer Paused: {data['consumer_id']}")

        # @room.on(RoomEvents.ConsumerResumed)
        # def on_remote_consumer_resumed(data: RoomEventsData.ConsumerResumed):
        #     logger.info(f"Remote Consumer Resumed: {data['consumer_id']}")


        # # Agent Events
        # breakpoint()
        # @agent.on(AgentsEvents.Connected)
        # def on_agent_connected():
        #     logger.info("Agent Connected")

        # @agent.on(AgentsEvents.Disconnected)
        # def on_agent_disconnected():
        #     logger.info("Agent Disconnected")

        # @agent.on(AgentsEvents.Speaking)
        # def on_agent_speaking():
        #     logger.info("Agent Speaking")

        # @agent.on(AgentsEvents.Listening)
        # def on_agent_listening():
        #     logger.info("Agent Listening")

        # @agent.on(AgentsEvents.Thinking)
        # def on_agent_thinking():
        #     logger.info("Agent Thinking")


        # Connect to the LLM to the Room
        await llm.connect()

        # Connect the Agent to the Room
        await agent.connect()

        # breakpoint()

        # if agent.text_track is not None:
        #     await agent.rtc.produce(
        #         options=ProduceOptions(
        #             label="audio",
        #             track=agent.text_track,
        #         )
        #     )

        # @agent.on(RoomEvents.NewDataMessage)
        # def on_new_data_message(data: AgentEvent.NewDataMessage):
        #     print(f"New Data Message: {data['peer_id']} - {data['message']}")

        # Force the program to run indefinitely
        try:
            await asyncio.Future()
        except KeyboardInterrupt:
            logger.info("Exiting...")

    except KeyboardInterrupt:
        print("Exiting...")

    except Exception as e:
        print(e)


if __name__ == "__main__":
    asyncio.run(main())
