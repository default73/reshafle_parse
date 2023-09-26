import datetime
import random
import re
import shutil
from time import sleep

import requests
from bs4 import BeautifulSoup


def parse_changes(quarter, limit):
    # Отправляем GET-запрос к странице и получаем HTML-код
    response = requests.get(
        f'https://liquipedia.net/counterstrike/index.php?title=Player_Transfers/{quarter}&offset=&limit={limit}&action=history')  # Замените ссылку на нужную страницу
    html = response.text

    # Создаем объект BeautifulSoup для парсинга HTML
    soup = BeautifulSoup(html, 'html.parser')

    # Далее продолжайте использовать BeautifulSoup для извлечения информации из HTML-кода
    # Например, поиск тегов <li> с атрибутом data-mw-revid
    li_tags = soup.find_all('li', attrs={'data-mw-revid': True})

    # Извлекаем значения data-mw-revid из найденных тегов
    data_mw_revid_values = [tag['data-mw-revid'] for tag in li_tags]



    # Выводим значения
    print(data_mw_revid_values)
    return data_mw_revid_values


def parse_diff(old, quarter):
    should_continue = True

    while should_continue:
        response = requests.get(
            f'https://liquipedia.net/counterstrike/index.php?title=Player_Transfers/{quarter}&diff=prev&oldid={old}')
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

        # Находим тег <td> с классом "diff-ntitle"
        td_tag = soup.find('td', class_='diff-ntitle')

        # Получение содержимого элемента <title>
        title = soup.title

        # Получение текстового содержимого заголовка
        title_text = title.string if title else None

        if title_text == "Rate Limited":
            print("БЛОК ПО IP")
            input("Пройди капчу на https://liquipedia.net, после чего нажми Enter.")
        else:
            should_continue = False

        if td_tag is not None:
            # Извлекаем текст из тега <td>
            td_text = td_tag.get_text(strip=True)
        else:
            return

        # Ищем дату и время с помощью регулярных выражений
        pattern = r'(\d{2}:\d{2}, \d{1,2} \w+ \d{4})'
        matches = re.findall(pattern, td_text)

        # Извлекаем первое совпадение (если оно есть)
        date_time = matches[0] if matches else None

        text = ""

        # Выводим значение
        print("-------------------------")
        text += "-------------------------\n"
        print(date_time)
        text += date_time + "\n"

        # Находим все теги <tr>
        tr_tags = soup.find_all('tr')

        # Проходимся по каждому тегу <tr>
        for tr in tr_tags:
            # Находим все теги <td> с классами 'diff-deletedline' или 'diff-addedline'
            td_tags = tr.find_all('td', class_=lambda value: value and (
                    'diff-deletedline' in value or 'diff-addedline' in value) if value else False)

            # Проходимся по каждому тегу <td>

            for td in td_tags:
                # Находим тег <div> внутри тега <td>
                div_tag = td.find('div')

                # Проверяем, что тег <div> найден и имеет текст
                if div_tag and div_tag.text:
                    # Извлекаем текст из тега <div>
                    div_text = div_tag.text.strip()

                    # Выводим значение
                    # print(div_text)

                    # Ищем значения name и date с помощью регулярных выражений
                    name_match = re.search(r'\bname=([^|}]+)', div_text)
                    date_match = re.search(r'\bdate=([^|}]+)', div_text)

                    # Извлекаем значения
                    name = name_match.group(1) if name_match else None
                    date = date_match.group(1) if date_match else None

                    # Выводим значения
                    if len(td_tags) < 2 and len(td_tags) > 0:
                        print("Запись добавлена:")
                        print(f'name: {name}', f'date: {date}')
                        print()
                        text += "Запись добавлена:\n" + "Ник: " + str(name) + " Дата: " + str(date) + "\n\n"
                        break
                    if len(td_tags) >= 2:
                        print("Запись изменена:")
                        print(f'name: {name}', f'date: {date}')
                        print()
                        text += "Запись изменена:\n" + "Ник: " + str(name) + " Дата: " + str(date) + "\n\n"
                        break
        try:
            with open(quarter + "_Changes.txt", "r") as file:
                lines = file.readlines()
                if date_time + "\n" not in lines:  # Проверяем, содержит ли файл нужное значение
                    write_changes(quarter + "_Changes.txt", text)
        except:
            with open(quarter + "_Changes.txt", "w") as file:
                file.write("")
                write_changes(quarter + "_Changes.txt", text)

def write_changes(file, text):
    # Имя исходного файла
    filename = file

    # Создаем имя временного файла
    tempfile = "temp.txt"

    # Читаем содержимое исходного файла
    with open(filename, "r") as file:
        lines = file.readlines()

    # Вставляем новый текст через 2 строки
    lines.insert(2, text + "\n")

    # Записываем содержимое во временный файл
    with open(tempfile, "w") as temp:
        temp.writelines(lines)

    # Заменяем исходный файл временным файлом
    shutil.move(tempfile, filename)


# parse_changes("3rd_Quarter_2023")
# parse_diff('2553162', '2552982')


def auto_run():
    #uarter = "3rd_Quarter_2023"
    with open("config.txt", "r") as file:
        lines = file.readlines()
    quarter = lines[0]
    with open(quarter + "_idChanges.txt", "a"):
        pass
    id_changes = parse_changes(quarter, 5000)
    id_changes.sort()

    max_retries = 5
    retry_count = 0
    success = False
    for i in range(len(id_changes)):
        while retry_count < max_retries and not success:
            try:
                with open(quarter + "_idChanges.txt", "r") as file:
                    lines = file.readlines()
                    if id_changes[i] + "\n" not in lines:  # Проверяем, содержит ли файл нужное значение
                        parse_diff(id_changes[i], quarter)
                        sleep(random.randrange(5, 10))
                        with open(quarter + "_idChanges.txt", "a") as file:
                            file.write(id_changes[i] + "\n")
                    success = True
                    print(id_changes[i])
            except Exception as ex:
                print(ex)
                retry_count += 1
                sleep(random.randrange(5, 10))
            if retry_count >= max_retries:
                print("Превышено максимальное количество попыток.")
                break

        retry_count = 0
        success = False

        i += 1


    # Получение текущей даты и времени
    current_datetime = datetime.datetime.now()

    with open(quarter + "_Changes.txt", 'r+') as file:
        lines = file.readlines()
        lines[0] = "Обновлено - " + str(current_datetime) + '\n'  # Замена первой строки файла
        file.seek(0)  # Перемещение указателя в начало файла
        file.writelines(lines)  # Запись измененных строк обратно в файл


if __name__ == '__main__':
    while True:
        auto_run()
        print(datetime.datetime.now())
        sleep(300)
