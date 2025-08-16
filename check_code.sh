#!/bin/bash
set -e

echo "🔹 1. Форматирование кода с Black"
poetry run black .

echo "🔹 2. Линтинг и автоисправление с Ruff"
poetry run ruff check . --fix

echo "🔹 3. Проверка типов с Mypy"
poetry run mypy .

echo "✅ Проверка и автоисправление завершены"
