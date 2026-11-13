import pandas as pd


REQUIRED_COLUMNS = {
    "timestamp",
    "machine_id",
    "machine_type",
    "vibration_rms",
    "temperature_motor",
    "current_phase_avg",
    "pressure_level",
    "rpm",
    "operating_mode",
    "hours_since_maintenance",
    "ambient_temp",
    "rul_hours",
    "failure_within_24h",
    "failure_type",
    "estimated_repair_cost",
}


def validate(df: pd.DataFrame) -> None:
    """Validate transformed dataset."""

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

    if not df["failure_within_24h"].isin([0, 1]).all():
        raise ValueError("Целевая переменная должна содержать 0 или 1.")

    print("Валидация пройдена успешно.")