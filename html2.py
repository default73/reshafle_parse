from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    with open('3rd_Quarter_2023_Changes.txt', 'r') as file:
        lines = file.readlines()
        first_line = lines[0].strip()  # Получаем первую строку файла и удаляем лишние пробелы
        other_lines = '\n'.join(lines[1:])  # Объединяем остальные строки файла с помощью переноса строки
    with open('config.txt', 'r') as file:
        lines = file.readlines()
        title = lines[0].strip()
    return render_template('index.html', first_line=first_line, other_lines=other_lines, title=title)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
