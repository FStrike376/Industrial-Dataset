# Industrial-Dataset

Синтетический набор данных для промышленного интернета вещей с 24 042 записями о станках с ЧПУ и сопутствующем оборудовании, предназначенный для предиктивного обслуживания, прогнозирования отказов и оценки остаточного срока службы в производственных условиях.

**Источник:** [Kaggle — Industrial Machine Predictive Maintenance](https://www.kaggle.com/datasets/tatheerabbas/industrial-machine-predictive-maintenance)

**Размер файла:** 2.1 МБ

[Скачать датасет (Яндекс.Диск)](https://disk.yandex.ru/d/Uk1Lt-CmOnijEw)

## Описание признаков

- `timestamp` — временная метка
- `machine_id` — идентификатор станка
- `machine_type` — тип оборудования (CNC, Pump, Compressor)
- `vibration_rms` — среднеквадратичная вибрация
- `temperature_motor` — температура двигателя
- `current_phase_avg` — средний ток фазы
- `pressure_level` — уровень давления
- `rpm` — обороты в минуту
- `operating_mode` — режим работы (idle, normal, peak)
- `hours_since_maintenance` — часы с последнего обслуживания
- `ambient_temp` — температура окружающей среды
- `rul_hours` — остаточный ресурс в часах
- `failure_within_24h` — отказ в течение 24 часов (0/1)
- `failure_type` — тип отказа (none, hydraulic, bearing, electrical, motor_overheat)
- `estimated_repair_cost` — оценка стоимости ремонта

## Структура проекта

```text
Industrial-Dataset/
├── data/
│   └── raw/                  # Локальное хранилище сырого датасета (исключено из Git)
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   └── EDA.ipynb             # Исследовательский анализ данных и визуализация Plotly
├── scripts/
│   ├── read_api.py           # Сбор почасовой погоды через Open-Meteo API
│   └── write_to_db.py        # Скрипт загрузки данных в PostgreSQL (Homework 7)
├── src/
│   └── etl/                  # Самодостаточный пакет ETL-пайплайна (Homework 8)
│       ├── __init__.py
│       ├── extract.py
│       ├── transform.py
│       ├── validate.py
│       ├── load.py
│       └── main.py
├── data_loader.py            # Скрипт первичной загрузки и сохранения в Parquet
├── pyproject.toml            # Конфигурация пакета и разделение зависимостей (etl / dev)
├── requirements.txt          # Основные зависимости для запуска ETL и скриптов
└── README.md                 # Документация проекта
```

## Установка и запуск

1. Клонируйте репозиторий:

   ```bash
   git clone https://github.com/FStrike376/Industrial-Dataset.git
   cd Industrial-Dataset
   ```

2. Создайте виртуальное окружение:

   ```bash
   python -m venv .venv
   ```

3. Активируйте окружение.

   **Windows (PowerShell):**

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   **Windows (cmd):**

   ```cmd
   .venv\Scripts\activate.bat
   ```

   **Linux/macOS:**

   ```bash
   source .venv/bin/activate
   ```

4. Установите зависимости и сам пакет проекта:

   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

   Для работы с исследовательскими ноутбуками (`notebooks/EDA.ipynb`) и библиотеками визуализации (`plotly`, `kaleido`, `seaborn`, `matplotlib`, `jupyter`) установите пакет вместе с `dev`-блоком:

   ```bash
   pip install -e ".[dev]"
   ```

5. Загрузите датасет и запустите скрипт загрузчика:

   ```bash
   python data_loader.py
   ```

## Анализ данных

Основной анализ находится в ноутбуке `notebooks/EDA.ipynb`. В нём представлены восемь разделов исходного EDA и дополнительный раздел 9 «Продвинутая визуализация (Plotly)».

В ноутбуке по умолчанию установлен статический рендерер `"png"` (в первой ячейке с импортами: `pio.renderers.default = "png"`), что требует установленного пакета Kaleido и совместимого браузера Chrome/Chromium. Для интерактивного просмотра графиков поменяйте значение `pio.renderers.default` в ячейке с импортами на `"plotly_mimetype"` (для Jupyter/VS Code) или `"browser"` (для открытия в отдельной вкладке браузера):

```python
import plotly.io as pio
pio.renderers.default = "plotly_mimetype"  # или "browser"
```

## Работа с удалённой базой данных (Homework 7)

### Описание

Реализована загрузка 100 строк датасета Industrial Machine Predictive Maintenance в удалённую базу данных PostgreSQL с использованием встроенных возможностей `pandas` (`df.to_sql` и `pd.read_sql_table`) и `SQLAlchemy`.

### Настройка доступа

Для подключения используются два локальных файла:

- `creds.db` — SQLite-база с учётными данными;
- `.env` — файл с параметрами подключения к PostgreSQL.

Оба файла должны находиться в корне проекта и исключаться из Git через `.gitignore`. Не публикуйте их в репозитории.

### Запись данных

Для загрузки данных используется скрипт:

```bash
python scripts/write_to_db.py
```

Скрипт:

1. Загружает полный датасет с помощью `data_loader.py`.
2. Выбирает первые 100 строк.
3. Пересоздаёт и заполняет таблицу `akhmetkhanovar` в базе `homeworks` через `df.to_sql(..., if_exists="replace")`.
4. Проверяет количество записанных строк чтением таблицы через `pd.read_sql_table`.

### Результат

В удалённую базу данных PostgreSQL успешно загружено 100 строк с 15 столбцами в таблицу `akhmetkhanovar`.

## Домашнее задание №8 — ETL-процесс

Для организации процесса ETL создан отдельный самодостаточный Python-пакет `etl` в директории `src`.

Структура пакета:

```text
src/
└── etl/
    ├── __init__.py
    ├── extract.py
    ├── transform.py
    ├── validate.py
    ├── load.py
    └── main.py
```

Пакет реализует полный цикл ETL:

1. **Extract** — безопасное скачивание исходного датасета через временный `.part`-файл и чтение CSV.
2. **Transform** — приведение типов данных, очистка пропусков целевой переменной и подготовка таблицы.
3. **Validate** — проверка схемы, отсутствия пустых ключей и соблюдения бизнес-правил (`rul_hours >= 0`, `estimated_repair_cost >= 0`, `0 <= rpm <= 100000`).
4. **Load** — пакетная загрузка подготовленных данных в PostgreSQL с помощью `pandas.to_sql` и `SQLAlchemy`.

### Назначение модулей

- `extract.py` — отвечает за скачивание с Яндекс.Диска и чтение исходного датасета.
- `transform.py` — выполняет приведение типов и очистку данных.
- `validate.py` — хранит единые константы схемы и проверяет корректность и полноту данных.
- `load.py` — отвечает за загрузку данных в PostgreSQL через `SQLAlchemy` и `pandas.to_sql`.
- `main.py` — объединяет все этапы ETL, настраивает логирование и предоставляет интерфейс командной строки (`argparse`).
- `__init__.py` — инициализирует пакет Python.

### Настройка подключения к базе данных

Для работы ETL необходимо создать файл `.env` в корне проекта и указать параметры подключения:

```env
HOMEWORK_HOST=your_host
HOMEWORK_PORT=5432
HOMEWORK_USER=your_user
HOMEWORK_PASSWORD=your_password
HOMEWORK_DB=your_database
```

Не добавляйте файл `.env` в Git.

### Установка зависимостей и запуск ETL

Перед запуском ETL перейдите в корневую директорию проекта.

1. Создайте и активируйте виртуальное окружение:

   **Windows (PowerShell):**

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   **Linux / macOS:**

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Установите зависимости и пакет `etl` в editable-режиме:

   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

   Команда `pip install -e .` регистрирует директорию `src/` в виртуальном окружении, благодаря чему Python находит пакет `etl`.

3. Запустите ETL-процесс:

   ```bash
   python -m etl.main --limit 100
   ```

   *(Альтернативный вариант запуска напрямую по пути к скрипту: `python src/etl/main.py --limit 100`)*

Доступные аргументы:

- `--source` — путь к локальному CSV-файлу;
- `--limit` — максимальное количество строк для загрузки (от 1 до 100, по умолчанию `100`);
- `--table` — название таблицы PostgreSQL (по умолчанию `akhmetkhanovar`).

Пример запуска с дополнительными параметрами:

```bash
python -m etl.main --source data/raw/predictive_maintenance_v3.csv --limit 100 --table akhmetkhanovar
```

В результате выполнения ETL-процесса данные извлекаются, преобразуются, проходят валидацию и загружаются в PostgreSQL (с ограничением в 100 строк).
