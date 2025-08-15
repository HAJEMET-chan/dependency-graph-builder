from pathlib import Path
import logging
import networkx as nx

from pprint import pprint

from .graph import (
                    modules_to_nx_nodes, 
                    print_nx_nodes, 
                    add_dependencies_to_graph,
                    draw_graph,
                    draw_dependency_table
                    )
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
    nx_nodes = modules_to_nx_nodes(python_modules)
    dependencies = analyzer.results
    
    G = nx.Graph()
    G.add_nodes_from(nx_nodes)

    add_dependencies_to_graph(G, dependencies)
    draw_dependency_table(G)
    draw_graph(G)

    print_nx_nodes(G)