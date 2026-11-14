import pandas as pd

from etl.validate import (
    CATEGORY_COLUMNS,
    FLOAT_COLUMNS,
    INTEGER_COLUMNS,
    TARGET_COLUMN,
)


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and transform the source dataset."""

    df = df.copy()

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce",
    )

    for column in FLOAT_COLUMNS:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    for column in INTEGER_COLUMNS:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        ).astype("Int64")

    # Используем nullable Int8 без dropna/fillna, чтобы validate() явно проверил отсутствие пропусков в таргете
    df[TARGET_COLUMN] = pd.to_numeric(
        df[TARGET_COLUMN],
        errors="coerce",
    ).astype("Int8")

    for column in CATEGORY_COLUMNS:
        df[column] = df[column].astype("category")

    return df
