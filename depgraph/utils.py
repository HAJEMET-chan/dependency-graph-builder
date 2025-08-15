from typing import get_origin, get_args, Union, List, Dict, Optional

def _validate_structure(data, template_types, path=""):
    """
    Рекурсивно проверяет структуру и типы данных с поддержкой typing.
    :param data: dict, list или примитивные данные для проверки
    :param template_types: шаблон типа (str, int, List[str], Dict[str, int], Optional[str], Union[int, str], ...)
    :param path: для рекурсивного отслеживания места ошибки
    :return: None, выбрасывает TypeError или ValueError при несоответствии
    """
    origin = get_origin(template_types)
    args = get_args(template_types)

    if origin is None:
        # обычный тип (str, int и т.д.)
        if not isinstance(data, template_types):
            raise TypeError(f"Expected type {template_types.__name__} at '{path}', got {type(data).__name__}")
    elif origin is Union:
        # Union[...] или Optional[...]
        if not any((isinstance(data, arg) if arg is not type(None) else data is None) for arg in args):
            expected_names = ', '.join([a.__name__ if a is not type(None) else 'None' for a in args])
            raise TypeError(f"Expected type Union[{expected_names}] at '{path}', got {type(data).__name__}")
    elif origin in (list, List):
        if not isinstance(data, list):
            raise TypeError(f"Expected list at '{path}', got {type(data).__name__}")
        if args:
            for i, item in enumerate(data):
                _validate_structure(item, args[0], f"{path}[{i}]")
    elif origin in (dict, Dict):
        if not isinstance(data, dict):
            raise TypeError(f"Expected dict at '{path}', got {type(data).__name__}")
        if args:
            key_type, value_type = args
            for k, v in data.items():
                _validate_structure(k, key_type, f"{path}.key")
                _validate_structure(v, value_type, f"{path}[{k}]")
    else:
        raise TypeError(f"Unsupported type {template_types} at '{path}'")
