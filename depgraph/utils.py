from pathlib import Path
from typing import Iterator, Optional, Union, Dict
import logging


logger = logging.getLogger(__name__)


def get_all_files_list(
    path: Union[str, Path],
    recursive: bool = True,
    extensions: Optional[set[str]] = None,
    ignore_hidden: bool = True,
    sort: bool = True
) -> list[Path]:
    """
    Получает список файлов в указанной директории.

    Args:
        path (Union[str, Path]): Путь к директории или файлу.
        recursive (bool, optional): Идти ли в подпапки. По умолчанию True.
        extensions (Optional[set[str]], optional): 
            Набор расширений для фильтрации (без точки, в нижнем регистре). 
            Если None — берутся все файлы. Пример: {"jpg", "png"}.
        ignore_hidden (bool, optional): Пропускать ли скрытые файлы и папки. По умолчанию True.
        sort (bool, optional): Сортировать ли результат. По умолчанию True.

    Returns:
        list[Path]: Список путей к найденным файлам.

    Raises:
        FileNotFoundError: Если путь не существует.
        NotADirectoryError: Если путь не является директорией (кроме случая, когда это файл).
    """
    path = Path(path).expanduser().resolve()

    if not path.exists():
        raise FileNotFoundError(f"Path does not exist: {path}")

    def _iter_files(p: Path) -> Iterator[Path]:
        if p.is_file():
            if _is_valid_file(p):
                # logger.info(f'found file {p}')
                yield p
            return
        if not p.is_dir():
            return

        try:
            for entry in p.iterdir():
                if ignore_hidden and entry.name.startswith('.'):
                    continue
                if entry.is_dir():
                    if recursive:
                        yield from _iter_files(entry)
                elif _is_valid_file(entry):
                    # logger.info(f'found file {entry}')
                    yield entry
        except PermissionError:
            return

    def _is_valid_file(f: Path) -> bool:
        if not f.is_file():
            return False
        if extensions:
            return f.suffix.lower().lstrip('.') in extensions
        return True

    files = list(_iter_files(path))
    return sorted(files) if sort else files


def scan_python_modules(root_dir: Path) -> Dict[str, Path]:
    """
    Сканирует root_dir и возвращает словарь всех импортируемых модулей/пакетов:
    { 'package.module': Path_to_module_or___init__.py }
    
    Args:
        root_dir (Path): корневая директория для сканирования
    
    Returns:
        Dict[str, Path]: словарь модулей и пакетов
    """
    modules = {}
    for path in root_dir.rglob("*.py"):
        rel_path = path.relative_to(root_dir).with_suffix("")
        parts = rel_path.parts
        if parts[-1] == "__init__":
            # Пакет
            full_name = ".".join(parts[:-1])
        else:
            # Модуль
            full_name = ".".join(parts)
        if full_name:
            modules[full_name] = path.resolve()
    return modules
