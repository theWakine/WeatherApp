import asyncio
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
import uvicorn
import random

from src.controllers.weather import Weather
from src.settings.log import Logger  # Импортируем Logger

# Инициализируем логгер
logger = Logger().get_logger()

app = FastAPI()
app.mount("/static", StaticFiles(directory="src/static"), name="static")

templates = Jinja2Templates(directory="src/templates")


@app.get("/", response_class=HTMLResponse)
async def start(request: Request):
    logger.info("Запрос на стартовую страницу")
    return templates.TemplateResponse(
        request=request,
        name="start.html",
        context={},
    )

@app.get("/", response_class=HTMLResponse)
async def redirect_to_random_city():
    logger.info("Перенаправление на случайный город")
    with open("src/settings/database.json", "r") as f:
        config = json.load(f)
        cities = config.get("city", [])
    
    if cities:
        random_city = random.choice(cities)["id"]
        logger.debug(f"Выбран случайный город: {random_city}")
        return RedirectResponse(url=f"/{random_city}", status_code=303)
    else:
        logger.warning("Нет доступных городов")
        return HTMLResponse("No cities available", status_code=404)

@app.get("/{city}", response_class=HTMLResponse)
async def read_root(city: str, request: Request):
    logger.info(f"Запрос на город: {city}")
    user_agent = request.headers.get('user-agent')
    with open("src/settings/database.json", "r") as f:
        config = json.load(f)
        cities = config.get("city", [])

    if not cities:
        logger.warning("Нет доступных городов")
        return RedirectResponse(url="/", status_code=303)

    user_cities = [city for city in cities if city.get("user_agent") == user_agent]

    if not user_cities:
        logger.warning("Нет городов для данного user-agent")
        return RedirectResponse(url="/", status_code=303)

    result = await Weather(city).main()
    
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"data": result, "cities": user_cities},
    )

@app.post("/add-city")
async def add_city(request: Request, city_name: str = Form(...)):
    logger.info(f"Добавление города: {city_name}")
    user_agent = request.headers.get('user-agent')
    with open("src/settings/database.json", "r+") as f:

        weather = Weather(city_name)
        result = await weather.main()

        if not result:
            logger.warning(f"Не удалось получить данные для города: {city_name}")
            return RedirectResponse(url="/", status_code=303)

        config = json.load(f)
        cities = config.get("city", [])
        
        # Проверка на наличие города для данного user-agent
        for city in cities:
            if city["name"] == city_name and city["user_agent"] == user_agent:
                logger.debug(f"Город уже существует: {city_name}")
                return RedirectResponse(url=f"/{city_name}", status_code=303)
        
        cities.append({"id": city_name, "name": city_name, "user_agent": user_agent})
        f.seek(0)
        json.dump(config, f, indent=4)
        logger.debug(f"Город  {city_name} добавлен для {user_agent}")
    
    if cities:
        random_city = random.choice(cities)["id"]
        logger.debug(f"Выбран случайный город после добавления: {random_city}")
        return RedirectResponse(url=f"/{random_city}", status_code=303)
    else:
        return RedirectResponse(url=f"/{city_name}", status_code=303)

@app.get("/delete-city/{city_id}")
async def delete_city(city_id: str, request: Request):
    logger.info(f"Удаление города: {city_id}")
    user_agent = request.headers.get('user-agent')
    with open("src/settings/database.json", "r+") as f:
        config = json.load(f)
        cities = config.get("city", [])
        cities = [city for city in cities if city["id"] != city_id]
        config["city"] = cities
        f.seek(0)
        f.truncate()
        json.dump(config, f, indent=4)
        logger.debug(f"Город {city_id} удален для {user_agent}")
    if cities:
        random_city = random.choice(cities)["id"]
        logger.debug(f"Выбран случайный город после удаления: {random_city}")
        return RedirectResponse(url=f"/{random_city}", status_code=303)
    else:
        return templates.TemplateResponse(
            name="start.html",
            context={},
            request=request,
        )

if __name__ == "__main__":
    logger.info("Запуск приложения")
    uvicorn.run("setup:app", host="0.0.0.0", reload=True)
