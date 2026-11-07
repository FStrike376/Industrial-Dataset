import os
import sys
from pathlib import Path

import pandas as pd
import psycopg2
from dotenv import load_dotenv
from psycopg2 import sql
from psycopg2.extras import execute_values


# Пути проекта
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from data_loader import (
    load_data,
    cast_types,
    LOCAL_FILE_NAME,
    YANDEX_DISK_URL,
    download_file,
)

# Настройки
TABLE_NAME = "akhmetkhanovar"
ROWS_TO_UPLOAD = 100


def get_postgres_type(dtype):
    """Convert pandas data types to PostgreSQL types."""

    if pd.api.types.is_datetime64_any_dtype(dtype):
        return "TIMESTAMP"
    if pd.api.types.is_bool_dtype(dtype):
        return "BOOLEAN"
    if pd.api.types.is_integer_dtype(dtype):
        return "BIGINT"
    if pd.api.types.is_float_dtype(dtype):
        return "DOUBLE PRECISION"

    return "TEXT"


def convert_value(value):
    """Convert pandas and NumPy values to Python values."""

    if pd.isna(value):
        return None

    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime()

    if hasattr(value, "item"):
        return value.item()

    return value


def main():
    # Загружаем настройки из .env
    load_dotenv(BASE_DIR / ".env")

    required_vars = [
        "HOMEWORK_HOST",
        "HOMEWORK_PORT",
        "HOMEWORK_USER",
        "HOMEWORK_PASSWORD",
        "HOMEWORK_DB",
    ]

    missing = [var for var in required_vars if not os.getenv(var)]

    if missing:
        raise RuntimeError(
            "В .env отсутствуют необходимые настройки подключения."
        )

    # Загружаем полный датасет
    if not LOCAL_FILE_NAME.exists():
        download_file(YANDEX_DISK_URL, LOCAL_FILE_NAME)

    df = cast_types(load_data(LOCAL_FILE_NAME))

    if len(df) < ROWS_TO_UPLOAD:
        raise ValueError("В датасете меньше 100 строк.")

    # Выбираем первые 100 строк
    df_upload = df.head(ROWS_TO_UPLOAD).copy()

    print(f"Всего строк в датасете: {len(df)}")
    print(f"Будет загружено строк: {len(df_upload)}")
    print(f"Количество столбцов: {len(df_upload.columns)}")

    # Подключаемся к homeworks
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

                # Создаём описание столбцов таблицы
                columns_sql = []

                for column, dtype in df_upload.dtypes.items():
                    columns_sql.append(
                        sql.SQL("{} {}").format(
                            sql.Identifier(str(column)),
                            sql.SQL(get_postgres_type(dtype)),
                        )
                    )

                # Удаляем предыдущую версию своей таблицы,
                # чтобы при повторном запуске осталось ровно 100 строк.
                cursor.execute(
                    sql.SQL("DROP TABLE IF EXISTS {}").format(
                        sql.Identifier(TABLE_NAME)
                    )
                )

                cursor.execute(
                    sql.SQL("CREATE TABLE {} ({})").format(
                        sql.Identifier(TABLE_NAME),
                        sql.SQL(", ").join(columns_sql),
                    )
                )

                # Подготавливаем записи
                rows = [
                    tuple(convert_value(value) for value in row)
                    for row in df_upload.itertuples(
                        index=False, name=None
                    )
                ]

                # Записываем данные
                insert_query = sql.SQL(
                    "INSERT INTO {} ({}) VALUES %s"
                ).format(
                    sql.Identifier(TABLE_NAME),
                    sql.SQL(", ").join(
                        sql.Identifier(str(column))
                        for column in df_upload.columns
                    ),
                )

                execute_values(
                    cursor,
                    insert_query.as_string(connection),
                    rows,
                    page_size=100,
                )

                # Проверяем результат
                cursor.execute(
                    sql.SQL("SELECT COUNT(*) FROM {}").format(
                        sql.Identifier(TABLE_NAME)
                    )
                )

                count = cursor.fetchone()[0]

        print("\nЗагрузка завершена успешно!")
        print(f"Таблица: {TABLE_NAME}")
        print(f"Записано строк: {count}")

        if count != ROWS_TO_UPLOAD:
            raise RuntimeError(
                f"Ожидалось 100 строк, получено {count}."
            )

    finally:
        connection.close()


if __name__ == "__main__":
    main()
