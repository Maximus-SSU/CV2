from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

# указываем параметры для подключения БД
# DATABASE_URL = 'postgresql://postgres:7237@localhost/cv'


load_dotenv()
database_name = os.getenv("DATABASE_NAME")
database_password=os.getenv("DATABASE_PASSWORD")


DATABASE_URL = f'postgresql://{database_name}:{database_password}@localhost/cv'

############################################################################################################
# Запускаем "движок", подключаемся к БД
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
db = SessionLocal()
############################################################################################################
#Классы таблиц
class LinksCategoryModel(Base):
    __tablename__ = 'LinksCategory'
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
def get_links_category():
    data = db.query(LinksCategoryModel).all()
    return data
# Вытащить все ссылки на изображения
def get_links_images():
    data = db.query(LinksImagesModel).all()
    return data


def add_link_image(data_in):
    new_data= LinksImagesModel(category=data_in[0], name=data_in[1], link=data_in[2], dwnloadlink=data_in[3])
    db.add(new_data)
    db.commit()

def add_category_link(data_in):
    new_data=LinksCategoryModel(name=data_in[0],link=data_in[1],pagenum=data_in[2]) 
    db.add(new_data)
    db.commit()

def delete_all_category_links():
    # Удаляем все записи из таблицы LinksCategoryModel
    db.query(LinksCategoryModel).delete()  # Удаляет все строки в таблице
    db.commit()  # Фиксируем изменения, чтобы удалить записи из базы данных

def delete_all_link_images():
    # Удаляем все записи из таблицы LinksImagesModel
    db.query(LinksImagesModel).delete()  # Удаляет все строки в таблице
    db.commit()  # Фиксируем изменения

def clear_all_tables():
    # Удаление всех записей из LinksCategoryModel
    delete_all_category_links()
    
    # Удаление всех записей из LinksImagesModel
    delete_all_link_images()
    
    print("Все записи успешно удалены.")