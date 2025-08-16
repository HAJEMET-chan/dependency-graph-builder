import logging
import sys

def setup_logger():
    # Создаём корневой логгер
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # минимальный уровень для всего приложения

    # Формат сообщений
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Вывод в stdout
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)  # уровень для консоли
    console_handler.setFormatter(formatter)

    # Запись в файл
    file_handler = logging.FileHandler("app.log", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)  # более подробные логи в файл
    file_handler.setFormatter(formatter)

    # Чтобы не дублировались сообщения при повторной настройке
    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger
