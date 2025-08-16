import ast
from typing import Any, Optional, Dict
from pprint import pprint
from copy import deepcopy
import logging

from ..utils import (
    _validate_structure
)

__all__=['PythonImportsAnalyzer']
logger = logging.getLogger(__name__)

class PythonImportsAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self._results = []

        self._entry_tempate = {
            'module': None,
            'name': None,
            'asname': None,
            'level': None
        }

        self._entry_tempate_types = {
            'module': Optional[str],
            'name': str,
            'asname': Optional[str],
            'level': int
        }
    
    def analyze(self, code: str):

        logger.info('starting analyzing Python import')

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
        return self._results
    
