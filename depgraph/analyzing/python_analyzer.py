import ast
from typing import Any, Optional, Dict, List
from pprint import pprint
from copy import deepcopy
import logging
from pathlib import Path

from ..utils import (
    _validate_structure
)

__all__=['PythonImportsAnalyzer']
logger = logging.getLogger(__name__)

class PythonImportsAnalyzer(ast.NodeVisitor):
    def __init__(self, root_folder: Path):
        self._results: List = []
        self._root_folder = root_folder

        self._entry_tempate: Dict = {
            'module': None,
            'name': None,
            'asname': None,
            'level': None
        }

        self._entry_tempate_types: Dict = {
            'module': Optional[str],
            'name': str,
            'asname': Optional[str],
            'level': int
        }

    def analyze(self, file_path: Path):

        code = self._read_file(file_path)
        self.visit(ast.parse(code))

    def visit_Import(self, node: ast.Import):
        
        logger.debug('found an ast.Import node')

        for import_name in node.names:
            module, name = (import_name.name.rsplit('.', 1) + [None])[:2]

            if name is None:
                module, name = None, module  

            entry = self.get_entry_template()
            entry.update({
                "module" : module,
                "level"  : 0,
                "name"   : name,
                "asname" : import_name.asname,
            })

            self._add_to_results(entry)

    def visit_ImportFrom(self, node: ast.ImportFrom):

        logger.debug('found an ast.ImportFrom node')

        for import_name in node.names:
            entry = self.get_entry_template()
            entry.update({
                'module' : node.module,
                'level'  : node.level,
                'name'   : import_name.name,
                'asname' : import_name.asname
            })

            self._add_to_results(entry)



    def _add_to_results(self, res: Dict):
        _validate_structure(res,self._entry_tempate_types)

        logger.debug((
            'founded import`s info'
            f'\nimport module: {res['module']}'
            f'\nimport name:   {res['name']}'
            f'\nimport asname: {res['asname']}'
            f'\nimport level:  {res['level']}'
        ))
        
        self._results.append(res)

    def get_entry_template(self):
        return deepcopy(self._entry_tempate)
    
    def get_results(self):
        return deepcopy(self._results)
    
    def _read_file(self, file_path: Path) -> Optional[str]:
        """
        Считывает содержимое Python-файла.

        Args:
            file_path (Path): относительный путь к Python-файлу 
                            (относительно self._root_folder).

        Returns:
            Optional[str]: содержимое файла или None, если файл не удалось прочитать.
        """
        full_path = self._root_folder / file_path

        if not full_path.exists():
            raise FileNotFoundError(f"Файл не найден: {full_path}")

        if not full_path.is_file():
            raise ValueError(f"Ожидался файл, но получен каталог: {full_path}")

        try:
            return full_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            raise UnicodeDecodeError(
                f"Не удалось декодировать файл {full_path} в кодировке utf-8"
            )
        except OSError as e:
            raise OSError(f"Ошибка при чтении файла {full_path}: {e}")

        
    def clear_results(self):
        self._results = []
    
