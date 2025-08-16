from pathlib import Path

from . import test_strings
from .dep_finding.python_dep_finder import PythonDepFinder
from .graph_building.graph_creator import GraphCreator
from .logging_setup import setup_logger
from .utils import visualize_graph

logger = setup_logger()


def main() -> None:
    logger.info("APPLICATION START")

    pass


def test_func() -> None:
    logger.info("START TEST FUNCTION")

    PATH = Path(test_strings.TEST_PATH_DEPGRAPH).resolve()

    dep_finder = PythonDepFinder(PATH)
    graph_creator = GraphCreator()


    dep_finder.start_dep_finding()
    graph_creator.build_graph(dep_finder.get_dep_dict())

    visualize_graph(graph_creator.get_graph())

    print("end")
    pass


if __name__ == "__main__":
    test_func()
