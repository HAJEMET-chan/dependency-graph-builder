import ast
from typing import Any, Optional
from copy import deepcopy

from ..utils import (
    _validate_structure
)

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

    def visit_Import(self, node: ast.Import):
        super().visit_Import(node)


        names = []

        for import_name in node.names:
            names.append(import_name.name)

    def visit_ImportFrom(self, node):
        super().visit_ImportFrom(node)

        for import_name in node.names:
            entry = self.get_entry_template()
            entry['module'] = node.module
            entry['level'] = node.level
            entry['name'] = import_name.name
            entry['asname'] = import_name.asname

            self._add_to_results(entry)



    def _add_to_results(self, res: Any):
        _validate_structure(res,self._entry_tempate_types)
        self._results.append(res)

    def get_entry_template(self):
        return deepcopy(self._entry_tempate)