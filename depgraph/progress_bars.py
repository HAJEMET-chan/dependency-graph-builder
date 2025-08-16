from pathlib import Path
from typing import Dict

from tqdm import tqdm

from .dep_finding.python_dep_finder import PythonDepFinder  # импортируем твой класс


def run_with_progress(dir_path: Path) -> Dict:
    finder = PythonDepFinder(dir_path)
    modules = list(finder._dep_dict.keys())

    # Главный прогресс-бар по модулям
    with tqdm(total=len(modules), desc="Парсинг модулей") as modules_bar:

        for module in modules:
            # Получаем все импорты для текущего модуля
            finder._analyser.analyze(module)
            deps = finder._analyser.get_results()
            finder._analyser.clear_results()

            # Вложенный прогресс-бар по импортам модуля
            with tqdm(
                total=len(deps), desc=f"Резолвинг {module.name}", leave=False
            ) as imports_bar:
                for dep in deps:
                    finder._resolve_import_path(dep, module)
                    imports_bar.update(1)

            modules_bar.update(1)

    return finder.get_dep_dict()
