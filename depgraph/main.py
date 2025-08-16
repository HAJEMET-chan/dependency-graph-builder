from pprint import pprint
from pathlib import Path

from .logging_setup import setup_logger
from .analyzing.python_analyzer import PythonImportsAnalyzer
from .dep_finding.python_dep_finder import PythonDepFinder
from . import test_strings
from .utils import _find_all_python_modules

logger = setup_logger()

def main():
    logger.info('APPLICATION START')

    pass

def test_func():
    logger.info('START TEST FUNCTION')

    PATH = Path(test_strings.TEST_PATH_DEPGRAPH).resolve()

    dep_finder = PythonDepFinder(PATH)

    dep_finder.start_dep_finding()

    dep_dict = dep_finder.get_dep_dict()

    pass


if __name__=='__main__':
    test_func()