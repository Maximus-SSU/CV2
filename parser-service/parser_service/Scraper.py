import requests
import os
import time
from tqdm import tqdm
import urllib3
from bs4 import BeautifulSoup
import logging

# Из других файлов
from parser_service.db_links_init import read_links
from parser_service.db import get_links_category,add_link_image,get_links_images,clear_all_tables,delete_all_link_images


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) #убрать предупреждение  InsecureRequestWarning 
# (P.S. сайт хищника почему-то всегда с предупреждением)


# Основная ссылка на сайт
MAIN_LINK_DOMEN="https://саратов.хищник.рф"
 # Папка для сохранения изображения
SAVE_DIRECTORY = "../Data/ScrappedData/Images" 
CHECKER_PATH="../Data/check.txt"

# Настройка логгирования
logging.basicConfig(
    filename='../Data/scrapper.log',  # Имя файла для логов
    level=logging.INFO,  # Уровень логгирования
    format='%(asctime)s - %(levelname)s - %(message)s'  # Формат записей
)
##################################################################################################################
##################################################################################################################
##################################################################################################################
# Блок загрузчика ссылок
########################################################################################################
# Модуль транслитерации
# Словарь для транслитерации
def transliterate(text):
    translit_dict = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
    'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
    'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
    'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
    'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
    'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo',
    'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
    'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
    'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sch',
    'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
}
    translit_text = ''
    for char in text:
        if char in translit_dict:
            translit_text += translit_dict[char]
        else:
            translit_text += char
    return translit_text
#############################################################################################################

# #получаем готовый Url необходимой страницы для BS4, параметр verify можно отключить, в зависимости от сайта
def get_new_url(url):
    try:
        r = requests.get(url, verify=False)
        if r.status_code == 200:
            return r.text
        else:
            logging.error(f"Ошибка запроса: {url} - Статус: {r.status_code}")
            return None
    except Exception as e:
        logging.error(f"Ошибка запроса к {url}: {e}")
        return None

################################################################################################################
# Считываем из БД все необходимые категории
def open_categories_document():
    try:
        categories = get_links_category()
        category_links = [
            [category.name, category.link, category.pagenum]
            for category in categories
        ]
        return category_links
    except Exception as e:
        logging.error(f"Ошибка при открытии категорий: {e}")
        return []

################################################################################################################
# Парсим страничку, вытаскиваем оттуда все, что нас интересует
def parse_page(soup, item_group, prepared_links):
    catalog_block = soup.find("div", class_="catalog_block")
    if not catalog_block:
        logging.warning(f"Блок каталога не найден для {item_group}")
        return prepared_links

    raw_links = catalog_block.findAll("a")
    for raw_link in raw_links:
        raw_link_href = raw_link.get("href")
        picture_tag = raw_link.find("img")
        if picture_tag is not None:
            title = transliterate(picture_tag.get("title", ""))
            prepared_link = MAIN_LINK_DOMEN + raw_link_href
            upload_link = MAIN_LINK_DOMEN + picture_tag.get("src")
            prepared_links.append([item_group, title, prepared_link, upload_link])
    return prepared_links

################################################################################################################
#Парсим все (касательно ссылок)
def parse(prepared_links, item_group, start_url, max_pages):
    try:
        if max_pages > 0:
            for page_num in tqdm(range(1, max_pages + 1), desc=f"Парсинг {item_group}"):
                url = start_url + str(page_num)
                soup = BeautifulSoup(get_new_url(url), "lxml")
                if soup:
                    parse_page(soup, item_group, prepared_links)
        else:
            soup = BeautifulSoup(get_new_url(start_url), "lxml")
            if soup:
                parse_page(soup, item_group, prepared_links)
        return prepared_links
    except Exception as e:
        logging.error(f"Ошибка при парсинге {item_group}: {e}")
        return prepared_links

      

################################################################################################################
#Ф-я создания ссылки для загрузки страницы 
def create_link_document(img_links):
    try:
        for link in img_links:
            add_link_image(link)
    except Exception as e:
        logging.error(f"Ошибка при создании документов ссылок: {e}")


################################################################################################################

def  ParseLinks():
    delete_all_link_images()  # Очистка таблицы перед скраппингом
    prepared_links = []
    categories = open_categories_document()
    if not categories:
        logging.error("Нет категорий для парсинга.")
        return 0
    
    for category in tqdm(categories, desc="Парсинг категорий"):
        group_name = category[0]
        start_url = category[1]
        max_pages = int(category[2])
        prepared_links = parse(prepared_links, group_name, start_url, max_pages)
    
    create_link_document(prepared_links)
    parsed_count = len(prepared_links)
    logging.info(f"Успешно спарсено {parsed_count} ссылок.")
    return parsed_count

