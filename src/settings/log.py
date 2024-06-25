import logging
import os
from datetime import datetime

class Logger:
    def __init__(self, name='weather_app', log_directory='logs/'):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Проверяем, есть ли уже обработчики у логгера
        if not self.logger.handlers:
            # Создаем директорию для логов, если она не существует
            if not os.path.exists(log_directory):
                os.makedirs(log_directory)
            
            # Создаем обработчик для записи логов в файл с именем, включающим временную метку
            timestamp = datetime.now().strftime('%d-%m-%Y')  # Изменен формат временной метки
            file_handler = logging.FileHandler(os.path.join(log_directory, f'app-{timestamp}.log'))
            file_handler.setLevel(logging.DEBUG)
            
            # Создаем форматтер и добавляем его в обработчик
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            
            # Добавляем обработчик в логгер
            self.logger.addHandler(file_handler)
            
            # Создаем обработчик для вывода логов в консоль только для уровня INFO
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
    
    def get_logger(self):
        return self.logger
