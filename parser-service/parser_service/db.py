from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

# указываем параметры для подключения БД
# DATABASE_URL = 'postgresql://postgres:7237@localhost/cv'


load_dotenv()
database_host = os.getenv('POSTGRES_HOST')
database_port = os.getenv('POSTGRES_PORT')
database_name = os.getenv('POSTGRES_DB')
database_user = os.getenv('POSTGRES_USER')
database_password=os.getenv('POSTGRES_PASSWORD')

print(database_host, database_port, database_name, database_user, database_password)

DATABASE_URL = f'postgresql://{database_user}:{database_password}@{database_host}:{database_port}/{database_name}'

############################################################################################################
# Запускаем "движок", подключаемся к БД
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
db = SessionLocal()
############################################################################################################
#Классы таблиц
class LinksCategoryModel(Base):
    __tablename__ = 'linkscategory'
    id = Column(Integer, primary_key=True,autoincrement=True)
    name = Column(String)
    link= Column(String)
    pagenum=Column(Integer)

class LinksImagesModel(Base):
    __tablename__ = 'linksimages'
    id = Column(Integer, primary_key=True, autoincrement=True) 
    category = Column(String)
    name = Column(String)
    link= Column(String)
    dwnloadlink=Column(String)


############################################################################################################
#Методы
# Вытащить все ссылки на категории
async def get_links_category():
    data = db.query(LinksCategoryModel).all()
    return data
# Вытащить все ссылки на изображения
async def get_links_images():
    data = db.query(LinksImagesModel).all()
    return data


async def add_link_image(data_in):
    new_data= LinksImagesModel(category=data_in[0], name=data_in[1], link=data_in[2], dwnloadlink=data_in[3])
    db.add(new_data)
    db.commit()

async  def add_category_link(data_in):
    new_data=LinksCategoryModel(name=data_in[0],link=data_in[1],pagenum=data_in[2]) 
    db.add(new_data)
    db.commit()

async def delete_all_category_links():
    # Удаляем все записи из таблицы LinksCategoryModel
    db.query(LinksCategoryModel).delete()  # Удаляет все строки в таблице
    db.commit()  # Фиксируем изменения, чтобы удалить записи из базы данных

async  def delete_all_link_images():
    # Удаляем все записи из таблицы LinksImagesModel
    db.query(LinksImagesModel).delete()  # Удаляет все строки в таблице
    db.commit()  # Фиксируем изменения

async  def clear_all_tables():
    # Удаление всех записей из LinksCategoryModel
    delete_all_category_links()
    
    # Удаление всех записей из LinksImagesModel
    delete_all_link_images()
    
    print("Все записи успешно удалены.")

# import os
# from dotenv import load_dotenv
# import asyncio
# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# from sqlalchemy.orm import sessionmaker, declarative_base
# from sqlalchemy import Column, Integer, String, select,text

# # Подгружаем переменные среды
# load_dotenv()

# database_name = os.getenv("DATABASE_NAME")
# database_password = os.getenv("DATABASE_PASSWORD")

# DATABASE_URL = f'postgresql+asyncpg://{database_name}:{database_password}@localhost/cv'

# # Запускаем асинхронный движок
# engine = create_async_engine(DATABASE_URL, echo=True)
# SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
# Base = declarative_base()

# # Определяем классы таблиц
# class LinksCategoryModel(Base):
#     __tablename__ = 'LinksCategory'
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     name = Column(String)
#     link = Column(String)
#     pagenum = Column(Integer)

# class LinksImagesModel(Base):
#     __tablename__ = 'linksimages'
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     category = Column(String)
#     name = Column(String)
#     link = Column(String)
#     dwnloadlink = Column(String)

# # Асинхронные методы
# async def get_links_category():
#     async with SessionLocal() as session:
#         stmt = select(LinksCategoryModel)
#         result = await session.execute(stmt)
#         data = result.scalars().all()
#         return data

# async def get_links_images():
#     async with SessionLocal() as session:
#         stmt = select(LinksImagesModel)
#         result = await session.execute(stmt)
#         data = result.scalars().all()
#         return data

# async def add_link_image(data_in):
#     async with SessionLocal() as session:
#         new_data = LinksImagesModel(
#             category=data_in[0], 
#             name=data_in[1], 
#             link=data_in[2], 
#             dwnloadlink=data_in[3]
#         )
#         session.add(new_data)
#         await session.commit()

# async def add_category_link(data_in):
#     async with SessionLocal() as session:
#         new_data = LinksCategoryModel(
#             name=data_in[0], 
#             link=data_in[1], 
#             pagenum=data_in[2]
#         )
#         session.add(new_data)
#         await session.commit()

# async def delete_all_category_links():
#     async with SessionLocal() as session:
#         await session.execute(text("DELETE FROM LinksCategory"))
#         await session.commit()

# async def delete_all_link_images():
#     async with SessionLocal() as session:
#         await session.execute(text("DELETE FROM linksimages"))
#         await session.commit()

# async def clear_all_tables():
#     try:
#         await delete_all_category_links()
#         await delete_all_link_images()
#         print("Все записи успешно удалены.")
#     except Exception as e:
#         print("Ошибка при удалении записей:", e)

# # Убедитесь, что инициализация базы данных выполнена
# async def init_db():
#     async with engine.begin() as conn:
#         # Создаем все таблицы, которые определены
#         await conn.run_sync(Base.metadata.create_all)