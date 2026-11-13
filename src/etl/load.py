import os

import pandas as pd
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values


def get_postgres_type(dtype):
    """Convert pandas dtype to PostgreSQL type."""

    if pd.api.types.is_datetime64_any_dtype(dtype):
        return "TIMESTAMP"

    if pd.api.types.is_integer_dtype(dtype):
        return "BIGINT"

    if pd.api.types.is_float_dtype(dtype):
        return "DOUBLE PRECISION"

    return "TEXT"


def convert_value(value):
    """Convert pandas values to Python values."""

    if pd.isna(value):
        return None

    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime()

    if hasattr(value, "item"):
        return value.item()

    return value


def load(
    df: pd.DataFrame,
    table_name: str = "akhmetkhanovar",
) -> int:
    """Load transformed data into PostgreSQL."""

    if not table_name.replace("_", "").isalnum():
        raise ValueError("Некорректное имя таблицы.")

    connection = psycopg2.connect(
        host=os.getenv("HOMEWORK_HOST"),
        port=os.getenv("HOMEWORK_PORT"),
        user=os.getenv("HOMEWORK_USER"),
        password=os.getenv("HOMEWORK_PASSWORD"),
        dbname=os.getenv("HOMEWORK_DB"),
        connect_timeout=10,
    )

    try:
        with connection:
            with connection.cursor() as cursor:

                columns_sql = [
                    sql.SQL("{} {}").format(
                        sql.Identifier(str(column)),
                        sql.SQL(get_postgres_type(dtype)),
                    )
                    for column, dtype in df.dtypes.items()
                ]

                cursor.execute(
                    sql.SQL("DROP TABLE IF EXISTS {}").format(
                        sql.Identifier(table_name)
                    )
                )

                cursor.execute(
                    sql.SQL("CREATE TABLE {} ({})").format(
                        sql.Identifier(table_name),
                        sql.SQL(", ").join(columns_sql),
                    )
                )

                rows = [
                    tuple(convert_value(value) for value in row)
                    for row in df.itertuples(
                        index=False,
                        name=None,
                    )
                ]

                insert_query = sql.SQL(
                    "INSERT INTO {} ({}) VALUES %s"
                ).format(
                    sql.Identifier(table_name),
                    sql.SQL(", ").join(
                        sql.Identifier(str(column))
                        for column in df.columns
                    ),
                )

                execute_values(
                    cursor,
                    insert_query.as_string(connection),
                    rows,
                    page_size=100,
                )

                cursor.execute(
                    sql.SQL("SELECT COUNT(*) FROM {}").format(
                        sql.Identifier(table_name)
                    )
                )

                count = cursor.fetchone()[0]

        print(f"Загружено строк: {count}")

        return count

    finally:
        connection.close()