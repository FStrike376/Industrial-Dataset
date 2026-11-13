import argparse
import os
from pathlib import Path

from dotenv import load_dotenv

from etl.extract import extract
from etl.transform import transform
from etl.validate import validate
from etl.load import load


BASE_DIR = Path(__file__).resolve().parents[2]


def main():
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

    print("ETL: Extract")

    df = extract(args.source)
    print(f"Получено строк: {len(df)}")

    print("\nETL: Transform")

    df = transform(df)

    print("\nETL: Validate")

    validate(df)

    print("\nETL: Load")

    df = df.head(args.limit).copy()

    count = load(df, args.table)

    if count != len(df):
        raise RuntimeError(
            f"Ожидалось {len(df)} строк, загружено {count}"
        )

    print("\nETL pipeline завершён успешно!")


if __name__ == "__main__":
    main()