import logging
from pathlib import Path
from typing import Dict

import networkx as nx

logger = logging.getLogger(__name__)


class GraphCreator:
    def __init__(self):
        self._graph = nx.DiGraph()
        self._dep_dict: Dict[Path, list[Path]] = {}

    def _nodes_from_keys(self) -> None:
        for module in self._dep_dict.keys():
            self._node_from_path(module)

    def _node_from_path(self, module: Path) -> None:
        label = str(module.parent if module.stem == "__init__" else module)
        self._graph.add_node(module, label=label)
        logger.debug(f"Added {str(module)} module to graph")

    def _edges_from_dict(self) -> None:
        for importing_module in self._dep_dict.keys():
            self._edge_from_module_deps(importing_module)

    def _edge_from_module_deps(self, importing_module: Path) -> None:
        for imported_module in self._dep_dict[importing_module]:
            to_node = (
                imported_module.parent
                if imported_module.stem == "__init__"
                else imported_module
            )
            self._graph.add_edge(importing_module, to_node, label="import")
            logger.debug(
                f"Added {str(importing_module)} -> {str(to_node)} edge to graph"
            )

    def build_graph(self, dep_dict: Dict[Path, list[Path]]) -> None:
        logger.info("Starting building local dependencies graph")
        self._dep_dict = dep_dict
        self._nodes_from_keys()
        self._edges_from_dict()

    def print_nodes(self) -> None:
        for node, data in self._graph.nodes(data=True):
            print(f"{node} -> {data}")

    def print_edges(self) -> None:
        for u, v, data in self._graph.edges(data=True):
            print(f"{u} -> {v}, {data}")

    def get_graph(self) -> nx.DiGraph:
        return self._graph
