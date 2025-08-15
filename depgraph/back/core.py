from pathlib import Path
import logging
import networkx as nx

from pprint import pprint

from .graph import GraphControl
from .utils import (
    get_all_files_list,
    scan_python_modules
)
from .analyzer.python_analyzer import PythonFileAnalyzer





logger = logging.getLogger(__name__)


def start_process(local_path: Path):

    if not local_path.exists():
        raise FileExistsError(f'path {local_path} does not exist')
    
    if not local_path.is_dir():
        raise FileExistsError(f'path {local_path} is not a directory')
    
    all_files = get_all_files_list(local_path)
    logger.info(f'found {len(all_files)} files in {local_path}')

    analyzer = PythonFileAnalyzer(local_path)

    for file in all_files:
        if file.suffix == '.py':
            analyzer.get_imports(file)
        
    python_modules = scan_python_modules(local_path)
    dependencies = analyzer.results
    return create_graph(dependencies, python_modules)

def create_graph(dependencies, python_modules):
    
    G = GraphControl()
    G.add_modules_to_graph(python_modules)
    G.add_dependencies_to_graph(dependencies)
    G.draw_dependency_table()
    G.draw_graph()
    G.print_nx_nodes()
    return G.graph