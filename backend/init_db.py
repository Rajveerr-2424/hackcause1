from backend import models, database

# Create tables for SQLite specifically
models.Base.metadata.create_all(bind=database.engine)
print("SQLite Database initialized successfully.")
