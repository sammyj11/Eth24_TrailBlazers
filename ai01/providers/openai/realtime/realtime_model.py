import asyncio

import _api
from pydantic import BaseModel

from ai01.agent import Agent


class RealTimeModelOptions(BaseModel):
    """
    RealTimeModelOptions is the configuration for the RealTimeModel.
    """

    oai_api_key: str
    """
    OpenAI API Key is the API Key for the OpenAI API.
    """

    model: _api.RealTimeModels = "gpt-4o-realtime-preview"
    """
    Model is the RealTimeModel to be used, defaults to gpt-4o-realtime-preview.
    """

    instructions: str = ""
    """
    Instructions is the Initial Prompt given to the Model.
    """

    modalities: list[_api.Modality] = ["text", "audio"]
    """
    Modalities is the list of things to be used by the Model.
    """

    voice: _api.Voice = "alloy"
    """
    Voice is the of audio voices which will be generated and returned by the Model.
    """

    temperature: float = 0.8
    """
    Temperature is the randomness of the Model, to select the next token.
    """

    input_audio_format: _api.AudioFormat = "pcm16"
    """
    Input Audio Format is the format of the input audio, which is given to the Model.
    """

    output_audio_format: _api.AudioFormat = "pcm16"
    """
    Output Audio Format is the format of the audio, which is returned by the Model.
    """

    base_url: str = "wss://api.openai.com/v1/realtime"
    """
    Base URL is the URL of the RealTime API, defaults to the OpenAI RealTime API.
    """

    tool_choice: _api.ToolChoice = "auto"
    """
    Tools are different other APIs which the Model can access, defaults to auto.
    """

    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    """
    Loop is the Event Loop to be used for the RealTimeModel, defaults to the current Event Loop.
    """


class RealTimeModel:
    def __init__(self, agent: Agent, options: RealTimeModelOptions):
        # Agent is the instance which is interacting with the RealTimeModel.
        self.agent = agent

        # API Key is the OpenAI API Key.
        self.apiKey = options.oai_api_key

        # Model is the RealTimeModel to be used.
        self.model = options.model

        # Instructions is the Initial Prompt given to the Model.
        self.instructions = options.instructions

        # Modalities is the list of things to be used by the Model.
        self.modalities = options.modalities

        # Voice is the of audio voices which will be generated and returned by the Model.
        self.voice = options.voice

        # Temperature is the randomness of the Model, to select the next token.
        self.temperature = options.temperature

        # Input Audio Format is the format of the input audio, which is given to the Model.
        self.inputAudioFormat = options.input_audio_format

        # Output Audio Format is the format of the audio, which is returned by the Model.
        self.outputAudioFormat = options.output_audio_format

        # Base URL is the URL of the RealTime API.
        self.baseURL = f"${options.base_url}?model={self.model}"

        # Tool Choice is the choice of the tools to be used by the Model.
        self.toolChoice = options.tool_choice

        # Loop is the Event Loop to be used for the RealTimeModel.
        self.loop = options.loop
