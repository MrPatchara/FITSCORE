from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session
from app.config import DATABASE_URL

# Create the SQLite Database Engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=False)

# Session Factories
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = scoped_session(SessionLocal)

# Declarative Base for models
Base = declarative_base()


def _migrate_db():
    """
    Auto-migrate: adds missing columns to existing tables.
    Safe to run multiple times — silently skips columns that already exist.
    """
    inspector = inspect(engine)
    
    # ── Migrate 'groups' table ──
    if "groups" in inspector.get_table_names():
        existing_cols = {col["name"] for col in inspector.get_columns("groups")}
        new_columns = [
            ("address", "TEXT"),
            ("province", "VARCHAR(50)"),
            ("district", "VARCHAR(50)"),
            ("sub_district", "VARCHAR(50)"),
            ("postal_code", "VARCHAR(10)"),
            ("coordinator_name", "VARCHAR(100)"),
            ("coordinator_phone", "VARCHAR(20)"),
            ("coordinator_email", "VARCHAR(100)"),
            ("supervisor_name", "VARCHAR(100)"),
            ("supervisor_phone", "VARCHAR(20)"),
            ("supervisor_email", "VARCHAR(100)"),
        ]
        with engine.connect() as conn:
            for col_name, col_type in new_columns:
                if col_name not in existing_cols:
                    conn.execute(text(f"ALTER TABLE groups ADD COLUMN {col_name} {col_type}"))
            conn.commit()

    # ── Migrate 'athletes' table ──
    if "athletes" in inspector.get_table_names():
        existing_ath_cols = {col["name"] for col in inspector.get_columns("athletes")}
        new_ath_columns = [
            ("address", "TEXT"),
            ("phone", "VARCHAR(20)"),
            ("email", "VARCHAR(100)"),
        ]
        with engine.connect() as conn:
            for col_name, col_type in new_ath_columns:
                if col_name not in existing_ath_cols:
                    conn.execute(text(f"ALTER TABLE athletes ADD COLUMN {col_name} {col_type}"))
            conn.commit()


def init_db():
    """
    Creates all tables in the SQLite database based on the metadata.
    Also runs auto-migration for schema updates.
    """
    # Import models here to ensure they are registered on the Base metadata
    import app.models.athlete
    import app.models.test_type
    import app.models.record
    import app.models.standard
    
    _migrate_db()
    Base.metadata.create_all(bind=engine)
