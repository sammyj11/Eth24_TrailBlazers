import asyncio
import os

from dotenv import load_dotenv

from ai01.agent import Agent, AgentOptions
from ai01.providers.openai import AudioTrack
from ai01.providers.openai.realtime import RealTimeModel, RealTimeModelOptions
from ai01.rtc import HuddleClientOptions, Role, RoomEvents, RTCOptions

load_dotenv()


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

        agent_options = AgentOptions(rtc_options=rtcOptions, audio_track=AudioTrack())

        agent = Agent(
            agent_options,
        )

        room = await agent.join()

        model_options = RealTimeModelOptions(oai_api_key=openai_api_key)

        llm = RealTimeModel(agent=agent, options=model_options)

        @room.on(RoomEvents.RoomJoined)
        def on_room_joined():
            print("Room Joined")

        await agent.connect()

        # Force the program to run indefinitely
        await asyncio.Future()
    except KeyboardInterrupt:
        print("Exiting...")

    except Exception as e:
        print(e)


if __name__ == "__main__":
    asyncio.run(main())
