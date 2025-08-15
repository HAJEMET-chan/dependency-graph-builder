# depgraph/back/api.py

from pathlib import Path
from typing import Dict, Any

from .core import start_process
from .logger_setup import setup_logger
from .graph import GraphControl

# Модульный кэш для хранения уже сгенерированных графов.
# Ключ — это путь к проекту, значение — экземпляр GraphControl.
_graph_cache: Dict[Path, GraphControl] = {}

logger = setup_logger()

def generate_graph(local_path: str) -> Dict[str, Any]:
    """
    Генерирует граф зависимостей для указанного локального пути.
    
    Эта функция кэширует сгенерированный граф, чтобы избежать повторного
    трудоемкого анализа проекта при последующих вызовах с тем же путем.

    Args:
        local_path (str): Путь к анализируемой файловой системе.

    Returns:
        Dict[str, Any]: Словарь, содержащий данные графа в формате,
                        удобном для сериализации в JSON.
    """
    path = Path(local_path).resolve()
    
    # Проверка кэша.
    if path in _graph_cache:
        logger.info(f"Graph for '{path}' found in cache. Returning cached data.")
        graph_control = _graph_cache[path]
    else:
        logger.info(f"Generating new graph for '{path}'.")
        try:
            graph_control = start_process(path)
            # Сохранение сгенерированного графа в кэш.
            _graph_cache[path] = graph_control
            logger.info(f"Graph for '{path}' saved to cache.")
        except FileNotFoundError as e:
            logger.error(f"Error: {e}")
            return {"error": str(e)}

    # Преобразование графа в JSON-сериализуемый формат.
    return graph_control.to_json_serializable()

