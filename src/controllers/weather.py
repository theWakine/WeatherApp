import time
import aiohttp
import datetime
from src.settings.config import settings
from babel.dates import format_date


class Weather:
    def __init__(self, city_name: str):
        self.city_name = city_name
        self.access_token = settings.access_token

    async def main(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"http://api.openweathermap.org/data/2.5/forecast?q={self.city_name}&appid={self.access_token}&units=metric&lang=ru"
                ) as response:
                    data = await response.json()
                    if data["cod"] != "200":
                        return False

                    code_weather = {
                        "Clear": "Ясно",
                        "Clouds": "Облачно",
                        "Rain": "Дождь",
                        "Snow": "Снег",
                        "Thunderstorm": "Гроза",
                        "Drizzle": "Морось",
                        "Mist": "Туман",
                    }

                    result = []
                    day_id = 1  # Начинаем с ID 1 для сегодняшнего дня
                    for forecast in data['list'][:24*3:8]:  # Получаем данные на 3 дня (каждые 8 записей = 1 день)
                        day_result = {
                            'id': day_id,  # Добавляем ID для каждого дня
                            'date': forecast['dt_txt'],
                            'day_of_week': format_date(datetime.datetime.strptime(forecast['dt_txt'], '%Y-%m-%d %H:%M:%S'), 'E', locale='ru'),
                            'temperature': round(forecast['main']['temp']),
                            "weather": code_weather[forecast['weather'][0]['main']],
                            'humidity': forecast['main']['humidity'],
                            'pressure': forecast['main']['pressure'],
                            'wind_speed': forecast['wind']['speed'],
                        }
                        if day_id == 1:  # Добавляем время заката и рассвета для первого дня
                            day_result["city"] = data["city"]["name"]
                            day_result['sunrise'] = data['city']['sunrise']
                            day_result['sunset'] = data['city']['sunset']
                        result.append(day_result)
                        day_id += 1  # Увеличиваем ID для следующего дня

                    return result
