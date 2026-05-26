"""
Compatibility entrypoint for older setup instructions.

Database schema and bootstrap data are now managed by Alembic migrations.
Run directly with: alembic upgrade head
"""
from alembic.config import main


if __name__ == "__main__":
    main(argv=["upgrade", "head"])
