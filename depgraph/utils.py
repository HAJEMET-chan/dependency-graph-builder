import logging
import types
from pathlib import Path
from typing import Any, Dict, List, Set, Union, get_args, get_origin

import networkx as nx
from pyvis.network import Network

logger = logging.getLogger(__name__)


__all__ = ["_validate_structure", "_find_all_python_modules"]


def _validate_structure(data: Dict, template_types: Any, path: str = "") -> None:
    origin = get_origin(template_types)
    args = get_args(template_types)

    if isinstance(template_types, dict):
        if not isinstance(data, dict):
            raise TypeError(f"Expected dict at '{path}', got {type(data).__name__}")
        for key, expected_type in template_types.items():
            if key not in data:
                raise ValueError(f"Missing key '{path + key}' in data")
            _validate_structure(data[key], expected_type, f"{path}{key}.")

    elif origin in (Union, types.UnionType):
        if not any(
            (arg is type(None) and data is None) or isinstance(data, arg)
            for arg in args
        ):
            expected = ", ".join(
                [a.__name__ if a is not type(None) else "None" for a in args]
            )
            raise TypeError(
                f"Expected {expected} at '{path}', got {type(data).__name__}"
            )

    elif origin is list:
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

    elif origin:
        raise TypeError(f"Unsupported type {template_types} at '{path}'")

    else:
        if not isinstance(data, template_types):
            raise TypeError(
                f"Expected {template_types.__name__} at '{path}', got {type(data).__name__}"
            )


def _find_all_python_modules(dir_path: Path) -> List[Path]:

    if not dir_path.exists():
        raise FileExistsError(f"specified path {str(dir_path)} does not exist")

    if not dir_path.is_dir():
        raise FileExistsError(f"specified path {str(dir_path)} is not a directory")

    logger.debug(f"start searching python modules in {str(dir_path)}")

    modules = list(dir_path.glob("**/*.py"))

    for i in range(len(modules)):
        modules[i] = modules[i].relative_to(dir_path)
        logger.debug(f"Found Python module in {str(modules[i])}")
    else:
        logger.info(f"founded {len(modules)} modules in {str(dir_path)}")

    return modules


def _find_project_roots(project_root: Path) -> Set[Path]:
    """
    Находит только корневые пакеты в проекте.
    Корневой пакет = папка, содержащая __init__.py,
    но её родитель НЕ является пакетом.

    Args:
        project_root (Path): путь до корня проекта.

    Returns:
        Set[Path]: множество путей к корневым пакетам.
    """
    roots = set()

    for init_file in project_root.rglob("__init__.py"):
        candidate = init_file.parent
        parent_init = candidate.parent / "__init__.py"

        # если у родителя нет __init__.py → это root
        if not parent_init.exists():
            roots.add(candidate)

    return roots


def unique_paths(paths: List[Path]) -> List[Path]:
    """
    Убирает дубликаты из списка относительных путей.
    Возвращает их в нормализованном виде (без ./ и ../).

    Args:
        paths (List[Path]): список относительных путей

    Returns:
        List[Path]: список уникальных относительных путей
    """
    seen = set()
    unique = []
    for p in paths:
        # Нормализуем путь (убираем ./, ../)
        norm = Path(p).resolve().relative_to(Path.cwd())
        if norm not in seen:
            seen.add(norm)
            unique.append(norm)
    return unique


def visualize_graph(graph: nx.DiGraph, output_file: Path = Path("graph.html")) -> None:
    """
    Визуализирует directed graph с PyVis, используя label нод.

    Args:
        graph (nx.DiGraph): Граф для визуализации.
        output_file (Path): Путь к HTML-файлу для вывода.
    """
    if not isinstance(output_file, Path):
        raise TypeError(f"output_file must be a pathlib.Path, got {type(output_file)}")

    # Создаём сеть PyVis, отключаем notebook режим
    net = Network(
        directed=True,
        height="750px",
        width="100%",
        notebook=False,
        bgcolor="#ffffff",
        font_color="#000000",
    )

    # Добавляем ноды с их label
    for node, data in graph.nodes(data=True):
        label = data.get("label", str(node))
        net.add_node(str(node), label=str(label))

    # Добавляем рёбра
    for from_node, to_node in graph.edges():
        net.add_edge(str(from_node), str(to_node))

    # Генерация и сохранение HTML
    net.show(str(output_file), notebook=False)
    print(f"Graph saved to {output_file}")


def _to_dep_dict(modules: List) -> Dict[Path, List]:
    dep_dict: Dict[Path, List] = {}

    for module in modules:
        dep_dict[module] = []

    return dep_dict


def _get_sibling_python_files(file_path: Path) -> List[Path]:
    
    siblings = []
    root = file_path.parts[0]
    parent_folder = file_path.parent.resolve()

    for path in parent_folder.iterdir():

        if path.is_dir() and (path / "__init__.py").exists():
            sib_path = path / "__init__.py"

            siblings.append(path / "__init__.py")
            continue

        if path.is_file() and path.name != "__init__.py":
            siblings.append(path)
            continue

    relative_paths = []

    for p in siblings:
        try:
            # ищем 'depgraph' в пути
            depgraph_index = p.parts.index(root)
            # строим относительный путь начиная с 'depgraph'
            rel = Path(*p.parts[depgraph_index:])
            relative_paths.append(rel)
        except ValueError:
            # 'depgraph' нет в этом пути
            pass

    return relative_paths



    