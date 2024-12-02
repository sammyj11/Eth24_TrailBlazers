import asyncio
import os

from dotenv import load_dotenv

from ai01.agent import Agent, AgentOptions
from ai01.rtc import HuddleClientOptions, Role, RoomEvents, RTCOptions

load_dotenv()


async def main():
    # Huddle01 API Key
    huddle_api_key = os.getenv("HUDDLE_API_KEY")

    # Huddle01 Project ID
    huddle_project_id = os.getenv("HUDDLE_PROJECT_ID")

    if not huddle_api_key or not huddle_project_id:
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

    agent_options = AgentOptions(rtc_options=rtcOptions)

    agent = Agent(
        agent_options,
    )

    room = await agent.join()

    @room.on(RoomEvents.RoomJoined)
    def on_room_joined():
        print("Room Joined")

    await agent.connect()


if __name__ == "__main__":
    asyncio.run(main())
