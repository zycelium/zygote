"""
Log to file agent.
"""
import json
from zycelium.zygote.agent import Agent

agent = Agent(name="log_to_file", debug=True)

agent.config = {
    "log_file": "zygote_events.log",
}


@agent.on("*")
async def log_to_file(_kind, frame):
    """Log events to file."""
    with open(agent.config["log_file"], "a", encoding="utf-8") as file:
        file.write(json.dumps(frame) + "\n")
