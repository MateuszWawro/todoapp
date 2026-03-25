import os
import databases

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://dashboard:changeme@localhost:5432/life_dashboard"
)

database = databases.Database(DATABASE_URL)
