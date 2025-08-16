from pathlib import Path

from . import test_strings
from .logging_setup import setup_logger
from .progress_bars import run_with_progress

logger = setup_logger()


def main() -> None:
    logger.info("APPLICATION START")

    pass


def test_func() -> None:
    logger.info("START TEST FUNCTION")

    PATH = Path(test_strings.TEST_PATH_SKLEARN).resolve()

    run_with_progress(PATH)

    pass


if __name__ == "__main__":
    test_func()
