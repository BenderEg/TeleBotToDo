from abc import ABC
from datetime import datetime, UTC, timedelta
from enum import Enum
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


class SearchError(Exception):

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


class City(BaseModel):

    name: str
    country: str
    timezone: int


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


class ForecastDataIndividual(BaseModel):

    model_config = ConfigDict(extra='ignore')

    dt: int
    main: MainData
    weather: list[Weather]
    rain: Optional[dict] = None
    snow: Optional[dict] = None


class ForecastData(BaseModel):

    model_config = ConfigDict(extra='ignore')

    list: list[ForecastDataIndividual]
    city: City

    def __str__(self):
        return self.city.name


class LocationByName(BaseModel):

    model_config = ConfigDict(extra='ignore')

    name: str
    lat: float
    lon: float
    country: str
    state: Optional[str] = None


async def get_current_weather(latitude: float, longitude: float) -> Response:
    response: Response = request('GET', f'''https://api.openweathermap.org/data/2.5/weather?\
lat={latitude}&lon={longitude}&appid={settings.wapi_key}&lang\
={settings.language}&units={settings.units}''')
    if not response:
        raise RequestError('Ошибка подключения к сервесу погоды.\
Попробуйте позже.')
    return response


async def get_locations_by_name(name: str) -> Response:
    response: Response = request('GET', f'''http://api.openweathermap.org/geo/1.0/direct?\
q={name}&limit={5}&appid={settings.wapi_key}''')
    if not response:
        raise RequestError('Ошибка подключения к сервесу погоды.\
Попробуйте позже.')
    return response


async def validate_locations(response: Response) -> list:

    locations_list = response.json()
    if not locations_list:
        raise SearchError('Локация не найдена, проверьте наименование.')
    return [LocationByName(**ele) for ele in locations_list]


async def get_forecast(latitude: float, longitude: float) -> Response:
    response: Response = request('GET', f'''https://api.openweathermap.org/data/2.5/forecast?\
lat={latitude}&lon={longitude}&appid={settings.wapi_key}&lang\
={settings.language}&units={settings.units}&cnt={settings.points}''')
    if not response:
        raise RequestError('Ошибка подключения к сервесу погоды.\
Попробуйте позже.')
    return response


async def validate_forecast(response: Response) -> ForecastData:

    forecast = response.json()
    if not forecast:
        raise SearchError('Данные отсутствуют.')
    return ForecastData(**forecast)


async def convert_response_to_model(
          response: Response,
          class_name: AbstractWeather) -> AbstractWeather:

    weather_dict = response.json()
    return class_name(**weather_dict)


async def _prepare_current_output(obj: CurrentData,
                                  mode: Modes) -> str:

    description = ', '.join([ele.description for ele in obj.weather])
    if mode == Modes.CURRENT_SHORT.value:
        res = f'''
Описание: {description};
Температура: {obj.main.temp} {chr(176)}С;
Ощущается как: {obj.main.feels_like} {chr(176)}С;\n'''
        if obj.rain:
            res += f'Количество осадков: {obj.rain.get("1h")} мм;\n'
        elif obj.snow:
            res += f'Количество осадков: {obj.snow.get("1h")} мм;\n'
        res += f'Местоположение: {obj.name} ({obj.sys.country}).'
        return res
    else:
        sunrise = datetime.fromtimestamp(obj.sys.sunrise, tz=UTC) + \
            timedelta(seconds=obj.timezone)
        sunset = datetime.fromtimestamp(obj.sys.sunset, tz=UTC) + \
            timedelta(seconds=obj.timezone)
        res = f'''
Описание: {description};
Температура: {obj.main.temp} {chr(176)}С;
Ощущается как: {obj.main.feels_like} {chr(176)}С;
Влажность: {obj.main.humidity} %;'''
        if obj.rain:
            res += f'Количество осадков: {obj.rain.get("1h")} мм;\n'
        elif obj.snow:
            res += f'Количество осадков: {obj.snow.get("1h")} мм;\n'
        res += f'''
Давление: {obj.main.pressure} мм;
Ветер: {obj.wind.speed} м/с;
Восход: {_time_from_datetime(sunrise)};
Закат: {_time_from_datetime(sunset)};
Местоположение: {obj.name} ({obj.sys.country}).'''
        return res


async def send_current_weather(latitude: float,
                               longitude: float,
                               class_name: CurrentData,
                               mode: int) -> str:
    response = await get_current_weather(latitude, longitude)
    data: CurrentData = await convert_response_to_model(
        response, class_name)
    res = await _prepare_current_output(data, mode)
    return res


def _time_from_datetime(obj: datetime) -> str:

    hour = '{:0>2}'.format(obj.hour)
    minute = '{:0>2}'.format(obj.minute)
    return f'{hour}:{minute}'


def _filter_day_data(time: datetime) -> bool:

    hour = time.hour
    if 8 < hour < 22:
        return True
    else:
        return False


async def prepare_forecast_output(obj: ForecastData) -> str:

    res = f'Местоположение: {obj.city.name} ({obj.city.country}).\n\n'
    data = list(filter(lambda x: _filter_day_data(
        datetime.fromtimestamp(x.dt, tz=UTC) +
        timedelta(seconds=obj.city.timezone)), obj.list))
    starting_time = datetime.fromtimestamp(data[0].dt, tz=UTC) +\
        timedelta(seconds=obj.city.timezone)
    ref_day = starting_time.day
    res += f'<b>Дата: {starting_time.strftime("%Y_%m_%d")}.</b>\n\n'

    counter = cumulative_temp = cunmulative_humidity\
        = cumulative_feels_like = 0
    description = []

    for ele in data:
        tm = datetime.fromtimestamp(ele.dt, tz=UTC) + \
            timedelta(seconds=obj.city.timezone)
        cur_day = tm.day
        if cur_day != ref_day:
            res += f'<b>Дата: {tm.strftime("%Y_%m_%d")}.</b>\n\n'
            ref_day = cur_day
        description = ', '.join([ele.description for ele in ele.weather])
        res += f'''Время: {tm.strftime("%H")}:00.
Описание: {description};
Температура: {ele.main.temp} {chr(176)}С;
Ощущается как: {ele.main.feels_like} {chr(176)}С;\n'''
        if ele.rain:
            res += f'Количество осадков: {ele.rain.get("1h")} мм;\n'
        elif ele.snow:
            res += f'Количество осадков: {ele.snow.get("1h")} мм;\n'
        res += f'Влажность: {ele.main.humidity} %.\n\n'

    return res


async def create_modes_builder() -> InlineKeyboardBuilder:

    modes = {Modes.CURRENT_SHORT: 'Погода на текущий момент (краткий формат)',
             Modes.CURRENT_LONG: 'Погода на текущий момент (подробный формат)',
             Modes.FORECAST: 'Погода на ближайшие 5 дней'}
    builder = InlineKeyboardBuilder()
    for key, value in modes.items():
        builder.button(text=f'{value}',
                       callback_data=f"{key.value}")
    builder.adjust(1, 1)
    return builder


async def create_locations_builder(
        lst: list[LocationByName]) -> InlineKeyboardBuilder:

    builder = InlineKeyboardBuilder()
    for ele in lst:
        txt = f'{ele.name} ({ele.country}'
        if ele.state:
            txt += f' - {ele.state})'
        else:
            txt += ')'
        builder.button(text=txt,
                       callback_data=f"{ele.lat} {ele.lon}")
    builder.adjust(1, 1)
    return builder
