# services.py
from db import SessionLocal
from models import Curso, Cliente, Venta, Devolucion, Comision, Socio
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_
import pandas as pd


# --- Gestión de Cursos ---
def crear_curso(nombre, descripcion, precio, fecha_creacion=None):
    db = SessionLocal()
    try:
        # Validar que el nombre sea único
        curso_existente = db.query(Curso).filter(Curso.nombre == nombre).first()
        if curso_existente:
            return {"error": "El curso ya existe"}
        nuevo_curso = Curso(nombre=nombre, descripcion=descripcion, precio=precio)
        if fecha_creacion:
            nuevo_curso.fecha_creacion = fecha_creacion
        db.add(nuevo_curso)
        db.commit()
        db.refresh(nuevo_curso)
        return nuevo_curso
    except IntegrityError as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()


def actualizar_curso(curso_id, nombre, descripcion, precio):
    db = SessionLocal()
    try:
        curso = db.query(Curso).filter(Curso.id == curso_id).first()
        if not curso:
            return {"error": "Curso no encontrado"}
        # Validar que el nuevo nombre sea único si se cambia
        if nombre != curso.nombre:
            curso_existente = db.query(Curso).filter(Curso.nombre == nombre).first()
            if curso_existente:
                return {"error": "Ya existe otro curso con ese nombre"}
        curso.nombre = nombre
        curso.descripcion = descripcion
        curso.precio = precio
        db.commit()
        db.refresh(curso)
        return curso
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()


def eliminar_curso(curso_id):
    db = SessionLocal()
    try:
        curso = db.query(Curso).filter(Curso.id == curso_id).first()
        if not curso:
            return {"error": "Curso no encontrado"}
        db.delete(curso)
        db.commit()
        return {"message": "Curso eliminado"}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()


def obtener_cursos(busqueda=None, filtro=None, orden="asc", page=1, per_page=10):
    db = SessionLocal()
    try:
        query = db.query(Curso)
        if busqueda:
            query = query.filter(
                or_(
                    Curso.nombre.ilike(f"%{busqueda}%"),
                    Curso.descripcion.ilike(f"%{busqueda}%"),
                )
            )
        if orden == "asc":
            query = query.order_by(Curso.fecha_creacion.asc())
        else:
            query = query.order_by(Curso.fecha_creacion.desc())
        total = query.count()
        cursos = query.offset((page - 1) * per_page).limit(per_page).all()
        return {"total": total, "cursos": cursos}
    finally:
        db.close()


def exportar_cursos(formato="csv", busqueda=None):
    data = obtener_cursos(busqueda=busqueda, per_page=1000)  # ajustar si es necesario
    cursos = data["cursos"]
    rows = []
    for curso in cursos:
        rows.append(
            {
                "id": curso.id,
                "nombre": curso.nombre,
                "descripcion": curso.descripcion,
                "precio": curso.precio,
                "fecha_creacion": curso.fecha_creacion,
            }
        )
    df = pd.DataFrame(rows)
    if formato == "csv":
        return df.to_csv(index=False)
    elif formato == "excel":
        from io import BytesIO

        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Cursos")
        return output.getvalue()


# --- Gestión de Clientes ---
def crear_cliente(nombre, email, telefono, pais, fuente_referencia):
    db = SessionLocal()
    try:
        # Validar duplicidad por email
        cliente_existente = db.query(Cliente).filter(Cliente.email == email).first()
        if cliente_existente:
            return {"error": "El cliente con este email ya existe"}
        nuevo_cliente = Cliente(
            nombre=nombre,
            email=email,
            telefono=telefono,
            pais=pais,
            fuente_referencia=fuente_referencia,
        )
        db.add(nuevo_cliente)
        db.commit()
        db.refresh(nuevo_cliente)
        return nuevo_cliente
    except IntegrityError as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()


def actualizar_cliente(cliente_id, nombre, email, telefono, pais, fuente_referencia):
    db = SessionLocal()
    try:
        cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
        if not cliente:
            return {"error": "Cliente no encontrado"}
        if email != cliente.email:
            if db.query(Cliente).filter(Cliente.email == email).first():
                return {"error": "Ya existe otro cliente con ese email"}
        cliente.nombre = nombre
        cliente.email = email
        cliente.telefono = telefono
        cliente.pais = pais
        cliente.fuente_referencia = fuente_referencia
        db.commit()
        db.refresh(cliente)
        return cliente
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()


def obtener_clientes(busqueda=None, filtro=None):
    db = SessionLocal()
    try:
        query = db.query(Cliente)
        if busqueda:
            query = query.filter(
                or_(
                    Cliente.nombre.ilike(f"%{busqueda}%"),
                    Cliente.email.ilike(f"%{busqueda}%"),
                    Cliente.pais.ilike(f"%{busqueda}%"),
                )
            )
        clientes = query.all()
        return clientes
    finally:
        db.close()


