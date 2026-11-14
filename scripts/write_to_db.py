import os
import sys
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL


# Пути проекта
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from data_loader import (
    LOCAL_FILE_NAME,
    YANDEX_DISK_URL,
    cast_types,
    download_file,
    load_data,
)

# Настройки
TABLE_NAME = "akhmetkhanovar"
ROWS_TO_UPLOAD = 100


def get_engine():
    """Create a SQLAlchemy engine from environment variables."""

    connection_url = URL.create(
        drivername="postgresql+psycopg2",
        username=os.getenv("HOMEWORK_USER"),
        password=os.getenv("HOMEWORK_PASSWORD"),
        host=os.getenv("HOMEWORK_HOST"),
        port=int(os.getenv("HOMEWORK_PORT", "5432")),
        database=os.getenv("HOMEWORK_DB"),
    )
    return create_engine(connection_url, connect_args={"connect_timeout": 10})


def main() -> None:
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
            f"В .env отсутствуют необходимые настройки подключения: {missing}"
        )

    if not LOCAL_FILE_NAME.exists():
        download_file(YANDEX_DISK_URL, LOCAL_FILE_NAME)

    df = cast_types(load_data(LOCAL_FILE_NAME))

    if len(df) < ROWS_TO_UPLOAD:
        raise ValueError("В датасете меньше 100 строк.")

    df_upload = df.head(ROWS_TO_UPLOAD).copy()

    print(f"Всего строк в датасете: {len(df)}")
    print(f"Будет загружено строк: {len(df_upload)}")
    print(f"Количество столбцов: {len(df_upload.columns)}")

    engine = get_engine()

    try:
        with engine.begin() as connection:
            df_upload.to_sql(
                name=TABLE_NAME,
                con=connection,
                if_exists="replace",
                index=False,
                method="multi",
                chunksize=ROWS_TO_UPLOAD,
            )

            df_loaded = pd.read_sql_table(TABLE_NAME, con=connection)
            count = len(df_loaded)

        print("\nЗагрузка и проверка чтения завершены успешно!")
        print(f"Таблица: {TABLE_NAME}")
        print(f"Прочитано строк из БД через pd.read_sql_table: {count}")

        if count != ROWS_TO_UPLOAD:
            raise RuntimeError(
                f"Ожидалось {ROWS_TO_UPLOAD} строк, получено {count}."
            )

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
