import logging
import os

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


logger = logging.getLogger(__name__)


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


def load(
    df: pd.DataFrame,
    table_name: str = "akhmetkhanovar",
) -> int:
    """Load transformed data into PostgreSQL using pandas.to_sql."""

    if not table_name.replace("_", "").isalnum():
        raise ValueError("Некорректное имя таблицы.")

    engine = get_engine()

    try:
        with engine.begin() as connection:
            df.to_sql(
                name=table_name,
                con=connection,
                if_exists="replace",
                index=False,
                method="multi",
                chunksize=100,
            )

            count = connection.execute(
                text(f'SELECT COUNT(*) FROM "{table_name}"')
            ).scalar_one()

        logger.info("Загружено строк: %d", count)
        return int(count)

    finally:
        engine.dispose()