##################################################################################################################
##################################################################################################################
##################################################################################################################
# Блок загрузчика картинок


# #####################################################################################

# #функции для чтения и записи файла, в котором хранится позиция последнего спарсенного файла.
def check_write(value):
    try:
        with open(CHECKER_PATH, "w") as file:
            file.write(str(value))
        logging.info(f"Чекер обновлен значением: {value}")
    except Exception as e:
        logging.error(f"Ошибка записи в чекер: {e}")
#####################################################################################
# Сосчитать чекер
def check_read():
    try:
        with open(CHECKER_PATH, "r") as file:
            value = int(file.read())
        return value
    except Exception as e:
        logging.error(f"Ошибка чтения из чекера: {e}")
        return 0

#####################################################################################
# Открыть чекер 
def check_open():
    try:
        with open(CHECKER_PATH, 'r') as file:
            value = int(file.read())
        return value
    except Exception as e:
        print("\n*Check READ - :", e)
#####################################################################################
# Сброс файла, на котором лежит значение уже спарсенных картинок. (чекер)
def check_reset():
    try:
        with open(CHECKER_PATH, "w") as file:
            file.write("0")
        logging.info("Чекер сброшен.")
    except Exception as e:
        logging.error(f"Ошибка при сбросе чекера: {e}")
################################################################################################
#Основные функции
#Загрузка изображения
def download_image(image_url, new_filename):
    try:
        response = requests.get(image_url, verify=False)
        if response.status_code == 200:
            if not os.path.exists(SAVE_DIRECTORY):
                os.makedirs(SAVE_DIRECTORY)

            save_path = os.path.join(SAVE_DIRECTORY, new_filename)
            with open(save_path, "wb") as f:
                f.write(response.content)
            logging.info(f"Изображение сохранено: {save_path}")
        else:
            logging.error(f"Ошибка загрузки изображения {image_url} - Статус: {response.status_code}")
    except Exception as e:
        logging.error(f"Ошибка при загрузке изображения {image_url}: {e}")

#####################################################################################
# Функция для создание имени изображения.
def create_image_name(data_input):
    category=RepairArticleName (data_input.category)
    name=RepairArticleName(data_input.name)
    return str(category + "_" + name+".png")

######################################################################################
# Убрать запрещенные символы
def RepairArticleName(string):
    forbidden_symbols = ['<', '>', ':', '"', '/', '\\', '|', '?', '*','№','.']
    for symbol in forbidden_symbols:
        string = string.replace(symbol, '')
    return string


######################################################################################
# Функция, которая отслеживает процесс скраппинга и ведет счет загруженных картинок (закидывая их в check.txt)
def data_splitter(data_input, start_position):
    check_counter = 0
    for i, data in enumerate(tqdm(data_input[start_position:], desc="Загрузка изображений", unit="изображений")):
        image_name = create_image_name(data)
        download_image(data.dwnloadlink, image_name)
        check_counter += 1
        check_write(start_position + check_counter)
    logging.info(f"Успешно загружено {check_counter} изображений с позиции {start_position}.")
    return check_counter


#####################################################################################
#Основная функция:  в ней происходит именно скраппинг страниц.
def startScrapper():
    ready_links = get_links_images()
    pages = len(ready_links)
    scrapper_pos = check_read()  # Узнаем, откуда продолжать

    start_time = time.time()  # Замеряем время
    data_splitter(ready_links, scrapper_pos)  # Парсим
    end_time = time.time() - start_time

    logging.info(f"Время выполнения: {end_time} секунд.")
    check_write(scrapper_pos + data_splitter(ready_links, scrapper_pos))  # Обновляем чекер




def clear_start():
    clear_all_tables()
    check_reset()
    read_links()  # Читаем ссылки для скраппинга
    ParseLinks  # Парсим ссылки
    startScrapper()  # Начинаем скраппинг изображений
    logging.info("Скраппинг завершен.")


######################################################################################
# #ВНИМАНИЕ, для самого начала скраппинга нужно поставить значение внутри check в 0 
# (в ClearStart делается автоматически)
    



##################################################################################################################
##################################################################################################################
##################################################################################################################
# Запуск всего скрапера. Очистка чекера и таблиц БД, считывание ссылок для скачивания, загрузка изображений.

def ClearStart():
    clear_all_tables()
    check_reset()
    read_links()
    ParseLinks()
    startScrapper()

####################################################################################



