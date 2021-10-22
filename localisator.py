import os, shutil, time
from google_trans_new.google_trans_new import google_translator

class Russificator:
    FORBIDDEN = ['.py', '__pycache__', 'google_trans_new', 'build', 'dist', '.spec', 'LOCALISED', '.exe', '.mod']
    LOCALISED_DIR = 'LOCALISED'
    def __init__(self, is_translating: bool=True):
        self.is_translating = is_translating
        self.translator = google_translator()
    
    def _translate(self, line: str):
        tokens = line.split()
        try:
            param_name, text = tokens[0], ' '.join(tokens[1:])
            text = f'"{self.translator.translate(text[1:-1], "ru")}"'
            full_line = f'{param_name} {text}\n'
            content = full_line
        except IndexError: # Если пустая строка
            content = '\n'
        
        return content

    def _translate_file(self, russian_path: str, file_path: str):
        localisation_file_start_time = time.time()
        print('--------Локализация главного файла...')

        new_content = ''
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line_no, line in enumerate(lines):
                if line_no == 0:
                    new_content += f'l_russian:\n'
                elif self.is_translating:
                    new_content += self._translate(line)
                else:
                    new_content += line
                    
                # Принтуем каждый 5 раз прогресс локализации строк
                try:
                    if line_no % int(len(lines) / 5) == 0:
                        print(f'------------{int(line_no / len(lines) * 100)}% локализации файла')
                except ZeroDivisionError:
                    pass
        
        # Записываем то, что локализировали в файле
        with open(russian_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        
        # Принтуем о завершении
        localisation_file_end_time = round(time.time() - localisation_file_start_time, 2)
        print(f'------------Файл локализирован! {localisation_file_end_time}с.')

    def _translate_dir(self, localisation_file: str, localisation_file_no: int, russian_path: str, russian_dir: str, russian_files_count: int, language: str) -> None:
        localisation_file_start_time = time.time()
        print(f'--------Файл {localisation_file_no + 1}/{len(russian_dir)} {round(localisation_file_no / russian_files_count * 100, 2)}%')
        localisation_file_path = os.path.join(russian_path, localisation_file)
        new_content = ''
        with open(localisation_file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line_no, line in enumerate(lines):
                if line_no == 0:
                    new_content += f'l_russian:\n'
                elif self.is_translating:
                    new_content += self._translate(line)
                else:
                    new_content += line
                    
                # Принтуем каждый 5 раз прогресс локализации строк
                try:
                    if line_no % int(len(lines) / 5) == 0:
                        print(f'------------{int(line_no / len(lines) * 100)}% локализации файла')
                except ZeroDivisionError:
                    pass
        
        # Записываем то, что локализировали в файле
        with open(localisation_file_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        
        # Переименовываем файл
        new_name = localisation_file_path.replace(language, 'russian')
        os.rename(localisation_file_path, new_name)
        
        # Принтуем о завершении
        localisation_file_end_time = round(time.time() - localisation_file_start_time, 2)
        print(f'------------Файл локализирован! {localisation_file_end_time}с.')

    def start(self):
        start_time = time.time()
        print('Начало локализации...')

        # Фильтрация названий файлов в текущей дериктории и запись названий файлов модов
        mod_names = []
        current_dir = os.listdir()
        for file in current_dir:
            is_forbidden = False
            for forbidden_symbols in Russificator.FORBIDDEN:
                if forbidden_symbols in file:
                    is_forbidden = True
                    break
            if not is_forbidden:
                mod_names.append(file)
        
        # Начало локализации
        for mod_no, mod_name in enumerate(mod_names):
            mod_start_time = time.time()
            print(f'----{mod_no + 1}/{len(mod_names)}. Локализация {mod_name}')

            mod_in_localised = os.path.join(Russificator.LOCALISED_DIR, mod_name)

            # Проверка наличия мода в локализированной директории
            if not os.path.isdir(mod_in_localised):
                shutil.copytree(mod_name, mod_in_localised)

                # Проверка наличия дескриптора
                descriptor = False
                for name in os.listdir(mod_in_localised):
                    if '.mod' in name:
                        descriptor = True
                        break
                if descriptor:

                    # Проверка наличия файла "localisation" в моде
                    localisation = os.path.join(mod_in_localised, 'localisation')
                    if os.path.isdir(localisation):
                        
                        # Проверяем присутствует-ли изначальная русификация
                        localised = False
                        for file in os.listdir(localisation):
                            if 'russian' in file:
                                print('--------В моде уже присутствует локализация')
                                localised = True
                        if localised:
                            continue

                        # Теперь проверяем наличия папки с языковыми файлами
                        if '.' not in os.listdir(localisation)[0]:
                            language = os.listdir(localisation)[0]
                            language_path = os.path.join(localisation, language)

                            # Копируем языковую директорию и переименовываем его на "russian"
                            russian_path = os.path.join(localisation, 'russian')
                            shutil.copytree(language_path, russian_path)
                            russian_dir = os.listdir(russian_path)
                            russian_files_count = len(russian_dir)

                            # Перечисляем все файлы локализации в директории "russian" и локализируем их
                            for localisation_file_no, localisation_file in enumerate(russian_dir):
                                self._translate_dir(localisation_file, localisation_file_no, russian_path, russian_dir, russian_files_count, language)

                            mod_end_time = round(time.time() - mod_start_time, 2)
                            print(f'----Мод локализирован! {mod_end_time}с.')
                        
                        # Если в директории "localisation" присутствуют файлы, а не директории
                        else:
                            file_name = os.listdir(localisation)[0]
                            file_tokens = file_name.split('_')
                            file_path = os.path.join(localisation, file_name)

                            # Копируем файл с переименованием language на "russian" и локализируем
                            russian_name = '_'.join(file_tokens[:-1]) + '_russian.yml'
                            russian_path = os.path.join(localisation, russian_name)
                            self._translate_file(russian_path, file_path)

                    else:
                        print('--------Мод не нуждается в локализации')
                
                else:
                    print('--------Данная директория не является модом, из-за отсутвия дескриптора')

            else:
                print(f'--------Мод уже находится в {Russificator.LOCALISED_DIR}')
        
        end_time = round(time.time() - start_time, 2)
        print(f'< ЛОКАЛИЗАЦИЯ ОКОНЧЕНА УСПЕШНО ЗА {end_time}с. >')

print('''<{:=^32}>
Перед началом локализации киньте все моды (просто папку самого мода) в папку с этим файлом.
Или-же этот файл впрямь в папку C:\\Users\\<Пользователь>\\Documents\\Paradox Interactive\\Stellaris\\mod.
При окончании локализации локализированные моды будут лежать в папке LOCALISED.
'''.format(' ИСТРУКЦИЯ К ЛОКАЛИЗАТОРУ '))

is_translating = True if input('Использовать гугл переводчик, который довольно кривой, но он есть? (y/n): ').lower() == 'y' else False

localisator = Russificator(is_translating)
try:
    localisator.start()
except Exception as error:
    print(f'ERROR: {error}')
input()