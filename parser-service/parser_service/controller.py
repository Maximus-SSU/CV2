# from fastapi import FastAPI

# import os
# from fastapi.middleware.cors import CORSMiddleware
# #For Swager
# from fastapi.openapi.docs import get_swagger_ui_html
# from fastapi.responses import RedirectResponse
# #For uvicorn
# import uvicorn

# #Мои
# from parser_service.db import get_links_category, clear_all_tables
# from parser_service.Scraper import parse_links,start_scrapper,clear_start
# from parser_service.db_links_init import read_links



# app = FastAPI()
# ############################################################
# # Разрешаем все источники и все методы и заголовки
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# ###########################################################
# #Эндпоинты

# #Основная функция - "чистый" старт

# @app.get("/Start")
# def let_it_start():
#     return clear_start()
# # # Функция для получения списка всех ссылок
# # @app.get("/Links")
# # def links_list():
# #     return get_links_category()

# # Функция для получения списка всех ссылок
# @app.get("/Clear")
# def Clear_db():
#     return clear_all_tables()

# # @app.get("/ReadLinks")
# # def Read_Links_from_db():
# #     return read_links()

# # Функция для получения списка всех ссылок
# @app.get("/Parse/Links")
# def parse_links():
#     Links=parse_links()
#     return Links

# @app.get("/Parse/Images")
# def parse_images():
#     start_scrapper()

# # Обработчик для корневого URL
# @app.get("/")
# async def redirect_to_docs():
#     return RedirectResponse(url="/docs")

# # Добавляем обработчик для получения HTML-страницы Swagger UI
# @app.get("/docs", include_in_schema=False)
# async def custom_swagger_ui_html():
#     return get_swagger_ui_html(openapi_url="/openapi.json", title="Swagger UI")
  
# # Добавляем обработчик для получения схемы OpenAPI
# @app.get("/openapi.json", include_in_schema=False)
# async def get_openapi_endpoint():
#     return app.openapi()

# def start():
#     uvicorn.run("parser_service.controller:app", reload=True)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import RedirectResponse
import uvicorn

# Мои импорты
from parser_service.db import get_links_category, clear_all_tables
from parser_service.Scraper import parse_links, start_scrapper, clear_start
from parser_service.db_links_init import read_links

app = FastAPI()

# Разрешаем все источники, методы, и заголовки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Асинхронные эндпоинты

# Основная функция - "чистый" старт
@app.get("/Start")
async def let_it_start():
    await clear_start()  # Ensure this is awaited
    return {"status": "started"}

# Функция для очистки всех данных
@app.get("/Clear")
async def clear_db():
    await clear_all_tables()
    return {"status": "cleared"}

# Функция для получения списка всех ссылок
@app.get("/Links")
async def links_list():
    links = await get_links_category()  # Ensure async DB operations are awaited
    return links

# Функция для парсинга ссылок
@app.get("/Parse/Links")
async def parse_links_endpoint():
    parsed_links = await parse_links()
    return {"parsed_links": parsed_links}

# Функция для парсинга изображений
@app.get("/Parse/Images")
async def parse_images():
    await start_scrapper()  # Await the scraper
    return {"status": "scraping"}

# Обработчик для корневого URL
@app.get("/")
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

# Добавляем обработчик для получения HTML-страницы Swagger UI
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Swagger UI")

# Добавляем обработчик для получения схемы OpenAPI
@app.get("/openapi.json", include_in_schema=False)
async def get_openapi_endpoint():
    return app.openapi()

# Функция для запуска Uvicorn
def start():
    uvicorn.run("parser_service.controller:app", reload=True)
