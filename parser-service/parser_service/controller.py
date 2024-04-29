from fastapi import FastAPI

import os
from fastapi.middleware.cors import CORSMiddleware
#For Swager
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import RedirectResponse
#For uvicorn
import uvicorn

#Мои
from parser_service.db import get_links_category, clear_all_tables
from parser_service.Scraper import ParseLinks,startScrapper,ClearStart
from parser_service.db_links_init import read_links



app = FastAPI()
############################################################
# Разрешаем все источники и все методы и заголовки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


###########################################################
#Эндпоинты

#Основная функция - "чистый" старт

@app.get("/Start")
def let_it_start():
    return ClearStart()
# # Функция для получения списка всех ссылок
# @app.get("/Links")
# def links_list():
#     return get_links_category()

# Функция для получения списка всех ссылок
@app.get("/Clear")
def Clear_db():
    return clear_all_tables()

# @app.get("/ReadLinks")
# def Read_Links_from_db():
#     return read_links()

# Функция для получения списка всех ссылок
@app.get("/Parse/Links")
def parse_links():
    Links=ParseLinks()
    return Links

@app.get("/Parse/Images")
def parse_images():
    startScrapper()


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

def start():
    uvicorn.run("parser_service.controller:app", reload=True)