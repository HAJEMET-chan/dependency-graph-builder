from pathlib import Path
from typing import Iterator, Optional, Union, Dict, List, Tuple
import logging
import networkx as nx
import pandas as pd
from networkx.drawing.nx_pydot import to_pydot
import pydot
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET


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

def modules_to_nx_nodes(modules):
    nodes = []
    for full_name, path in modules.items():
        if path.name == "__init__.py":
            node_type = "package"
        else:
            node_type = "module"

        nodes.append((
            full_name,  # ключ узла — полное имя, чтобы было уникально
            {
                "path": path,
                "type": node_type
            }
        ))
    return nodes


def print_nx_nodes(G: nx.Graph):
    """
    Выводит список узлов графа с атрибутами в виде таблицы.
    
    Args:
        G (nx.Graph): граф NetworkX
    """
    nodes_data = [(node, *attrs.values()) for node, attrs in G.nodes(data=True)]
    
    # Определяем названия колонок: первая — имя узла, остальные — ключи атрибутов
    if len(G.nodes) > 0:
        attr_keys = list(next(iter(dict(G.nodes(data=True)).values())).keys())
    else:
        attr_keys = []
    
    df = pd.DataFrame(nodes_data, columns=["node"] + attr_keys)
    print(df.to_string(index=False))

def add_dependencies_to_graph(
    G: nx.Graph,
    dependencies: List[Tuple[Path, List[Tuple[str, Path]]]]
):
    """
    Добавляет рёбра в граф NetworkX на основе списка зависимостей.

    Args:
        G (nx.Graph): граф с уже добавленными узлами
        dependencies (list): список зависимостей в формате:
            [
              (Path_to_source, [
                  (full_module_name, Path_to_module),
                  ...
              ]),
              ...
            ]
    """
    # Создаём маппинг: path → имя узла
    path_to_node = {attrs["path"]: node for node, attrs in G.nodes(data=True)}

    for source_path, deps in dependencies:
        source_node = path_to_node.get(source_path)
        if not source_node:
            continue  # исходный модуль не найден в графе

        for dep_full_name, dep_path in deps:
            target_node = path_to_node.get(dep_path)
            if target_node:
                G.add_edge(source_node, target_node)




def draw_graph(G: nx.Graph, filename="graph.png"):
    """
    Красиво визуализирует граф зависимостей с помощью pydot.

    Args:
        G (nx.Graph): граф NetworkX с атрибутами 'type'
        filename (str): путь для сохранения изображения
    """
    pydot_graph = to_pydot(G)

    # Настройка узлов
    for node in pydot_graph.get_nodes():
        node_name = node.get_name().strip('"')  # убираем лишние кавычки
        attrs = G.nodes[node_name]
        node_type = attrs.get("type", "module")
        if node_type == "package":
            node.set_shape("box")
            node.set_style("filled")
            node.set_fillcolor("lightblue")
        else:
            node.set_shape("ellipse")
            node.set_style("filled")
            node.set_fillcolor("lightgreen")
        node.set_fontname("Courier")
        node.set_fontsize(10)

    # Настройка рёбер
    for edge in pydot_graph.get_edges():
        edge.set_color("gray")
        edge.set_arrowsize(0.7)

    # Сохраняем
    pydot_graph.write_png(filename)
    print(f"Graph saved to {filename}")


def draw_dependency_table(G: nx.Graph, filename="dependencies.xml"):
    """
    Сохраняет зависимости модулей из графа G в XML.
    """
    root = ET.Element("modules")

    for node in sorted(G.nodes()):
        node_type = G.nodes[node].get("type", "module")
        module_elem = ET.SubElement(root, "module", name=node, type=node_type)

        for neighbor in sorted(G.neighbors(node)):
            neighbor_type = G.nodes[neighbor].get("type", "module")
            ET.SubElement(module_elem, "dependency", name=neighbor, type=neighbor_type)

    tree = ET.ElementTree(root)
    tree.write(filename, encoding="utf-8", xml_declaration=True)
    print(f"Dependencies saved to {filename}")