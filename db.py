# db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Configura la URL de conexión a PostgreSQL (ajusta usuario, contraseña, host y base de datos)
DATABASE_URL = "postgresql://matias:contrasena@localhost:5432/app"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

