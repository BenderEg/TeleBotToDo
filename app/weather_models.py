from abc import ABC
from datetime import datetime
from enum import Enum, auto
from json import loads
from typing import Optional

from aiogram.utils.keyboard import InlineKeyboardBuilder
from pydantic import BaseModel, ConfigDict
from requests import request, Response

from settings import settings


class Modes(Enum):

    CURRENT_SHORT = 0
    CURRENT_LONG = 1
    FORECAST = 2


class AbstractWeather(ABC, BaseModel):

    pass


class RequestError(Exception):

    pass


class Weather(BaseModel):

    model_config = ConfigDict(extra='ignore')

    main: str
    description: str
    icon: Optional[str]


class MainData(BaseModel):

    model_config = ConfigDict(extra='ignore')

    temp: float
    feels_like: float
    humidity: int
    pressure: int


class Wind(BaseModel):

    model_config = ConfigDict(extra='ignore')

    speed: float


class Location(BaseModel):

    model_config = ConfigDict(extra='ignore')

    country: str
    sunrise: int
    sunset: int


class CurrentData(AbstractWeather):

    model_config = ConfigDict(extra='ignore')

    weather: list[Weather]
    main: MainData
    wind: Wind
    rain: Optional[dict] = None
    snow: Optional[dict] = None
    sys: Location
    timezone: int
    name: str


async def get_current_weather(latitude: float, longitude: float) -> Response:
    response: Response = request('GET', f'''https://api.openweathermap.org/data/2.5/weather?\
lat={latitude}&lon={longitude}&appid={settings.wapi_key}&lang\
={settings.language}&units={settings.units}''')
    if not response:
        raise RequestError('Ошибка подключения к сервесу погоды.\
Попробуйте позже.')
    return response


async def get_forecast(latitude: float, longitude: float) -> Response:
    response: Response = request('GET', f'''https://api.openweathermap.org/data/2.5/forecast/daily?\
lat={latitude}&lon={longitude}&appid={settings.wapi_key}&lang\
={settings.language}&units={settings.units}&cnt={settings.days_forecast}''')
    if not response:
        raise RequestError('Ошибка подключения к сервесу погоды.\
Попробуйте позже.')
    return response


async def convert_response_to_model(
          response: Response,
          class_name: AbstractWeather) -> AbstractWeather:

    weather_dict = response.json()
    return class_name(**weather_dict)


async def prepare_current_output(obj: CurrentData) -> str:

    description = ', '.join([ele.description for ele in obj.weather])
    res = f'''
Описание: {description};
Температура: {obj.main.temp} {chr(176)}С;
Ощущается как: {obj.main.feels_like} {chr(176)}С;
Влажность: {obj.main.humidity} %;
Давление: {obj.main.pressure} мм;
Ветер: {obj.wind.speed} м/с;
Местоположение: {obj.name} ({obj.sys.country}).'''
    return res


async def send_current_weather(latitude: float,
                               longitude: float,
                               class_name: CurrentData) -> str:
    response = await get_current_weather(latitude, longitude)
    data: CurrentData = await convert_response_to_model(
        response, class_name)
    res = await prepare_current_output(data)
    return res


async def create_modes_builder() -> InlineKeyboardBuilder:

    modes = {Modes.CURRENT_SHORT: 'Погода на текущий момент (краткий формат)',
             Modes.CURRENT_LONG: 'Погода на текущий момент (подробный формат)',
             Modes.FORECAST: f'''Погода на заданную дату (максимум {
                 settings.days_forecast} дней)'''}
    builder = InlineKeyboardBuilder()
    for key, value in modes.items():
        builder.button(text=f'{value}',
                       callback_data=f"{key.value}")
    builder.adjust(1, 1)
    return builder
