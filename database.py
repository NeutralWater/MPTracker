import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "mptracker.db"


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS packages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tracking_number TEXT NOT NULL UNIQUE,
                carrier TEXT NOT NULL,
                nickname TEXT,
                delivered INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def add_package(
    tracking_number: str,
    carrier: str,
    nickname: str | None = None,
) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO packages (
                tracking_number,
                carrier,
                nickname
            )
            VALUES (?, ?, ?)
            """,
            (
                tracking_number,
                carrier,
                nickname,
            ),
        )


def get_active_packages() -> list[sqlite3.Row]:
    with get_connection() as connection:
        return connection.execute(
            """
            SELECT *
            FROM packages
            WHERE delivered = 0
            ORDER BY created_at DESC
            """
        ).fetchall()


def mark_delivered(tracking_number: str) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE packages
            SET delivered = 1
            WHERE tracking_number = ?
            """,
            (tracking_number,),
        )

def remove_package(tracking_number: str) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            DELETE FROM packages
            WHERE tracking_number = ?
            """,
            (tracking_number,),
        )

    connection.close()