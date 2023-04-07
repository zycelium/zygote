"""
Weather updates from OpenWeatherMap.
"""
from sunnyside import Sunnyside
from zycelium.zygote.agent import Agent

agent = Agent(name="weather", debug=True)

agent.config = {
    "api_key": "",
    "city": "",
    "units": "metric",
}


@agent.on_startup(delay=1)
@agent.on_interval(minutes=10)
async def weather():
    """Update weather periodically."""
    sunnyside = Sunnyside(api_key=agent.config["api_key"], units=agent.config["units"])
    weather_api = sunnyside.current_weather()
    weather_data = weather_api.get_current_weather_by_city_name(
        city_name=agent.config["city"]
    )
    await agent.emit("weather/current", weather_data)