def importar_clientes_desde_excel(file):
    try:
        df = pd.read_excel(file)
    except Exception as e:
        return {"error": f"Error al leer el archivo: {str(e)}"}
    expected_cols = ["nombre", "email", "telefono", "pais", "fuente_referencia"]
    if not all(col in df.columns for col in expected_cols):
        return {
            "error": "Formato de archivo incorrecto. Se requieren columnas: nombre, email, telefono, pais, fuente_referencia"
        }
    db = SessionLocal()
    report = {"insertados": 0, "errores": []}
    for index, row in df.iterrows():
        try:
            if db.query(Cliente).filter(Cliente.email == row["email"]).first():
                report["errores"].append(
                    f"Fila {index + 2}: Cliente con email {row['email']} ya existe."
                )
                continue
            nuevo_cliente = Cliente(
                nombre=row["nombre"],
                email=row["email"],
                telefono=str(row["telefono"]),
                pais=row["pais"],
                fuente_referencia=row["fuente_referencia"],
            )
            db.add(nuevo_cliente)
            db.commit()
            report["insertados"] += 1
        except Exception as e:
            db.rollback()
            report["errores"].append(f"Fila {index + 2}: Error - {str(e)}")
    db.close()
    return report


# --- Gestión de Ventas ---
def crear_venta(cliente_id, curso_id, monto, fecha_venta=None):
    db = SessionLocal()
    try:
        from models import Cliente, Curso  # Asegurarse de validar existencia

        cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
        curso = db.query(Curso).filter(Curso.id == curso_id).first()
        if not cliente or not curso:
            return {"error": "Cliente o Curso no encontrado"}
        if monto <= 0:
            return {"error": "El monto de la venta debe ser positivo"}
        nueva_venta = Venta(cliente_id=cliente_id, curso_id=curso_id, monto=monto)
        if fecha_venta:
            nueva_venta.fecha_venta = fecha_venta
        db.add(nueva_venta)
        db.commit()
        db.refresh(nueva_venta)
        return nueva_venta
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()


def obtener_ventas(filtro=None):
    db = SessionLocal()
    try:
        query = db.query(Venta)
        ventas = query.all()
        return ventas
    finally:
        db.close()


# --- Gestión de Devoluciones ---
def crear_devolucion(venta_id, motivo, monto_reembolso, fecha_devolucion=None):
    db = SessionLocal()
    try:
        venta = db.query(Venta).filter(Venta.id == venta_id).first()
        if not venta:
            return {"error": "Venta no encontrada"}
        if monto_reembolso > venta.monto:
            return {
                "error": "El monto de reembolso no puede exceder el monto de la venta"
            }
        devolucion = Devolucion(
            venta_id=venta_id, motivo=motivo, monto_reembolso=monto_reembolso
        )
        if fecha_devolucion:
            devolucion.fecha_devolucion = fecha_devolucion
        db.add(devolucion)
        db.commit()
        db.refresh(devolucion)
        return devolucion
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()


# --- Gestión de Comisiones ---
def crear_comision(venta_id, closer, porcentaje, ajuste_manual=0.0):
    db = SessionLocal()
    try:
        venta = db.query(Venta).filter(Venta.id == venta_id).first()
        if not venta:
            return {"error": "Venta no encontrada"}
        monto_comision = venta.monto * (porcentaje / 100) + ajuste_manual
        comision = Comision(
            venta_id=venta_id,
            closer=closer,
            porcentaje=porcentaje,
            monto_comision=monto_comision,
            ajuste_manual=ajuste_manual,
        )
        db.add(comision)
        db.commit()
        db.refresh(comision)
        return comision
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()


# --- Funciones de Reportes y Analytics ---
def obtener_reportes_ventas():
    db = SessionLocal()
    try:
        ventas = db.query(Venta).all()
        data = []
        for venta in ventas:
            data.append(
                {
                    "id": venta.id,
                    "cliente_id": venta.cliente_id,
                    "curso_id": venta.curso_id,
                    "monto": venta.monto,
                    "fecha_venta": venta.fecha_venta,
                }
            )
        df = pd.DataFrame(data)
        return df
    finally:
        db.close()


def obtener_reportes_clientes():
    db = SessionLocal()
    try:
        clientes = db.query(Cliente).all()
        data = []
        for cliente in clientes:
            data.append(
                {
                    "id": cliente.id,
                    "nombre": cliente.nombre,
                    "email": cliente.email,
                    "pais": cliente.pais,
                    "fuente_referencia": cliente.fuente_referencia,
                }
            )
        df = pd.DataFrame(data)
        return df
    finally:
        db.close()
