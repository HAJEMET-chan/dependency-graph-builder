import typer
from pathlib import Path

from .core import start_process
from .logger_setup import setup_logger

logger = setup_logger()

app = typer.Typer()

@app.command()
def start(local_path: str):
    
    path = Path(local_path)
    start_process(path)

if __name__ == '__main__':
    app()