from pydantic import BaseModel


class AgentOptions(BaseModel):
    pass


class Agent(AgentOptions):
    """
    Agents is defined as the higher level user which is its own entity and has exposed APIs to
    interact with different Models and Outer World using dRTC.
    """

    def __init__(self, options: AgentOptions):
        self.options = options
