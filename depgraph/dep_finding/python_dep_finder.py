from pathlib import Path
from typing import List, Dict, Set
import logging

from ..utils import _find_all_python_modules, _find_package_roots
from ..analyzing.python_analyzer import PythonImportsAnalyzer

logger = logging.getLogger(__name__)

class PythonDepFinder:

    def __init__(self, dir_path: Path):
        self._dir_path: Path = dir_path
        self._package_roots = _find_package_roots(dir_path)
        self._dep_dict: Dict[Path: List] = self._to_dep_dict(_find_all_python_modules(dir_path))
        self._modules: Set[Path] = self._dep_dict.keys()
        self._analyser = PythonImportsAnalyzer(dir_path)


    def _to_dep_dict(self, modules: List) -> Dict[Path, List]:
        dep_dict = {}

        for module in modules:
            dep_dict[module] = []

        return dep_dict
    
    def start_dep_finding(self):

        for importing_module in self._dep_dict.keys():
            logger.debug(f'starting analyzing imports in {str(importing_module)}')
            self._analyze_module_deps(importing_module)

    def _analyze_module_deps(self, importing_module: Path):

        self._analyser.analyze(importing_module)

        deps = self._analyser.get_results()
        self._analyser.clear_results()
        self._resolve_imports(deps, importing_module)

    def _resolve_imports(self, deps: List, importing_module: Path):

        for module_import in deps:
            self._resolve_import_path(module_import, importing_module)

    def _resolve_import_path(self, module_import: Dict, importing_module: Path):
        """
        Разрешает путь импортируемого модуля внутри проекта и добавляет его в dep_dict.
        Внешние зависимости (stdlib, сторонние пакеты) игнорируются.
        """
        level = module_import.get("level", 0)
        module = module_import.get("module")
        name = module_import.get("name")

        resolved_path = None

        if level == 0:
            for root in self._package_roots:
                if module:
                    parts = module.split(".")
                    # если первый элемент модуля совпадает с именем рутового пакета, убираем его
                    if parts[0] == root.name:
                        parts = parts[1:]
                    candidate = root / Path("/".join(parts))
                else:
                    candidate = root / Path(name.replace(".", "/"))

                # Приводим к относительному пути относительно self._dir_path
                candidate_py = candidate.with_suffix(".py")
                candidate_init = candidate / "__init__.py"

                try:
                    candidate_py_rel = candidate_py.relative_to(self._dir_path)
                except ValueError:
                    candidate_py_rel = candidate_py

                try:
                    candidate_init_rel = candidate_init.relative_to(self._dir_path)
                except ValueError:
                    candidate_init_rel = candidate_init

                if candidate_py_rel in self._modules:
                    resolved_path = candidate_py_rel
                    break
                elif candidate_init_rel in self._modules:
                    resolved_path = candidate_init_rel
                    break

        else:
            base = importing_module.parent
            for _ in range(level - 1):
                base = base.parent

            if module:
                candidate = base / Path(module.replace(".", "/"))
            else:
                candidate = base / Path(name.replace(".", "/"))

            candidate_py = candidate.with_suffix(".py")
            candidate_init = candidate / "__init__.py"

            try:
                candidate_py_rel = candidate_py.relative_to(self._dir_path)
            except ValueError:
                candidate_py_rel = candidate_py

            try:
                candidate_init_rel = candidate_init.relative_to(self._dir_path)
            except ValueError:
                candidate_init_rel = candidate_init

            if candidate_py_rel in self._modules:
                resolved_path = candidate_py_rel
            elif candidate_init_rel in self._modules:
                resolved_path = candidate_init_rel

        if resolved_path:
            self._dep_dict[importing_module].append(resolved_path)
            logger.debug(f"Resolved import {module_import} in {importing_module} -> {resolved_path}")
        else:
            logger.debug(f"Could not resolve import {module_import} in {importing_module}")




    def get_dep_dict(self):
        return self._dep_dict