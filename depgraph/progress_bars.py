from pathlib import Path
from tqdm import tqdm
from .dep_finding.python_dep_finder import PythonDepFinder  # твой класс с колбэками

def run_with_progress(dir_path: str):
    dir_path = Path(dir_path)

    # Получаем количество модулей для главного прогресса
    temp_finder = PythonDepFinder(dir_path)
    total_modules = len(temp_finder._dep_dict)

    # Создаем главный прогресс-бар по модулям
    with tqdm(total=total_modules,
              desc="Парсинг модулей",
              bar_format="{l_bar}{bar} | {n_fmt}/{total_fmt} [{percentage:.1f}%]") as modules_bar:

        # Функция для обновления прогресса по импортам
        def import_progress_generator(total_imports):
            return tqdm(total=total_imports,
                        desc="Резолвинг импортов",
                        leave=False,
                        bar_format="{l_bar}{bar} | {n_fmt}/{total_fmt} [{percentage:.1f}%]")

        # Колбэк для обновления прогресса модулей
        def module_cb(_):
            modules_bar.update(1)

        # Колбэк для прогресса импортов (будет динамически меняться)
        current_import_bar = None
        def import_cb(step=1):
            if current_import_bar:
                current_import_bar.update(step)

        # Создаем finder с колбэками
        finder = PythonDepFinder(
            dir_path,
            module_progress_callback=module_cb,
            import_progress_callback=import_cb
        )

        # Оборачиваем _analyze_module_deps, чтобы отслеживать прогресс импортов
        for module in finder._dep_dict.keys():
            deps = finder._analyser.analyze(module) or []
            total_imports = len(finder._analyser.get_results())

            # Создаем прогресс-бар по импортам текущего модуля
            current_import_bar = import_progress_generator(total_imports)

            # Стартуем анализ и резолвинг
            finder._analyze_module_deps(module)

            current_import_bar.close()
            current_import_bar = None

    return finder.get_dep_dict()


if __name__ == "__main__":
    deps = run_with_progress("path/to/your/project")
    print("Готово! Зависимости собраны.")
