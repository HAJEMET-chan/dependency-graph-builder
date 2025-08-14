from pathlib import Path
from .file_utils import get_all_files_list
from .analyzer.python_analyzer import PythonFileAnalyzer
from pprint import pprint






def start_process(local_path: Path):

    if not local_path.exists():
        raise FileExistsError(f'path {local_path} does not exist')
    
    if not local_path.is_dir():
        raise FileExistsError(f'path {local_path} is not a directory')
    
    all_files = get_all_files_list(local_path)
    analyzer = PythonFileAnalyzer(local_path)

    for file in all_files:
        if file.suffix == '.py':
            analyzer.get_imports(file)

    