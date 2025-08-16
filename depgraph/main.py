from pprint import pprint

from .logging_setup import setup_logger
from .analyzer.python_analyzer import PythonImportsAnalyzer
from . import test_code_strings

logger = setup_logger()

def main():
    logger.info('APPLICATION START')

    analyzer = PythonImportsAnalyzer()

    analyzer.analyze(test_code_strings.PYTHON_IMPORT)
    analyzer.analyze(test_code_strings.PYTHON_IMPORT_FROM)

    pprint(analyzer.get_results())

if __name__=='__main__':
    main()