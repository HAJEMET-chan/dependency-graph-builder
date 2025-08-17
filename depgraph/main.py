from pathlib import Path

from .analyzing.python_analyzer import PythonImportsAnalyzer
from .dep_finding.python_dep_finder import PythonDepFinder
from .graph_building.graph_creator import GraphCreator
from .logging_setup import setup_logger
from .utils import (
    _find_all_python_modules,
    _find_project_roots,
    _to_dep_dict,
    visualize_graph,

)

logger = setup_logger()


class Depgraph:

    def __init__(self) -> None:
        self._dep_finder = None
        self._graph_creator = None
        self._analyzer = None
        self._project_path = None
        self._save_file_path = None
        self._all_modules = None
        self._project_roots = None
        self._dep_dict = None
        self._graph = None
        self._suffix = ".html"

    def set_proj_path(self, path: str) -> None:

        if not isinstance(path, str):
            raise ValueError(f"path is need to be a string but given {type(path)}")

        temp_path = Path(path).resolve()

        if not temp_path.exists():
            FileExistsError(f"given path {str(temp_path)} does not exist")

        if not temp_path.is_dir():
            FileExistsError(f"given path {str(temp_path)} is not a string")

        self._project_path = temp_path

    def set_save_file_path(self, path: str) -> None:

        if not isinstance(path, str):
            raise ValueError(f"path is need to be a string but given {type(path)}")

        temp_path = Path(path).resolve()

        if not temp_path.exists():
            FileExistsError(f"given path {str(temp_path)} does not exist")

        if not temp_path.is_file():
            FileExistsError(f"given path {str(temp_path)} is not a file")

        if not temp_path.suffix == self._suffix:
            raise ValueError(
                f"given`s file suffix need to be '{self._suffix}' but given '{temp_path.suffix}'"
            )

        self._save_file_path = temp_path

    def start_dep_finding(self) -> None:

        self._prepare_for_start()
        self._dep_finder.start_dep_finding()

    def start_graph_generating(self) -> None:

        self._graph_creator.build_graph(self._dep_dict)
        self._graph = self._graph_creator._graph

    def _prepare_for_start(self) -> None:

        self._prepare_data()
        self._analyzer = PythonImportsAnalyzer(self._project_path)
        self._graph_creator = GraphCreator()
        self._dep_finder = PythonDepFinder(
            dir_path=self._project_path,
            project_roots=self._project_roots,
            dep_dict=self._dep_dict,
            modules=self._all_modules,
            analyser=self._analyzer,
        )

    def _prepare_data(self) -> None:

        if not self._project_path:
            raise ValueError(
                "project path not specified. use 'Depgraph.set_proj_path()' to set it"
            )

        if not self._save_file_path:
            raise ValueError(
                "save file path not specified. use 'Depgraph.set_save_file_path()' to set it"
            )

        self._all_modules = _find_all_python_modules(self._project_path)
        self._project_roots = _find_project_roots(self._project_path)
        self._dep_dict = _to_dep_dict(self._all_modules)

    def visualize_graph_pyvis(self):
        visualize_graph(
            self._graph,
            self._save_file_path,
        )


if __name__ == "__main__":
    dg = Depgraph()

    dg.set_proj_path(r"/home/hajemet/Рабочий стол/py/dependency-graph-builder")
    dg.set_save_file_path(
        r"/home/hajemet/Рабочий стол/py/dependency-graph-builder/graph.html"
    )
    dg.start_dep_finding()
    dg.start_graph_generating()
    dg.visualize_graph_pyvis()
    print("end")
