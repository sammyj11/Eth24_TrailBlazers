from pydantic import BaseModel, Field
from rtc import RTC, RTCOptions
from ._exceptions import RoomNotConnectedError, RoomNotCreatedError


class AgentOptions(BaseModel):
    rtc_options: RTCOptions = Field(
        description="RTC Options for the Agent",
    )


class Agent:
    """
    Agents is defined as the higher level user which is its own entity and has exposed APIs to
    interact with different Models and Outer World using dRTC.

    Agents can be connected to the dRTC Network by two stepsL
     - Joining the Agent to the dRTC Network, which assigns the Agent to a Room, using this Agent can setup event Listeners before connecting to the Room.
     - Connecting the Agent to the Room, which allows the Agent to send and receive data from the Room, and become part of the Room.
    """

    def __init__(self, options: AgentOptions):
        # Options is the configuration for the Agent.
        self.options = options

        # RTC is the Real Time Communication Handler for the Agent.
        self.__rtc = RTC(options.rtc_options)

    @property
    def rtc(self):
        return self.__rtc

    @property
    def room(self):
        """
        Room is the Room the Agent is connected to, This is only available after the Agent is connected.

        raise ValueError if Agent is not connected to the Room.
        """
        if not self.__rtc.room:
            raise RoomNotCreatedError()

        return self.__rtc.room

    async def join(self):
        """
        Joins the Agent to the dRTC Network, Upon Joining the Agent is assigned to a Room.
        Using the Room the Agent can Listen to Events such as RemotePeer Joining, Leaving and Produce Events Triggered in the Room
        """
        room = await self.__rtc.create()

        if not room:
            raise RoomNotConnectedError()

        return room

    async def connect(self):
        """
        Connects the Agent to the Room, This is only available after the Agent is joined to the dRTC Network.
        """
        room = self.__rtc.room

        if not room:
            raise RoomNotCreatedError()

        await room.connect()
