import pickle

pickle.DEFAULT_PROTOCOL
from sys import platform

from multiprocessing import Process

import subprocess, os

import shutil

# log
import logging

# date
import datetime
today = datetime.datetime.today().strftime("%Y-%m-%d-%H.%M.%S")

# Путь до папки с приложением
path_app = os.path.abspath(os.curdir)

# Модуль для парсинга файлов ini
import configparser

# add filemode="w" to overwrite
logging.basicConfig(filename="log.log", level=logging.INFO)

# Если у нас платформа линукс, тогда приписываем корень linux, чтобы обрабатывать все пути от него
if platform == "linux" or platform == "linux2":
    os.chdir('/')
    separator = '/'
else:
    separator = '\\'

# Приписываем путь до файла ini
config = configparser.ConfigParser()
config.read(f'{path_app}{separator}/PATH.ini')

print(f'{path_app}{separator}PATH.ini')


# Класс Mainer
class Miner:
    # Переменная для отслеживания первого запуска
    first_launch = True

    # Переменные с путями
    path_create_to_plots = config.get('section_path_plots', 'path_create_to_plots')
    path_where_transfer_plot = config.get('section_path_plots', 'path_where_transfer_plot')
    min_proofs = int(config.get('section_value_proofs', 'min_value_proofs'))
    max_proofs = int(config.get('section_value_proofs', 'max_value_proofs'))
    path_chia_exe = config.get('section_path_chia', 'path_chia_exe')
    path_chia_plot_exe = config.get('section_path_chia', 'path_chia_plot_exe')
    path_plot = config.get('section_path_chia', 'path_plot')

    p = config.get('section_key_plot', 'p')
    f = config.get('section_key_plot', 'f')
    t = config.get('section_key_plot', 't')
    r = config.get('section_key_plot', 'r')
    K = config.get('section_key_plot', 'K')
    d = config.get('section_key_plot', 'd')
    u = config.get('section_key_plot', 'u')
    v = config.get('section_key_plot', 'v')
    n = config.get('section_key_plot', 'n')

    process_chia_exe = ''

    #  Инициализация приложения
    def __init__(self):
        super().__init__()  # Инициализируем приложение

        print('Майнер запущен!')  # Информируем пользователя о запуске майнера
        self.start_miner()  # Метод запуска майнера
        logging.info(f'Запуск метода start_mainer(). 74. {today}')

    def start_miner(self):
        '''
        Метод обработки плотов
        :return:
        '''

        logging.info(f'Запуск метода start_mainer(). 82. {today}')
        # Если директория уже не пуста, тогда начинем работу с файлом
        if len(os.listdir(self.path_create_to_plots)) > 0:
            self.first_launch = False  # Переводим значение первого запуска в False
            logging.info(f'Плот был найден. 87. {today}')
            # Запускаем метод работы с плотом
            self.working_plotter()
            return

        elif len(os.listdir(self.path_create_to_plots)) <= 0:
            # Если был произведен первый запуск
            if self.first_launch:
                print('Первый запуск')  # Информируем пользователя об первом запуске
                self.first_launch = False  # Переводим переменную первого запуска в положение false
                self.run_chia_exe()
                return

    def working_plotter(self):
        '''
        Метод работы с плотом
        Перенести или удалить
        :return:
        '''
        print('Плот найден')  # Информируем пользователя о том что плот найден
        logging.info(f'Начинается работа с plot. 112. {today}')
        # Обрабатываем плот
        p = subprocess.Popen(
            [
                self.path_chia_exe,
                'plots',
                'check',
                '-g',
                self.path_plot
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

        stdout, stderr = p.communicate()
        logging.info(f'{stdout}. 124. {today}')
        index_proofs = stdout.find('Proofs')  # Ищем в строке слово Proofs
        index_value_proofs = index_proofs + 7  # Прибовляем к найденому иедексу
        # Делаем срез из строки stdout по индексам index_value_proofs и index_value_proofs + 2
        res_proofs = int(stdout[index_value_proofs:index_value_proofs + 2:])

        # Если линукс, включаем многопоточность
        if platform == "linux" or platform == "linux2":
            self.process_chia_exe = Process(target=self.run_chia_exe)
            self.process_chia_exe.start()

        # Если proofs больше или равно min_proofs и меньше или равно max_proofs, переносим плот
        if self.min_proofs <= res_proofs <= self.max_proofs:
            logging.info(f'Proofs входит в рамки между максимальным и минимальным значениями. 136. {today}')
            try:
                # Записываем имя файла, которое будем перемещать
                name_file_to_replace = os.listdir(self.path_create_to_plots)[0]
                # Проверка существования директории
                if os.path.exists(f'{self.path_where_transfer_plot}{res_proofs}'):
                    logging.info(f'Директория найдена, будет переносится plot. 142. {today}')
                    try:
                        # Переносим файл в директорию
                        print(f'Перенос плота {res_proofs}')  # Информируем пользователя о названии плота
                        logging.info(f'Перенос плота {res_proofs}. 146. {today}')
                        shutil.move(
                            f'{self.path_create_to_plots}{name_file_to_replace}',
                            f'{self.path_where_transfer_plot}{str(res_proofs)}{separator}{name_file_to_replace}'
                        )
                        if platform != "linux" and platform != "linux2":
                            self.run_bat()  # Запуск батника
                        # self.start_miner()  # Перезапуск метода

                    except FileNotFoundError:
                        logging.error(f'Файл небыл найден! 157. {today}')
                        print('Файл перемещен!')  # Если файл не найден, обрабатываем как ошибку
                    except FileExistsError:
                        logging.error(f'Есть ошибка в существующем файле! 160. {today}')
                        print('Файл перемещен!')  # Если что-то не так с файлом, выводим сообщение

                else:
                    try:
                        os.mkdir(f'{self.path_where_transfer_plot}{res_proofs}')  # Создаем директорию
                        print('Создание директории')  # Инофрмируем пользователя о создании директории
                        logging.info(f'Создание директории {res_proofs}. 168. {today}')

                        try:
                            print(f'Перенос плота {res_proofs}')  # Информируем пользователя о названии плота
                            logging.info(f'Переносим plot {res_proofs}. 172. {today}')
                            # Переносим файл плота
                            shutil.move(
                                f'{self.path_create_to_plots}{name_file_to_replace}',
                                f'{self.path_where_transfer_plot}{str(res_proofs)}{separator}{name_file_to_replace}'
                            )
                        except FileNotFoundError:
                            logging.error(f'Файла был перемещен. 184. {today}')
                            print('Файл перемещен')
                        except FileExistsError:
                            logging.error(f'Ошибка файла. 185. {today}')
                            print('Файл перемещен')
                    except FileNotFoundError:
                        logging.warning(f'Директория существет. 190. {today}')
                        print('Директория существует')

                    except FileExistsError:
                        logging.warning(f'Директория существует. 194. {today}')
                        print('Директория существует')
            # Если не находим файл, который должна переместить
            except IndexError:
                logging.error(f'Файл небыл найден. 198. {today}')
                print('Файл перемещен')
        else:
            logging.info(f'Удаление плота. 203. {today}')
            try:
                print(f'Удаление плота {res_proofs}')  # Информируем пользователя о названии плота
                logging.info(f'Удаление плота {res_proofs}! 207. {today}')
                # Удаляем файл plot
                os.remove(f'{self.path_create_to_plots}{separator}{os.listdir(self.path_create_to_plots)[0]}')
            except FileNotFoundError:
                logging.error(f'Произошла ошибка, файл небыл найден!!! 214. {today}')
        if platform != "linux" and platform != "linux2":
            self.run_bat()  # Запуск батника
            self.run_chia_exe()
        self.process_chia_exe.join()
        self.process_chia_exe.close()
        return

    def run_chia_exe(self):
        print('Запуск Chia.exe')  # Информируем пользователя о запуске chia
        logging.info(f'Запуск chia.exe. 228. {today}')

        p = subprocess.Popen(
            [
                self.path_chia_plot_exe,
                '-p',
                self.p,
                '-f',
                self.f,
                '-t',
                self.t,
                '-r',
                self.r,
                '-K',
                self.K,
                '-d',
                self.d,
                '-u',
                self.u,
                '-v',
                self.v,
                '-n',
                self.n
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

        # Здесь мы обрабатываем все то, что приходит в stdout
        for line in p.stdout:
            print(line.decode().strip())
            logging.info(f'{line.decode().strip()} {today}')

        self.start_miner()  # Перезапуск метода
        return

    def run_bat(self):
        '''
        Метод запуска 2 exe файла, который запускает в себе bat файла
        :return:
        '''
        print('Запуск .bat файла')  # Информируем пользователя о запуске bat файла
        logging.info(f'Запуск bat. 259. {today}')
        os.startfile(f'{path_app}\\run_bat.exe')  # Запуск файла в новом окне
        return


# Создание экземпляра класса Miner и старт всего приложения
if __name__ == '__main__':
    miner = Miner()
