import os

# Путь до папки с приложением
path_app = os.path.abspath(os.curdir)

# Модуль для парсинга файлов ini
import configparser

# Приписываем путь до файла ini
config = configparser.ConfigParser()
config.read(f'{path_app}\\PATH.ini')

path_to_bat = config.get('section_path_chia', 'path_bat')

print(path_app)

import subprocess

subprocess.run(
    [
        f'{path_to_bat}'
    ]
)
