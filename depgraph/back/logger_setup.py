# logger_setup.py
import logging

def setup_logger():
    # Получаем корневой логгер
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # минимальный уровень логов

    # Формат логов
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')

    # Консольный обработчик
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Файловый обработчик
    file_handler = logging.FileHandler('app.log', encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
