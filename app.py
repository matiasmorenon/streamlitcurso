# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from services import (
    crear_curso,
    actualizar_curso,
    eliminar_curso,
    obtener_cursos,
    exportar_cursos,
    crear_cliente,
    actualizar_cliente,
    obtener_clientes,
    importar_clientes_desde_excel,
    crear_venta,
    obtener_ventas,
    crear_devolucion,
    crear_comision,
    obtener_reportes_ventas,
    obtener_reportes_clientes,
)
from datetime import datetime

st.set_page_config(page_title="Gestión de Cursos, Clientes y Ventas", layout="wide")

# Menú lateral de navegación
st.sidebar.title("Menú")
opcion = st.sidebar.radio(
    "Selecciona una opción:",
    ["Cursos", "Clientes", "Ventas", "Devoluciones", "Comisiones", "Analytics"],
)

if opcion == "Cursos":
    st.header("Gestión de Cursos")
    accion = st.selectbox(
        "Acción", ["Registrar", "Editar", "Eliminar", "Ver", "Exportar"]
    )

    if accion == "Registrar":
        with st.form("form_curso"):
            nombre = st.text_input("Nombre del Curso")
            descripcion = st.text_area("Descripción")
            precio = st.number_input("Precio", min_value=0.0, value=0.0, step=0.1)
            submit = st.form_submit_button("Registrar")
        if submit:
            result = crear_curso(nombre, descripcion, precio)
            if isinstance(result, dict) and "error" in result:
                st.error(result["error"])
            else:
                st.success("Curso registrado exitosamente")

    elif accion == "Editar":
        data = obtener_cursos(per_page=100)
        df = pd.DataFrame(
            [
                {
                    "ID": c.id,
                    "Nombre": c.nombre,
                    "Descripción": c.descripcion,
                    "Precio": c.precio,
                }
                for c in data["cursos"]
            ]
        )
        st.dataframe(df)
        curso_id = st.number_input("Ingrese ID del curso a editar", min_value=1, step=1)
        nombre = st.text_input("Nuevo nombre")
        descripcion = st.text_area("Nueva descripción")
        precio = st.number_input("Nuevo precio", min_value=0.0, value=0.0, step=0.1)
        if st.button("Actualizar"):
            result = actualizar_curso(curso_id, nombre, descripcion, precio)
            if isinstance(result, dict) and "error" in result:
                st.error(result["error"])
            else:
                st.success("Curso actualizado")

    elif accion == "Eliminar":
        curso_id = st.number_input(
            "Ingrese ID del curso a eliminar", min_value=1, step=1
        )
        if st.button("Eliminar"):
            result = eliminar_curso(curso_id)
            if "error" in result:
                st.error(result["error"])
            else:
                st.success(result["message"])

    elif accion == "Ver":
        busqueda = st.text_input("Buscar curso por nombre o descripción")
        page = st.number_input("Página", min_value=1, value=1, step=1)
        data = obtener_cursos(busqueda=busqueda, page=page)
        df = pd.DataFrame(
            [
                {
                    "ID": c.id,
                    "Nombre": c.nombre,
                    "Descripción": c.descripcion,
                    "Precio": c.precio,
                    "Fecha Creación": c.fecha_creacion,
                }
                for c in data["cursos"]
            ]
        )
        st.dataframe(df)

    elif accion == "Exportar":
        formato = st.selectbox("Formato", ["csv", "excel"])
        busqueda = st.text_input("Filtrar cursos (opcional)")
        data_export = exportar_cursos(formato=formato, busqueda=busqueda)
        if formato == "csv":
            st.download_button(
                "Descargar CSV", data_export, file_name="cursos.csv", mime="text/csv"
            )
        else:
            st.download_button(
                "Descargar Excel",
                data_export,
                file_name="cursos.xlsx",
                mime="application/vnd.ms-excel",
            )

