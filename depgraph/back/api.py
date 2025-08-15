from pathlib import Path

from .core import start_process
from .logger_setup import setup_logger

logger = setup_logger()

def generate_graph(local_path: str):

    path = Path(local_path)
    return start_process(path)