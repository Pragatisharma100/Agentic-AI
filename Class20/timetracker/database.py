"""Persistence for the time tracker.

Set DATABASE_URL to a Neon PostgreSQL connection string in production.
Without it, local development uses SQLite next to this file.
"""
import os
import tempfile
from pathlib import Path

from sqlalchemy import create_engine, text


DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
else:
    db_path = Path(tempfile.gettempdir()) / "timetrack.db" if os.getenv("VERCEL") else Path(__file__).parent / "timetrack.db"
    engine = create_engine(f"sqlite:///{db_path}")


def init_db():
    id_definition = "SERIAL PRIMARY KEY" if engine.dialect.name == "postgresql" else "INTEGER PRIMARY KEY"
    with engine.begin() as connection:
        connection.execute(text(f"""
            CREATE TABLE IF NOT EXISTS time_entries (
                id {id_definition},
                employee_name TEXT NOT NULL,
                project TEXT NOT NULL,
                entry_date TEXT NOT NULL,
                hours REAL NOT NULL,
                description TEXT NOT NULL DEFAULT ''
            )
        """))
        count = connection.execute(text("SELECT COUNT(*) FROM time_entries")).scalar_one()
        if count == 0:
            connection.execute(text("""
                INSERT INTO time_entries
                    (employee_name, project, entry_date, hours, description)
                VALUES (:employee_name, :project, :entry_date, :hours, :description)
            """), [
                {"employee_name": "Asha Patel", "project": "Website Redesign", "entry_date": "2026-09-08", "hours": 6.5, "description": "Homepage layout"},
                {"employee_name": "Asha Patel", "project": "Website Redesign", "entry_date": "2026-09-09", "hours": 7.0, "description": "Mobile responsive fixes"},
                {"employee_name": "Asha Patel", "project": "Client Onboarding", "entry_date": "2026-09-10", "hours": 3.0, "description": "Kickoff call + notes"},
                {"employee_name": "Rahul Mehta", "project": "Website Redesign", "entry_date": "2026-09-08", "hours": 5.5, "description": "API integration"},
                {"employee_name": "Rahul Mehta", "project": "Internal Tools", "entry_date": "2026-09-09", "hours": 8.0, "description": "Dashboard bug fixes"},
            ])


def _row_to_dict(row) -> dict:
    return dict(row)


def list_all_entries() -> list[dict]:
    with engine.connect() as connection:
        rows = connection.execute(text(
            "SELECT * FROM time_entries ORDER BY entry_date DESC, id DESC"
        )).mappings().all()
    return [_row_to_dict(row) for row in rows]


def delete_entry(entry_id: int) -> bool:
    with engine.begin() as connection:
        result = connection.execute(text(
            "DELETE FROM time_entries WHERE id = :id"
        ), {"id": entry_id})
    return result.rowcount > 0


def log_time(employee_name: str, project: str, entry_date: str, hours: float, description: str = "") -> dict:
    if hours <= 0:
        raise ValueError("hours must be a positive number")
    with engine.begin() as connection:
        result = connection.execute(text("""
            INSERT INTO time_entries
                (employee_name, project, entry_date, hours, description)
            VALUES (:employee_name, :project, :entry_date, :hours, :description)
            RETURNING id
        """), {"employee_name": employee_name, "project": project, "entry_date": entry_date, "hours": hours, "description": description})
        new_id = result.scalar_one()
        row = connection.execute(text(
            "SELECT * FROM time_entries WHERE id = :id"
        ), {"id": new_id}).mappings().one()
    return _row_to_dict(row)


def get_timesheet(employee_name: str, start_date: str | None = None, end_date: str | None = None) -> list[dict]:
    query = "SELECT * FROM time_entries WHERE employee_name = :employee_name"
    params = {"employee_name": employee_name}
    if start_date:
        query += " AND entry_date >= :start_date"
        params["start_date"] = start_date
    if end_date:
        query += " AND entry_date <= :end_date"
        params["end_date"] = end_date
    query += " ORDER BY entry_date"
    with engine.connect() as connection:
        rows = connection.execute(text(query), params).mappings().all()
    return [_row_to_dict(row) for row in rows]


def execute_query(query: str, params: dict | None = None) -> list[dict]:
    with engine.connect() as connection:
        rows = connection.execute(text(query), params or {}).mappings().all()
    return [_row_to_dict(row) for row in rows]


def list_projects() -> list[str]:
    with engine.connect() as connection:
        rows = connection.execute(text(
            "SELECT DISTINCT project FROM time_entries ORDER BY project"
        )).mappings().all()
    return [row["project"] for row in rows]


def get_project_summary(project: str) -> dict:
    with engine.connect() as connection:
        rows = connection.execute(text("""
            SELECT employee_name, SUM(hours) AS total_hours
            FROM time_entries
            WHERE project = :project
            GROUP BY employee_name
            ORDER BY employee_name
        """), {"project": project}).mappings().all()
    if not rows:
        raise ValueError(f"No time logged against project '{project}'")
    by_employee = {row["employee_name"]: row["total_hours"] for row in rows}
    return {"project": project, "total_hours": sum(by_employee.values()), "by_employee": by_employee}
