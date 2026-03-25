import os
import databases

# SQLite domyślnie — plik life_dashboard.db w katalogu backend/
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./life_dashboard.db"
)

database = databases.Database(DATABASE_URL)
