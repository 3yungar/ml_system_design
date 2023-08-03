# !/bin/bash

# Активация виртуального окружения
# source venv/bin/activate
# echo 'Virtual environment activate'

# Переход в директорию с расчетом базового уровня потребления
cd genesis_arena/baseline

# Запуск скрипта с расчетом и вставкой базового уровня потребления
python3 insert_baseline_today.py
echo 'Data is inserted'

# Деактвация виртулаьного окружения
# deactivate
# echo 'Virtual environment deactivate'

# Возврат в корень рабочей директории
cd ../..
