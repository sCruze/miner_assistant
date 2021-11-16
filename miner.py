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
today = datetime.datetime.today().strftime("%d-%m-%Y Время: %H:%M:%S")

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
    t2 = config.get('section_key_plot', 't2')
    r = config.get('section_key_plot', 'r')
    K = config.get('section_key_plot', 'K')
    d = config.get('section_key_plot', 'd')
    u = config.get('section_key_plot', 'u')
    v = config.get('section_key_plot', 'v')
    n = config.get('section_key_plot', 'n')

    id_plot = 0  # id майнера для записи в файл, изменяется в метоа

    # Перемныые, в которые записываются процессы
    process_chia_exe = ''
    process_clear_cache = ''

    counter = 0  # Количество проходов за время работы майнера до завершения его работы
    counters_info = {}  # Объект, в который мы заисываем proofs_plot = value count

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
        # Если нет директории, куда будет записываться готовый плот, создаем ее
        if '1' not in os.listdir(self.path_plot):
            os.mkdir(f'{self.path_plot}1')

        # Запускаем метод отчистки дректории
        self.clear_dir()

        # Если линукс, включаем многопоточность
        if platform == "linux" or platform == "linux2":
            self.process_chia_exe = Process(target=self.run_chia_exe)
            self.process_clear_cache = Process(target=self.clear_cache)

            #
            if self.first_launch and self.process_clear_cache != '':
                self.process_clear_cache.start()
                self.process_clear_cache.join()

        logging.info(f'Запуск метода start_mainer(). 82. {today}')

        # Если директория уже не пуста, тогда начинем работу с файлом
        if len(os.listdir(self.path_create_to_plots)) > 0:
            # self.first_launch = False  # Переводим значение первого запуска в False
            logging.info(f'Плот был найден. 87. {today}')
            # Запускаем метод работы с плотом
            self.working_plotter()
            return
        # Пустая директория
        elif len(os.listdir(self.path_create_to_plots)) <= 0:
            # Если был произведен первый запуск
            if self.first_launch:
                print('Первый запуск')  # Информируем пользователя об первом запуске
                self.run_chia_exe()
                return

    def working_plotter(self):
        '''
        Метод работы с плотом
        Перенести или удалить
        :return:
        '''
        self.first_launch = False
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
        # Отправляем полученный пруфс в метод, который записывает файл с данными
        self.write_counter(res_proofs)
        # Если линукс, включаем многопоточность
        if platform == "linux" or platform == "linux2":
            self.process_chia_exe.start()

        # Если proofs больше или равно min_proofs и меньше или равно max_proofs, переносим плот
        if self.min_proofs <= res_proofs <= self.max_proofs:
            logging.info(f'Proofs входит в рамки между максимальным и минимальным значениями. 136. {today}')
            try:
                # Записываем имя файла, который будем перемещать
                name_file_to_replace = os.listdir(self.path_create_to_plots)[0]
                # Проверка существования директории
                if os.path.exists(f'{self.path_where_transfer_plot}{res_proofs}'):
                    logging.info(f'Директория найдена, будет переносится plot. 142. {today}')
                    try:
                        # Переносим файл в директорию
                        print(f'Перенос плота {res_proofs}')  # Информируем пользователя о названии плота
                        logging.info(f'Перенос плота {res_proofs}. 146. {today}')
                        if self.process_clear_cache != '':
                            self.process_clear_cache.start()
                            self.process_clear_cache.join()
                            # self.process_clear_cache.close()
                        shutil.move(
                            f'{self.path_create_to_plots}{name_file_to_replace}',
                            f'{self.path_where_transfer_plot}{str(res_proofs)}{separator}{name_file_to_replace}'
                        )
                        if platform != "linux" and platform != "linux2":
                            self.run_bat()  # Запуск батника
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
                            if self.process_clear_cache != '':
                                self.process_clear_cache.start()
                                # self.process_clear_cache.close()
                            # Переносим файл плота
                            shutil.move(
                                f'{self.path_create_to_plots}{name_file_to_replace}',
                                f'{self.path_where_transfer_plot}{str(res_proofs)}{separator}{name_file_to_replace}'
                            )
                            if platform != "linux" and platform != "linux2":
                                self.run_bat()  # Запуск батника
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

        return

    def run_chia_exe(self):
        # Логика отображения информации
        with open(f'{path_app}/counters/counter.txt', 'r+') as fr:
            lines = fr.readlines()  # Записываем все строки из файла

            counter_id = 0  # Количесвто id

            # Если id майнера, который запущен сейчас, не равен 0
            if self.id_plot > 0:
                print('\n')  # Делаем отступ в 2 строки сверху
                print('*' * 50)  # Выводим 50 звездочек, для разграничения
                # Перебираем список строк из файла
                for line in lines:
                    # Ищем все элементы, де есть id
                    if 'id: ' in line:
                        # Если нашли id, прибавляем 1 в переменную counter_id
                        counter_id = counter_id + 1
                # Если мы нашли всего 1 id
                if counter_id == 1:
                    # Перебираем список со строками
                    for line in lines:
                        # Выводим все строки в терминал
                        print(line)

                # Если количество id больше 1
                elif counter_id > 1:

                    start = None  # Перемнная, в которую передаем индекс нашего id в списке
                    # Перебираем список со сроками и вытаскиваем индексы
                    for i in range(len(lines)):
                        # Перебираем все строки из файла и ищем строку с id: ищем наш
                        if f'id: {self.id_plot}' in lines[i]:
                            # Добавляем номер индекса в переменную
                            start = i
                    # Пербираем элементы из списка от определенного индекса
                    for line in lines[start:]:
                        print(line[:-1])
                        # if 'id: ' in line or 'Дата: ' in line or 'Всего плотов: ' in line:
                        #     print(line)  # Выводим все строки от определенного индекса
                        # else:
                        #     print(line[:-1])
                print('*' * 50)  # Выводим 50 звездочек для разграничения
                print('\n')
        print('Запуск Chia.exe')  # Информируем пользователя о запуске chia
        logging.info(f'Запуск chia.exe. 228. {today}')
        try:
            p = subprocess.Popen(
                [
                    self.path_chia_plot_exe,
                    '-p',
                    self.p,
                    '-f',
                    self.f,
                    '-t',
                    self.t,
                    # '-2',
                    # self.t2,
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
            # Если в переменной есть поцесс, закрываем его
            if self.process_chia_exe != '':
                self.process_chia_exe.close()
            self.start_miner()  # Перезапуск метода
        except Exception as e:
            logging.error(f'Ошибка запуска chia. Происходит отчистка каталога и переапуск метода')
            logging.error(f'{e}')
            self.clear_dir()  # Меод отчистки каталога
            self.start_miner()  # Метод старта майнера
        return

    def run_bat(self):
        '''
        Метод запуска 2 exe файла, который запускает в себе bat файла
        :return:
        '''
        print('Запуск .bat файла')  # Информируем пользователя о запуске bat файла
        logging.info(f'Запуск bat. 258. {today}')  # Логирование действия
        os.startfile(f'{path_app}\\run_bat.exe')  # Запуск файла в новом окне
        return

    def clear_dir(self):
        '''
        Метод отчистки директории
        :param dir_name:
        :return:
        '''
        print(f'Отчистка каталога {self.path_plot}')
        # print(f'Отчистка каталога {self.t2}')
        logging.info(f'Отчистка каталога {self.path_plot} .272.{today}')
        for the_file in os.listdir(self.path_plot):
            file_path = os.path.join(self.path_plot, the_file)
            try:
                if '1' not in os.listdir(self.path_plot):
                    os.remove(file_path)
            except Exception as e:
                logging.info(f'Найден файл 1. 278. {today}')
                logging.error(f'Ошибка отистки каталога. {e}. {today}')
        # for the_file in os.listdir(self.t2):
        #     file_path = os.path.join(self.t2, the_file)
        #     try:
        #         os.remove(file_path)
        #     except Exception as e:
        #         logging.error(f'Ошибка отистки каталога. {e}. {today}')

    def clear_cache(self):
        '''
        :return:
        '''
        print('Отчистка кэша')
        logging.info(f'Отчистка кэша. 146. {today}')
        subprocess.run(['sudo', 'home/a111/miner/clearcache.sh'])

    def write_counter(self, proofs):
        self.counter = self.counter + 1
        # Наименование файла
        name_file = f'counter'
        if proofs in self.counters_info:
            # Найден ключ proofs, увеличиваем значение
            self.counters_info[proofs] = self.counters_info[proofs] + 1
        else:
            # Ключа как proofs нет
            self.counters_info[proofs] = 1
        try:
            def write_line(fw):
                # Записываем id
                fw.write(f'id: {self.id_plot}\n')
                # Добовляем дату
                fw.write(f'Дата: {today}\n')  # Дата создания файла
                # Количество созданных плотов, за время работы программы до завершения
                fw.write(f'Всего плотов: {self.counter}\n')
                for count in sorted(self.counters_info.keys()):
                    # Запись значений из словаря в файл с вычислением процента
                    fw.write(
                        f'{count} = {self.counters_info[count]}  {to_fixed((int(self.counters_info[count]) / self.counter) * 100, 2)}%\n')

            def to_fixed(num, digits=0):
                '''
                Функция ограничения вывода чисел после запятой
                :param num:
                :param digits:
                :return:
                '''
                return f"{num:.{digits}f}"

            # Открываем файл для чтения
            with open(f'{path_app}/counters/{name_file}.txt', 'r+') as fr:
                # Передаем все строки из файла
                lines_to_file = fr.readlines()
                if len(lines_to_file) == 0:
                    with open(f'{path_app}/counters/{name_file}.txt', 'w+') as fw:
                        # Функция записи шаблона id, date, counter, lines
                        # Метод для записи шаблона
                        write_line(fw)
                else:
                    list_id = []  # Список id

                    for i in range(len(lines_to_file)):
                        if 'id: ' in lines_to_file[i]:
                            list_id.append(int(lines_to_file[i][4:-1]))
                    if self.id_plot == 0:
                        self.id_plot = int(list_id[-1]) + 1
                        with open(f'{path_app}/counters/{name_file}.txt', 'r+') as fw:
                            for line in lines_to_file:
                                fw.write(line)
                            # Метод для записи шаблона
                            write_line(fw)
                    with open(f'{path_app}/counters/{name_file}.txt', 'r+') as fw:
                        for i in range(len(lines_to_file)):
                            if f'id: {self.id_plot}' in lines_to_file[i] and i == 0:
                                write_line(fw)
                            elif f'id: {self.id_plot}' in lines_to_file[i]:
                                for line in lines_to_file[:i]:
                                    fw.write(line)
                                # Метод для записи шаблона
                                write_line(fw)

        except FileNotFoundError:
            #
            os.mkdir(f'{path_app}/counters')
            #
            self.write_counter(proofs)


# Создание экземпляра класса Miner и старт всего приложения
if __name__ == '__main__':
    miner = Miner()
