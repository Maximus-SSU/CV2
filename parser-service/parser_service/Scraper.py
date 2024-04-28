import requests
import os
import time
from tqdm import tqdm
import urllib3
from bs4 import BeautifulSoup

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
def getNewUrl(newUrl):
    r=requests.get(newUrl,verify=False)
    return r.text

################################################################################################################
# Считываем из БД все необходимые категории
def openCategoriesDocument():
    category_links = []
    categories = get_links_category()
    for category in categories:
        category_links.append([category.name, category.link, category.pagenum])
    return category_links

################################################################################################################
# Парсим страничку, вытаскиваем оттуда все, что нас интересует
def ParsePage(soup, item_group,preparedLinks):
    soup=soup.find('div', class_="catalog_block")
    rawLinks=soup.findAll('a') #Список всех картинок (ммм, суп, как вкусно)

    for rawLink in rawLinks:
        rawLink_link= rawLink.get('href') 
        picture_link= rawLink.find('img')
        if picture_link is not None:
            # debug MODE:
            #####################################################################
            # count+=1
            # print("\n________________________________________________________")
            # print("\n********************************************************")
            # print(count)
            # print("\n********************************************************")
            # print(rawLink)
            # print("\n********************************************************")
            # print(picture_link)
            # print("\n********************************************************")
             #####################################################################
            pictureLink_title= picture_link.get('title')
            pictureLink_upload_raw=picture_link.get('src')
            pictureLink_upload=MAIN_LINK_DOMEN+pictureLink_upload_raw
            preparedlink=MAIN_LINK_DOMEN+rawLink_link
            preparedLinks.append([item_group,transliterate(pictureLink_title),preparedlink,pictureLink_upload])
        
    return preparedLinks

################################################################################################################
#Парсим все (касательно ссылок)
def Parse(preparedLinks,item_group, startUrl,max_pages_in_group):
    if max_pages_in_group>0:
        for page_count in range (1,max_pages_in_group+1):
            url=startUrl+str(page_count)
            # print("\nTRY SCRAPPING : "+ url+"\n")
            Soup=BeautifulSoup(getNewUrl(url),'lxml')
            preparedLinks=ParsePage(Soup,item_group,preparedLinks)
            page_count+=1
        return preparedLinks     
    else:
        url=startUrl
        # print("\nTRY SCRAPPING : "+ url+"\n")
        Soup=BeautifulSoup(getNewUrl(url),'lxml')
        preparedLinks=ParsePage(Soup,item_group,preparedLinks)
        return preparedLinks 
      

################################################################################################################
#Ф-я создания ссылки для загрузки страницы 
def CreateLinkDocument(img_links):
    for link in img_links:
        add_link_image(link)


################################################################################################################
def ParseLinks():
    delete_all_link_images()
    # ClearImgLinksDocument(img_links_path)
    preparedLinks=[]
    start_DATA=openCategoriesDocument()
    k=len(start_DATA)
    for i in tqdm(range(0,k)):
    # for i in range(0,k):
       preparedLinks= Parse(preparedLinks,start_DATA[i][0],start_DATA[i][1],int(start_DATA[i][2]))
    #################################################################
    # debug mode
    # Parse(start_DATA[0][0],start_DATA[0][1],start_DATA[0][2])
    ###############################################################
    CreateLinkDocument(preparedLinks)
    parsed_count= len(preparedLinks)
    print(f"\n * SUCCESSFULLY SCRAPPED [{parsed_count}] LINKS\n")
    return parsed_count


##################################################################################################################
##################################################################################################################
##################################################################################################################
# Блок загрузчика картинок


# #####################################################################################

# #функции для чтения и записи файла, в котором хранится позиция последнего спарсенного файла.
def check_write(value):
    try:
        with open(CHECKER_PATH, 'w') as file:
            file.write(str(value))
    except Exception as e:
        print("\nCheck WRITE -", e)
#####################################################################################
# Сосчитать чекер
def check_read(value):
    try:
        with open(CHECKER_PATH, 'r') as file:
            value = int(file.read())
        return value
    except Exception as e:
        print("\n*Check READ - :", e)
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
        # Открываем файл в режиме 'w' для перезаписи содержимого
        with open(CHECKER_PATH, 'w') as file:
            file.write("0")  # Записываем "0" в файл
        print("Файл check.txt успешно перезаписан.")

    except Exception as e:
        # Обработка ошибок при попытке перезаписать файл
        print("Ошибка при перезаписи файла check.txt:", e)

################################################################################################
#Основные функции
#Загрузка изображения
def download_image(image_url, new_filename):

    # Отправляем GET-запрос для загрузки страницы
    response = requests.get(image_url,verify=False)

    # Проверяем успешность запроса
    if response.status_code == 200:
        
        # Создаем папку, если она не существует
        if not os.path.exists(SAVE_DIRECTORY):
            os.makedirs(SAVE_DIRECTORY)
    
        img_filename = new_filename
        # Путь для сохранения изображения
        save_path = os.path.join(SAVE_DIRECTORY, img_filename)

        # Сохраняем изображение на диск
        with open(save_path, 'wb') as f:
            f.write(response.content)
        # print("Изображение успешно сохранено:", save_path)

    else:
        print("Ошибка при загрузке страницы:", response.status_code)


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
def Data_splitter(data_input, start_position):
    check_counter = 1
    print("\n*START POSITION = ", start_position)
    for data in tqdm(data_input[start_position:]):
        name=create_image_name(data)
        download_image(data.dwnloadlink,name)
        check_counter += 1
        check_write(start_position+check_counter)
    
    print("\n\n***EXECUTED SUCCESSFULLY!***\n SCRAPPED = ", check_counter,"PAGES")
    return check_counter


#####################################################################################
#Основная функция:  в ней происходит именно скраппинг страниц.
def startScrapper():
    readyLinks=get_links_images()
    pages=len(readyLinks)
    scrapper_data=readyLinks[:pages] #Подгрузка подготовленных ссылок 
    scrapper_pos=0 #Текущая позиция скраппера

    scrapper_pos=check_read(scrapper_pos) # Проверяем, если скарппинг уже происходил, и необходимо начать с N позиции
    start_time = time.time() #Замеряем время
    scrapper_pos=scrapper_pos+Data_splitter(scrapper_data, scrapper_pos)# Парсим
    end_time = time.time() - start_time
    print("\n\nEXECUTION TIME: ",end_time) 
    scrapper_pos=check_write(scrapper_pos) #Записываем в лог текущую позицию 



def ClearStart():
    clear_all_tables()
    check_reset()
    read_links()
    ParseLinks()
    startScrapper()


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



