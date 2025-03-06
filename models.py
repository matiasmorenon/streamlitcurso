# models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from db import Base


class Curso(Base):
    __tablename__ = "cursos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)
    descripcion = Column(Text, nullable=False)
    precio = Column(Float, nullable=False)
    fecha_creacion = Column(DateTime, default=func.now(), nullable=False)


class Cliente(Base):
    __tablename__ = "clientes"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    telefono = Column(String(20), nullable=False)
    pais = Column(String(50), nullable=False)
    fuente_referencia = Column(String(100), nullable=False)
    fecha_creacion = Column(DateTime, default=func.now(), nullable=False)


class Venta(Base):
    __tablename__ = "ventas"
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    curso_id = Column(Integer, ForeignKey("cursos.id"), nullable=False)
    monto = Column(Float, nullable=False)
    fecha_venta = Column(DateTime, default=func.now(), nullable=False)


class Devolucion(Base):
    __tablename__ = "devoluciones"
    id = Column(Integer, primary_key=True, index=True)
    venta_id = Column(Integer, ForeignKey("ventas.id"), nullable=False)
    fecha_devolucion = Column(DateTime, default=func.now(), nullable=False)
    motivo = Column(Text, nullable=False)
    monto_reembolso = Column(Float, nullable=False)


class Comision(Base):
    __tablename__ = "comisiones"
    id = Column(Integer, primary_key=True, index=True)
    venta_id = Column(Integer, ForeignKey("ventas.id"), nullable=False)
    closer = Column(String(100), nullable=False)
    porcentaje = Column(Float, nullable=False)  # Porcentaje de comisión
    monto_comision = Column(Float, nullable=False)
    ajuste_manual = Column(Float, default=0.0)


class Socio(Base):
    __tablename__ = "socios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    porcentaje_participacion = Column(Float, nullable=False)


# Nota: La distribución de beneficios se puede calcular dinámicamente
