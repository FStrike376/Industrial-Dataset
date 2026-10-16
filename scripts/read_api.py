"""
Сбор датасета почасовой погоды через Open-Meteo API.

Источник: https://open-meteo.com/
Эндпоинт: https://api.open-meteo.com/v1/forecast
Лицензия данных: CC BY 4.0 (attribution required).
API-ключ не требуется, лимит ~10 000 запросов/сутки для non-commercial.

Что собираем:
    почасовую погоду в нескольких городах за последние N дней.

Результат:
    data/weather_hourly.parquet  (в .gitignore, в репо не попадает)
"""

from __future__ import annotations

import time
from pathlib import Path

import pandas as pd
import requests

# ----------------------------------------------------------------------
# Конфигурация
# ----------------------------------------------------------------------
API_URL = "https://api.open-meteo.com/v1/forecast"

# Города: название -> (широта, долгота)
CITIES: dict[str, tuple[float, float]] = {
    "Moscow":           (55.7558, 37.6173),
    "Saint Petersburg": (59.9311, 30.3609),
    "Berlin":           (52.5200, 13.4050),
    "Tokyo":            (35.6762, 139.6503),
    "New York":         (40.7128, -74.0060),
}

HOURLY_VARS = [
    "temperature_2m",
    "relative_humidity_2m",
    "wind_speed_10m",
    "precipitation",
    "surface_pressure",
    "is_day",
]

PAST_DAYS = 30
TIMEOUT = 20
RETRIES = 3
RETRY_PAUSE = 2.0

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)
OUT_PATH = DATA_DIR / "weather_hourly.parquet"


# ----------------------------------------------------------------------
# HTTP-слой
# ----------------------------------------------------------------------
def fetch_city(name: str, lat: float, lon: float) -> dict:
    """
    Один запрос к Open-Meteo для одного города.

    :param name: название города
    :param lat: широта
    :param lon: долгота
    :return: JSON-ответ как dict
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ",".join(HOURLY_VARS),
        "past_days": PAST_DAYS,
        "timezone": "auto",
    }

    last_exc: Exception | None = None
    for attempt in range(1, RETRIES + 1):
        try:
            r = requests.get(API_URL, params=params, timeout=TIMEOUT)
            r.raise_for_status()
            return r.json()
        except Exception as e:  # noqa: BLE001
            last_exc = e
            if attempt == RETRIES:
                break
            print(f"  [{name}] попытка {attempt} не удалась: {e}")
            time.sleep(RETRY_PAUSE)

    raise RuntimeError(f"Не удалось получить данные для {name}: {last_exc}")


# ----------------------------------------------------------------------
# Сборка датафрейма
# ----------------------------------------------------------------------
def build_dataframe() -> pd.DataFrame:
    """Обходит все города и возвращает объединённый DataFrame."""
    frames: list[pd.DataFrame] = []

    for city, (lat, lon) in CITIES.items():
        print(f"→ {city} ({lat}, {lon})")
        payload = fetch_city(city, lat, lon)

        hourly = payload.get("hourly")
        if not hourly:
            print(f"  [!] нет данных hourly для {city}, пропускаем")
            continue

        df_city = pd.DataFrame(hourly)
        df_city["city"] = city
        df_city["latitude"] = lat
        df_city["longitude"] = lon

        frames.append(df_city)

    if not frames:
        raise SystemExit("Не удалось собрать ни одного города — API вернул пусто.")

    return pd.concat(frames, ignore_index=True)


# ----------------------------------------------------------------------
# Приведение типов
# ----------------------------------------------------------------------
def cast_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Приводит столбцы к корректным типам:
    - time → datetime64[ns]
    - city → category
    - координаты и физические величины → float32
    - humidity → Int8 (nullable)
    - is_day → int8 (бинарный флаг)
    """
    df = df.copy()

    df["time"] = pd.to_datetime(df["time"], errors="coerce")
    df["city"] = df["city"].astype("category")

    float_cols = [
        "latitude", "longitude",
        "temperature_2m", "wind_speed_10m",
        "precipitation", "surface_pressure",
    ]
    for col in float_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("float32")

    if "relative_humidity_2m" in df.columns:
        df["relative_humidity_2m"] = (
            pd.to_numeric(df["relative_humidity_2m"], errors="coerce")
            .astype("Int8")
        )

    if "is_day" in df.columns:
        df["is_day"] = (
            pd.to_numeric(df["is_day"], errors="coerce")
            .fillna(0)
            .astype("int8")
        )

    ordered = [
        "time", "city", "latitude", "longitude",
        "temperature_2m", "relative_humidity_2m",
        "wind_speed_10m", "precipitation",
        "surface_pressure", "is_day",
    ]
    return df[[c for c in ordered if c in df.columns]]


# ----------------------------------------------------------------------
# main
# ----------------------------------------------------------------------
def main() -> None:
    print(f"Open-Meteo: почасовая погода за последние {PAST_DAYS} дней\n")

    df = cast_types(build_dataframe())

    print("\nСобрано:", df.shape)
    print(df.dtypes)

    df.to_parquet(OUT_PATH, index=False, engine="pyarrow")
    print(f"\nParquet сохранён: {OUT_PATH}")

    summary = (
        df.groupby("city", observed=True)
        .agg(
            rows=("time", "size"),
            t_min=("temperature_2m", "min"),
            t_max=("temperature_2m", "max"),
            wind_mean=("wind_speed_10m", "mean"),
        )
        .round(2)
    )
    print("\nСводка по городам:")
    print(summary)

    print("\nПервые 10 строк:")
    print(df.head(10).to_string(index=False))


if __name__ == "__main__":
    main()