"""
Загрузчик датасета predictive_maintenance_v3.

Функции:
- download_file  — скачивает CSV с Яндекс.Диска по публичной ссылке
- load_data      — читает CSV в pandas.DataFrame
- cast_types     — приводит типы столбцов к корректным
- save_parquet   — сохраняет DataFrame в parquet
"""

from pathlib import Path

import pandas as pd
import requests

# Публичная ссылка на файл (Яндекс.Диск)
YANDEX_DISK_URL = "https://disk.yandex.ru/d/Uk1Lt-CmOnijEw"

# Таймаут для сетевых запросов (секунды)
REQUEST_TIMEOUT = 30

# Пути считаем относительно самого файла data_loader.py
BASE_DIR = Path(__file__).resolve().parent
LOCAL_FILE_NAME = BASE_DIR / "predictive_maintenance_v3.csv"
PARQUET_FILE_NAME = BASE_DIR / "predictive_maintenance_v3.parquet"


def download_file(url: str, dest_path: Path) -> None:
    """
    Скачивает файл с Яндекс.Диска по публичной ссылке.

    :param url: публичная ссылка на файл
    :param dest_path: путь, куда сохранить файл
    """
    api_url = "https://cloud-api.yandex.net/v1/disk/public/resources/download"
    params = {"public_key": url}
    response = requests.get(api_url, params=params, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    download_url = response.json()["href"]

    print(f"Скачиваем файл с {url}...")
    with requests.get(download_url, stream=True, timeout=REQUEST_TIMEOUT) as r:
        r.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print(f"Файл сохранён: {dest_path}")


def load_data(file_path: Path) -> pd.DataFrame:
    """
    Загружает датасет из CSV-файла и возвращает DataFrame.

    :param file_path: путь к CSV
    :return: pandas.DataFrame
    """
    return pd.read_csv(file_path)


def cast_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Приводит типы столбцов датасета predictive_maintenance к корректным.

    :param df: исходный DataFrame
    :return: DataFrame с правильными типами
    """
    df = df.copy()

    # --- datetime ---
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    # --- числовые float ---
    float_cols = [
        "vibration_rms",
        "temperature_motor",
        "current_phase_avg",
        "pressure_level",
        "rpm",
        "hours_since_maintenance",
        "ambient_temp",
        "rul_hours",
    ]
    for col in float_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("float64")

    # --- целочисленные ---
    # nullable Int64 — устойчиво к возможным пропускам
    df["machine_id"] = pd.to_numeric(df["machine_id"], errors="coerce").astype("Int64")
    df["estimated_repair_cost"] = pd.to_numeric(
        df["estimated_repair_cost"], errors="coerce"
    ).astype("Int64")

    # --- целевая переменная ---
    # failure_within_24h — бинарный таргет (0/1).
    # Пропуски трактуем как 0
    df["failure_within_24h"] = (
        pd.to_numeric(df["failure_within_24h"], errors="coerce")
        .fillna(0)
        .astype("int8")
    )

    # --- категориальные ---
    cat_cols = ["machine_type", "operating_mode", "failure_type"]
    for col in cat_cols:
        df[col] = df[col].astype("category")

    return df


def save_parquet(df: pd.DataFrame, path: Path) -> None:
    """
    Сохраняет DataFrame в parquet без индекса.

    :param df: DataFrame
    :param path: путь к parquet-файлу
    """
    df.to_parquet(path, index=False, engine="pyarrow")
    print(f"Parquet сохранён: {path}")


def print_first_rows(df: pd.DataFrame, n_rows: int = 10) -> None:
    """
    Выводит первые n_rows строк датасета в консоль.
    """
    print(f"Первые {n_rows} строк датасета:")
    print(df.head(n_rows))


if __name__ == "__main__":
    # Скачиваем CSV, если его ещё нет
    if not LOCAL_FILE_NAME.exists():
        try:
            download_file(YANDEX_DISK_URL, LOCAL_FILE_NAME)
        except Exception as e:
            print(f"Не удалось скачать файл: {e}")
            raise SystemExit(1)

    try:
        df = load_data(LOCAL_FILE_NAME)
        df = cast_types(df)
        print_first_rows(df)
        print("\nТипы после приведения:")
        print(df.dtypes)

        save_parquet(df, PARQUET_FILE_NAME)
    except FileNotFoundError:
        print(f"Файл {LOCAL_FILE_NAME} не найден.")
        raise SystemExit(1)
    except pd.errors.ParserError:
        print("Ошибка при чтении CSV — файл повреждён.")
        raise SystemExit(1)