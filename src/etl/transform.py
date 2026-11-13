import pandas as pd


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and transform the source dataset."""

    df = df.copy()

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce",
    )

    float_columns = [
        "vibration_rms",
        "temperature_motor",
        "current_phase_avg",
        "pressure_level",
        "rpm",
        "hours_since_maintenance",
        "ambient_temp",
        "rul_hours",
    ]

    for column in float_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    integer_columns = [
        "machine_id",
        "estimated_repair_cost",
    ]

    for column in integer_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        ).astype("Int64")

    df["failure_within_24h"] = (
        pd.to_numeric(
            df["failure_within_24h"],
            errors="coerce",
        )
        .fillna(0)
        .astype("int8")
    )

    category_columns = [
        "machine_type",
        "operating_mode",
        "failure_type",
    ]

    for column in category_columns:
        df[column] = df[column].astype("category")

    return df