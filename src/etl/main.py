import argparse
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

from etl.extract import extract
from etl.load import load
from etl.transform import transform
from etl.validate import validate


BASE_DIR = Path(__file__).resolve().parents[2]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Industrial Dataset ETL pipeline"
    )

    parser.add_argument(
        "--source",
        type=str,
        default=None,
        help="Path to source CSV file",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Maximum number of rows to upload",
    )

    parser.add_argument(
        "--table",
        type=str,
        default="akhmetkhanovar",
        help="PostgreSQL destination table",
    )

    args = parser.parse_args()

    if not 1 <= args.limit <= 100:
        parser.error("--limit должен быть от 1 до 100.")

    load_dotenv(BASE_DIR / ".env")

    required_vars = [
        "HOMEWORK_HOST",
        "HOMEWORK_PORT",
        "HOMEWORK_USER",
        "HOMEWORK_PASSWORD",
        "HOMEWORK_DB",
    ]

    missing = [
        var for var in required_vars
        if not os.getenv(var)
    ]

    if missing:
        raise RuntimeError(
            f"В .env отсутствуют настройки: {missing}"
        )

    logger.info("ETL: Extract")
    df = extract(args.source)
    logger.info("Получено строк: %d", len(df))

    logger.info("ETL: Transform")
    df = transform(df)

    logger.info("ETL: Validate")
    validate(df)

    logger.info("ETL: Load")
    df = df.head(args.limit).copy()

    count = load(df, args.table)

    if count != len(df):
        raise RuntimeError(
            f"Ожидалось {len(df)} строк, загружено {count}"
        )

    logger.info("ETL pipeline завершён успешно!")


if __name__ == "__main__":
    main()
