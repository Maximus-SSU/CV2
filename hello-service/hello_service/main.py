from fastapi import FastAPI

import os
from fastapi.middleware.cors import CORSMiddleware
#For Swager
#For Swager
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import RedirectResponse
#For uvicorn
import uvicorn




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

#Основная функция - привет мир


@app.get("/hello")
async def func():
    return {"message": "Hello World"}


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
    uvicorn.run("hello-service.main:app", reload=True)