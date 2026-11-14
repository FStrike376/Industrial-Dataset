import logging

import pandas as pd


logger = logging.getLogger(__name__)

SENSOR_COLUMNS = [
    "vibration_rms",
    "temperature_motor",
    "current_phase_avg",
    "pressure_level",
    "rpm",
]

NON_NULL_COLUMNS = [
    "timestamp",
    "machine_id",
    "machine_type",
    "operating_mode",
    "hours_since_maintenance",
    "ambient_temp",
    "rul_hours",
    "failure_within_24h",
    "failure_type",
    "estimated_repair_cost",
]

FLOAT_COLUMNS = SENSOR_COLUMNS + [
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
MAX_SENSOR_MISSING_RATIO = 0.20


def validate(df: pd.DataFrame) -> None:
    """Validate transformed dataset against schema and business rules."""

    missing_columns = REQUIRED_COLUMNS - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Отсутствуют обязательные столбцы: {missing_columns}"
        )

    if df.empty:
        raise ValueError("Датасет пустой.")

    # Служебные и целевые колонки не должны содержать пропусков (NaN/NaT)
    for col in NON_NULL_COLUMNS:
        if df[col].isna().any():
            raise ValueError(
                f"Обнаружены недопустимые пропуски или некорректные значения в столбце '{col}'."
            )

    # В сенсорных колонках допустима небольшая доля пропусков (потеря пакетов IoT до 20%)
    for col in SENSOR_COLUMNS:
        missing_ratio = df[col].isna().mean()
        if missing_ratio > MAX_SENSOR_MISSING_RATIO:
            raise ValueError(
                f"Доля пропусков в сенсоре '{col}' ({missing_ratio:.1%}) превышает порог {MAX_SENSOR_MISSING_RATIO:.0%}."
            )

    if not df[TARGET_COLUMN].isin([0, 1]).all():
        raise ValueError("Целевая переменная должна содержать только 0 или 1.")

    if (df["rul_hours"] < 0).any():
        raise ValueError("Обнаружены отрицательные значения остаточного ресурса (rul_hours < 0).")

    if (df["estimated_repair_cost"] < 0).any():
        raise ValueError("Обнаружена отрицательная стоимость ремонта (estimated_repair_cost < 0).")

    if (df["hours_since_maintenance"] < 0).any():
        raise ValueError("Обнаружены отрицательные значения hours_since_maintenance.")

    # Для rpm проверяем только непустые значения (так как rpm — сенсор с допустимыми пропусками ~2.2%)
    rpm_valid = df["rpm"].dropna()
    if ((rpm_valid < 0) | (rpm_valid > MAX_RPM)).any():
        raise ValueError(f"Значения оборотов (rpm) выходят за допустимые пределы [0, {MAX_RPM}].")

    logger.info("Валидация пройдена успешно.")
