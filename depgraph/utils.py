from typing import get_origin, get_args, Union

def _validate_structure(data, template_types, path=""):
    origin = get_origin(template_types)
    args = get_args(template_types)

    if isinstance(template_types, dict):
        if not isinstance(data, dict):
            raise TypeError(f"Expected dict at '{path}', got {type(data).__name__}")
        for key, expected_type in template_types.items():
            if key not in data:
                raise ValueError(f"Missing key '{path + key}' in data")
            _validate_structure(data[key], expected_type, f"{path}{key}.")
    elif origin is Union:
        if not any(
            (arg is type(None) and data is None) or isinstance(data, arg)
            for arg in args
        ):
            expected = ', '.join([a.__name__ if a is not type(None) else "None" for a in args])
            raise TypeError(f"Expected {expected} at '{path}', got {type(data).__name__}")
    elif origin:
        # list, dict, etc.
        if origin is list:
            if not isinstance(data, list):
                raise TypeError(f"Expected list at '{path}', got {type(data).__name__}")
            for i, item in enumerate(data):
                _validate_structure(item, args[0], f"{path}[{i}].")
        elif origin is dict:
            if not isinstance(data, dict):
                raise TypeError(f"Expected dict at '{path}', got {type(data).__name__}")
            key_type, val_type = args
            for k, v in data.items():
                _validate_structure(k, key_type, f"{path}.<key>")
                _validate_structure(v, val_type, f"{path}[{k}].")
        else:
            raise TypeError(f"Unsupported type {template_types} at '{path}'")
    else:
        # обычный тип
        if not isinstance(data, template_types):
            raise TypeError(f"Expected {template_types.__name__} at '{path}', got {type(data).__name__}")
