import os
import logging


from parser_service.db import add_category_link,delete_all_category_links

PATH_TO_LINKS_FILE= '../Data/categorylinks.txt'
# Чтение файла и обработка данных
def read_links():
    delete_all_category_links()
    file_path=PATH_TO_LINKS_FILE
    # Проверяем, что файл существует
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл {file_path} не найден")

    # Открываем файл и читаем строки
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()  # Считываем все строки в списке

    # Обрабатываем каждую строку
    for line in lines:
        line = line.strip()  # Удаляем пробелы в начале и в конце строки

        # Разделяем строку по символу '|'
        parts = line.split('|')

        # Проверяем, что строка содержит три элемента
        if len(parts) == 3:
            # Подготовка данных
            name = parts[0].strip()  # Категория
            link = parts[1].strip()  # Ссылка
            pagenum = int(parts[2].strip())  # Номер страницы (преобразуем в целое число)

            # Добавляем в базу данных
            try:
                add_category_link([name, link, pagenum])
            except Exception as e:
                logging.error(f"Ошибка при добавлении категории: {e}")

        else:
            logging.warning(f"Неверный формат строки: {line}")

# # Используем функцию process_file для чтения файла и добавления данных в базу данных
# if __name__ == "__main__":
#     file_path = "path/to/your/file.txt"  # Укажите путь к вашему файлу с данными
#     process_file(file_path)