elif opcion == "Clientes":
    st.header("Gestión de Clientes")
    accion = st.selectbox("Acción", ["Registrar", "Editar", "Ver", "Importar"])

    if accion == "Registrar":
        with st.form("form_cliente"):
            nombre = st.text_input("Nombre")
            email = st.text_input("Email")
            telefono = st.text_input("Teléfono")
            pais = st.text_input("País")
            fuente_referencia = st.text_input("Fuente de Referencia")
            submit = st.form_submit_button("Registrar Cliente")
        if submit:
            result = crear_cliente(nombre, email, telefono, pais, fuente_referencia)
            if isinstance(result, dict) and "error" in result:
                st.error(result["error"])
            else:
                st.success("Cliente registrado exitosamente")

    elif accion == "Editar":
        clientes = obtener_clientes()
        df = pd.DataFrame(
            [
                {"ID": c.id, "Nombre": c.nombre, "Email": c.email, "País": c.pais}
                for c in clientes
            ]
        )
        st.dataframe(df)
        cliente_id = st.number_input(
            "Ingrese ID del cliente a editar", min_value=1, step=1
        )
        nombre = st.text_input("Nuevo nombre")
        email = st.text_input("Nuevo email")
        telefono = st.text_input("Nuevo teléfono")
        pais = st.text_input("Nuevo país")
        fuente_referencia = st.text_input("Nueva fuente de referencia")
        if st.button("Actualizar Cliente"):
            result = actualizar_cliente(
                cliente_id, nombre, email, telefono, pais, fuente_referencia
            )
            if isinstance(result, dict) and "error" in result:
                st.error(result["error"])
            else:
                st.success("Cliente actualizado")

    elif accion == "Ver":
        busqueda = st.text_input("Buscar cliente")
        clientes = obtener_clientes(busqueda=busqueda)
        df = pd.DataFrame(
            [
                {
                    "ID": c.id,
                    "Nombre": c.nombre,
                    "Email": c.email,
                    "País": c.pais,
                    "Fuente": c.fuente_referencia,
                }
                for c in clientes
            ]
        )
        st.dataframe(df)

    elif accion == "Importar":
        st.info("Seleccione un archivo Excel para importar clientes")
        file = st.file_uploader("Subir archivo", type=["xlsx"])
        if file:
            result = importar_clientes_desde_excel(file)
            if "error" in result:
                st.error(result["error"])
            else:
                st.success(
                    f"Importación completa. Clientes insertados: {result['insertados']}"
                )
                if result["errores"]:
                    st.warning("Errores durante la importación:")
                    for err in result["errores"]:
                        st.write(err)

elif opcion == "Ventas":
    st.header("Gestión de Ventas")
    accion = st.selectbox("Acción", ["Registrar", "Ver"])

    if accion == "Registrar":
        with st.form("form_venta"):
            cliente_id = st.number_input("ID del Cliente", min_value=1, step=1)
            curso_id = st.number_input("ID del Curso", min_value=1, step=1)
            monto = st.number_input(
                "Monto de Venta", min_value=0.0, value=0.0, step=0.1
            )
            submit = st.form_submit_button("Registrar Venta")
        if submit:
            result = crear_venta(cliente_id, curso_id, monto)
            if isinstance(result, dict) and "error" in result:
                st.error(result["error"])
            else:
                st.success("Venta registrada")

    elif accion == "Ver":
        ventas = obtener_ventas()
        df = pd.DataFrame(
            [
                {
                    "ID": v.id,
                    "Cliente ID": v.cliente_id,
                    "Curso ID": v.curso_id,
                    "Monto": v.monto,
                    "Fecha": v.fecha_venta,
                }
                for v in ventas
            ]
        )
        st.dataframe(df)

elif opcion == "Devoluciones":
    st.header("Gestión de Devoluciones")
    with st.form("form_devolucion"):
        venta_id = st.number_input("ID de la Venta", min_value=1, step=1)
        motivo = st.text_area("Motivo de la devolución")
        monto_reembolso = st.number_input(
            "Monto a reembolsar", min_value=0.0, value=0.0, step=0.1
        )
        submit = st.form_submit_button("Registrar Devolución")
    if submit:
        result = crear_devolucion(venta_id, motivo, monto_reembolso)
        if isinstance(result, dict) and "error" in result:
            st.error(result["error"])
        else:
            st.success("Devolución registrada")

elif opcion == "Comisiones":
    st.header("Gestión de Comisiones")
    with st.form("form_comision"):
        venta_id = st.number_input("ID de la Venta", min_value=1, step=1)
        closer = st.text_input("Nombre del Closer")
        porcentaje = st.number_input(
            "Porcentaje de comisión", min_value=0.0, value=0.0, step=0.1
        )
        ajuste_manual = st.number_input(
            "Ajuste manual", min_value=0.0, value=0.0, step=0.1
        )
        submit = st.form_submit_button("Registrar Comisión")
    if submit:
        result = crear_comision(venta_id, closer, porcentaje, ajuste_manual)
        if isinstance(result, dict) and "error" in result:
            st.error(result["error"])
        else:
            st.success("Comisión registrada")

elif opcion == "Analytics":
    st.header("Dashboard y Análisis Avanzados")

    st.subheader("Reporte de Ventas")
    df_ventas = obtener_reportes_ventas()
    if not df_ventas.empty:
        fig = px.line(
            df_ventas, x="fecha_venta", y="monto", title="Tendencia de Ventas"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("No hay datos de ventas")

    st.subheader("Reporte de Clientes")
    df_clientes = obtener_reportes_clientes()
    st.dataframe(df_clientes)
    # Se pueden agregar más gráficos y análisis (por ejemplo, análisis geográfico) según se requiera.
