import json
import logging
from pydantic import BaseModel, Field
from huddle01 import (
    HuddleClient,
    HuddleClientOptions,
    Role,
    AccessTokenOptions,
    AccessToken,
    AccessTokenData,
)

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("RTC")


class RTCOptions(BaseModel):
    """
    RTCOptions is the configuration for the Room.
    """

    project_id: str = Field(
        description="Huddle Project Id",
    )

    api_key: str = Field(
        description="Huddle API Key",
    )

    room_id: str = Field(
        description="Huddle Room Id to Join",
    )

    huddle_client_options: HuddleClientOptions = Field(
        description="Huddle Client Options",
    )

    metadata: dict[str, str] = Field(
        description="Metadata to be sent to the Room",
    )

    role: str = Field(
        description="Role of the User",
    )


class RTC:
    """
    RTC Handles anything related to Real Time Communication, using the dRTC Network,
    Currently it is using Huddle01 as the dRTC Network.
    """

    def __init__(self, options: RTCOptions):
        self._logger = logger.getChild(options.room_id)

        self._options = options

    def __str__(self):
        return f"RTC Room: {self._options.room_id}"

    def __repr__(self):
        return f"RTC Room: {self._options.room_id}"

    @property
    def options(self):
        return self._options

    async def join_room(self):
        """
        Join Room is used to join the Room with the given Room Id,

        Exceptions:
            - If there is any error while joining the Room, it will raise an Exception.
        """
        logger.info("Joining Huddle01 Room ", self._options.room_id)

        accessTokenData = AccessTokenData(
            room_id=self._options.room_id,
            api_key=self._options.api_key,
            options=AccessTokenOptions(
                metadata=json.dumps(self._options.metadata),
            ),
            role=Role(self._options.role),
        )

        accessToken = AccessToken(
            data=accessTokenData,
        )

        try:
            token = await accessToken.to_jwt()

            client = HuddleClient(
                project_id=self._options.project_id,
                options=self._options.huddle_client_options,
            )

            room = await client.create(self._options.room_id, token)

            logger.info("Successfully joined the Room: ", room)

            return room
        except Exception as e:
            logger.error("Error while joining the Room: ", e)
            raise e
