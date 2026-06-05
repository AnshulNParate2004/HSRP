"""Apply lightweight schema upgrades for existing databases."""

from sqlalchemy import inspect, text

from app.db.session import engine


def run_schema_upgrades() -> None:
    insp = inspect(engine)
    if not insp.has_table("orders"):
        return
    cols = {c["name"] for c in insp.get_columns("orders")}
    with engine.begin() as conn:
        if "external_id" not in cols:
            conn.execute(text("ALTER TABLE orders ADD COLUMN external_id VARCHAR(80)"))
        if "last_synced_at" not in cols:
            conn.execute(text("ALTER TABLE orders ADD COLUMN last_synced_at DATETIME"))


if __name__ == "__main__":
    run_schema_upgrades()
    print("Schema upgrade complete")
