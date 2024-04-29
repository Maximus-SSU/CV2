# import os
# import logging


# from parser_service.db import add_category_link,delete_all_category_links

# PATH_TO_LINKS_FILE= '../Data/categorylinks.txt'
# # Чтение файла и обработка данных
# def read_links():
#     delete_all_category_links()
#     file_path=PATH_TO_LINKS_FILE
#     # Проверяем, что файл существует
#     if not os.path.exists(file_path):
#         raise FileNotFoundError(f"Файл {file_path} не найден")

#     # Открываем файл и читаем строки
#     with open(file_path, 'r', encoding='utf-8') as file:
#         lines = file.readlines()  # Считываем все строки в списке

#     # Обрабатываем каждую строку
#     for line in lines:
#         line = line.strip()  # Удаляем пробелы в начале и в конце строки

#         # Разделяем строку по символу '|'
#         parts = line.split('|')

#         # Проверяем, что строка содержит три элемента
#         if len(parts) == 3:
#             # Подготовка данных
#             name = parts[0].strip()  # Категория
#             link = parts[1].strip()  # Ссылка
#             pagenum = int(parts[2].strip())  # Номер страницы (преобразуем в целое число)

#             # Добавляем в базу данных
#             try:
#                 add_category_link([name, link, pagenum])
#             except Exception as e:
#                 logging.error(f"Ошибка при добавлении категории: {e}")

#         else:
#             logging.warning(f"Неверный формат строки: {line}")

# # # Используем функцию process_file для чтения файла и добавления данных в базу данных
# # if __name__ == "__main__":
# #     file_path = "path/to/your/file.txt"  # Укажите путь к вашему файлу с данными
# #     process_file(file_path)


import os
import logging
import aiofiles
from parser_service.db import delete_all_category_links, add_category_link

# Path to the file containing the category links
ROOT = os.getcwd()
PATH_TO_LINKS_FILE = os.path.join(ROOT, "Data/categorylinks.txt")

# Asynchronous function for reading links and processing them
async def read_links():
    await delete_all_category_links()  # Ensure asynchronous execution

    # Check if the file exists
    if not os.path.exists(PATH_TO_LINKS_FILE):
        raise FileNotFoundError(f"File {PATH_TO_LINKS_FILE} not found")

    # Asynchronous file reading
    async with aiofiles.open(PATH_TO_LINKS_FILE, 'r', encoding='utf-8') as file:
        lines = await file.readlines()  # Read all lines asynchronously

    # Process each line
    for line in lines:
        line = line.strip()  # Strip any leading/trailing whitespace

        # Split the line by the '|' character
        parts = line.split('|')

        # Ensure the line contains three elements
        if len(parts) == 3:
            # Prepare data
            name = parts[0].strip()  # Category
            link = parts[1].strip()  # Link
            pagenum = int(parts[2].strip())  # Page number (converted to integer)

            # Add to the database asynchronously
            try:
                await add_category_link([name, link, pagenum])
            except Exception as e:
                logging.error(f"Error adding category: {e}")

        else:
            logging.warning(f"Invalid line format: {line}")
