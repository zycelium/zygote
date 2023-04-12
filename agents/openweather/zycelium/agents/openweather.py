"""
Weather updates from OpenWeatherMap.
"""
from sunnyside import Sunnyside
from zycelium.zygote.agent import Agent, config
# pyright: reportOptionalMemberAccess=false


@config
class Config:
    """Config."""

    api_key: str = ""
    city: str = ""
    units: str = "metric"


agent = Agent("openweather")

agent.config = Config()


async def validate_config():
    """Validate config."""
    if not agent.config.api_key:
        await agent.emit(
            "openweather/error", {"message": "OpenWeather API key not provided."}
        )
        return False
    if not agent.config.city:
        await agent.emit("openweather/error", {"message": "City not provided."})
        return False
    if not agent.config.units:
        await agent.emit("openweather/error", {"message": "Units not provided."})
        return False
    if agent.config.units not in ["metric", "imperial"]:
        await agent.emit(
            "openweather/error", {"message": "Units must be metric or imperial."}
        )
        return False
    return True


@agent.on_startup(delay=1)
@agent.on_cron(minute="*/30")
async def weather():
    """Update weather periodically."""
    if not await validate_config():
        return
    sunnyside = Sunnyside(api_key=agent.config.api_key, units=agent.config.units)
    weather_api = sunnyside.current_weather()
    weather_data = weather_api.get_current_weather_by_city_name(
        city_name=agent.config.city
    )
    await agent.emit("openweather/current", weather_data)



if __name__ == "__main__":
    import asyncio

    asyncio.run(
        agent.run(
            "https://localhost:3965/",
            auth={"token": ""},
        )
    )
