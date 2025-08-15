import ast
import os
from pathlib import Path
from pprint import pprint

from ..utils import scan_python_modules


class PythonFileAnalyzer:
    def __init__(self, root_dir: Path):
        self.results = []
        self.root_dir = root_dir
        self.scanner = ModuleScanner(root_dir)
        

    def _read_file(self, path: Path):
        with open(path, 'r') as f:
            return f.read()

    def get_imports(self, path: Path):
        code = self._read_file(path)
        imports = self.get_all_imported_names(code)

        resolved_imports = self.scanner.resolve_imports(imports, path)
    
        self.results.append((path,resolved_imports))
        
    def get_all_imported_names(self,code):
        """
        Возвращает список всех импортируемых имен с полным путём.
        Относительные импорты сохраняются с точками:
        from . import mymodule      -> .mymodule
        from ..subpackage import f   -> ..subpackage.f
        """
        tree = ast.parse(code)
        imported_names = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    # обычный import module
                    imported_names.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                dots = '.' * node.level  # количество точек для относительного импорта
                for alias in node.names:
                    if node.module:
                        full_name = f"{dots}{node.module}.{alias.name}"
                    else:
                        full_name = f"{dots}{alias.name}"
                    imported_names.add(full_name)

        return list(imported_names)

from pathlib import Path

class ModuleScanner:
    def __init__(self, root_dir: Path):
        """
        root_dir: корневая директория проекта (Path)
        modules: словарь {имя модуля: путь к файлу}
        """
        self.root_dir = root_dir.resolve()
        self.modules = scan_python_modules(self.root_dir)


    def resolve_imports(self, imports_list, file_path: Path):
        """
        imports_list: список импортов из файла (как get_all_imported_names)
        file_path: Path к файлу, где были сделаны импорты
        
        Возвращает список кортежей:
        [(имя_модуля_строка, Path_к_файлу_модуля), ...]
        """
        resolved = set()
        file_path = file_path.resolve()
        file_dir = file_path.parent
        file_rel_path = file_dir.relative_to(self.root_dir)
        current_package = ".".join(file_rel_path.parts) if file_rel_path.parts else ""

        for imp in imports_list:
            full_name = None
            # Относительный импорт
            if imp.startswith("."):
                dots = 0
                while dots < len(imp) and imp[dots] == ".":
                    dots += 1
                remainder = imp[dots:]

                package_parts = current_package.split(".") if current_package else []
                base_parts = package_parts[:-dots] if dots <= len(package_parts) else []

                full_parts = base_parts + remainder.split(".") if remainder else base_parts
                full_name = ".".join(full_parts) if full_parts else None
            else:
                # Абсолютный импорт
                full_name = imp

            if full_name:
                parts = full_name.split(".")
                for i in range(len(parts), 0, -1):
                    candidate = ".".join(parts[:i])
                    if candidate in self.modules:
                        resolved.add((candidate, self.modules[candidate]))
                        break

        return list(resolved)

