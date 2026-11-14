import logging

import pandas as pd


logger = logging.getLogger(__name__)

FLOAT_COLUMNS = [
    "vibration_rms",
    "temperature_motor",
    "current_phase_avg",
    "pressure_level",
    "rpm",
    "hours_since_maintenance",
    "ambient_temp",
    "rul_hours",
]

INTEGER_COLUMNS = [
    "machine_id",
    "estimated_repair_cost",
]

CATEGORY_COLUMNS = [
    "machine_type",
    "operating_mode",
    "failure_type",
]

TARGET_COLUMN = "failure_within_24h"

REQUIRED_COLUMNS = set(
    ["timestamp", TARGET_COLUMN]
    + FLOAT_COLUMNS
    + INTEGER_COLUMNS
    + CATEGORY_COLUMNS
)

MAX_RPM = 100_000


def validate(df: pd.DataFrame) -> None:
    """Validate transformed dataset against schema and business rules."""

    missing_columns = REQUIRED_COLUMNS - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Отсутствуют обязательные столбцы: {missing_columns}"
        )

    if df.empty:
        raise ValueError("Датасет пустой.")

    if df["timestamp"].isna().any():
        raise ValueError("Обнаружены некорректные даты.")

    if df["machine_id"].isna().any():
        raise ValueError("Обнаружены пустые идентификаторы станков.")

    if df[TARGET_COLUMN].isna().any():
        raise ValueError("Обнаружены пропуски в целевой переменной failure_within_24h.")

    if not df[TARGET_COLUMN].isin([0, 1]).all():
        raise ValueError("Целевая переменная должна содержать 0 или 1.")

    if (df["rul_hours"].dropna() < 0).any():
        raise ValueError("Обнаружены отрицательные значения остаточного ресурса (rul_hours < 0).")

    if (df["estimated_repair_cost"].dropna() < 0).any():
        raise ValueError("Обнаружена отрицательная стоимость ремонта (estimated_repair_cost < 0).")

    rpm_series = df["rpm"].dropna()
    if ((rpm_series < 0) | (rpm_series > MAX_RPM)).any():
        raise ValueError(f"Значения оборотов (rpm) выходят за допустимые пределы [0, {MAX_RPM}].")

    logger.info("Валидация пройдена успешно.")
