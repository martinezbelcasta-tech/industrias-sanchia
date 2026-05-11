import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN Y ESTILOS
st.set_page_config(page_title="Sanchia Dashboard Premium", layout="wide")

# Estilo para las tarjetas de colores (resaltando el número)
def crear_tarjeta(titulo, valor, color_borde, unidad=""):
    st.markdown(f"""
        <div style="background-color: #ffffff; padding: 15px; border-radius: 10px; border-left: 6px solid {color_borde}; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); margin-bottom: 15px;">
            <p style="margin:0; font-size: 13px; color: #666; font-weight: bold; text-transform: uppercase;">{titulo}</p>
            <p style="margin:0; font-size: 28px; font-weight: bold; color: {color_borde};">{valor} <span style="font-size:14px;">{unidad}</span></p>
        </div>
    """, unsafe_allow_html=True)

st.title("🚀 Sistema Integral de Control de Producción")
st.markdown("---")

# 2. CARGA DE DATOS
archivo = st.sidebar.file_uploader("Subir Data app.xlsx", type=["xlsx"])
st.sidebar.title("🚀 Menú Principal")
pagina = st.sidebar.radio("Ir a:", ["📈 Dashboard General", "🗑️ Análisis de Desperdicios"])

if archivo:
    df = pd.read_excel(archivo)
    df.columns = [str(c).strip().upper() for c in df.columns]

    # Detección de columnas
    def buscar_col(lista_posibles):
        for p in lista_posibles:
            for col in df.columns:
                if p in col: return col
        return None

    c_fecha = buscar_col(["FECHA"])
    c_efec = buscar_col(["TON EFECTIVAS", "EFECTIVAS"])
    c_cons = buscar_col(["TOTAL DE CONSUMO", "CONSUMO"])
    c_mala = buscar_col(["PIEZA MALA KG", "MALA"])
    c_reba = buscar_col(["REBABA KG", "REBABA"])
    c_desp = buscar_col(["DESPERDICIO"])

    if c_fecha:
        df[c_fecha] = pd.to_datetime(df[c_fecha])
        meses_dict = {1:"Enero", 2:"Febrero", 3:"Marzo", 4:"Abril", 5:"Mayo", 6:"Junio",
                      7:"Julio", 8:"Agosto", 9:"Septiembre", 10:"Octubre", 11:"Noviembre", 12:"Diciembre"}
        df["MES_NOMBRE"] = df[c_fecha].dt.month.map(meses_dict)
        st.sidebar.markdown("---")
        mes_sel = st.sidebar.selectbox("Selecciona el Mes:", df["MES_NOMBRE"].unique())
        df_filtrado = df[df["MES_NOMBRE"] == mes_sel].copy()
    else:
        df_filtrado = df.copy()

    dias_proyectar = st.sidebar.slider("Días totales del mes para proyección:", 1, 31, 30)

    if pagina == "📈 Dashboard General" and not df_filtrado.empty:
        # CÁLCULOS
        t_efec = df_filtrado[c_efec].sum() if c_efec else 0
        t_cons = df_filtrado[c_cons].sum() if c_cons else 0
        t_mala = df_filtrado[c_mala].sum() if c_mala else 0
        t_reba = df_filtrado[c_reba].sum() if c_reba else 0
        df_op = df_filtrado[df_filtrado[c_efec] > 0] if c_efec else df_filtrado
        d_op = max(len(df_op), 1)
        p_efec, p_cons = t_efec / d_op, t_cons / d_op
        p_mala, p_reba = t_mala / d_op, t_reba / d_op

        # FILA 1: PROYECCIONES
        st.subheader(f"📈 Proyecciones al Cierre")
        col1, col2, col3, col4 = st.columns(4)
        with col1: crear_tarjeta("Proy. Efectivas", f"{p_efec * dias_proyectar:,.2f}", "#1E88E5", "Tn")
        with col2: crear_tarjeta("Proy. Consumo", f"{p_cons * dias_proyectar:,.2f}", "#1E88E5", "Tn")
        with col3: crear_tarjeta("Proy. Mala", f"{p_mala * dias_proyectar:,.2f}", "#1E88E5", "Kg")
        with col4: crear_tarjeta("Proy. Rebaba", f"{p_reba * dias_proyectar:,.2f}", "#1E88E5", "Kg")

        # FILA 2: PROMEDIOS
        st.subheader(f"📊 Promedio Diario")
        col5, col6, col7, col8 = st.columns(4)
        with col5: crear_tarjeta("Prom. Efectivas", f"{p_efec:,.2f}", "#43A047", "Tn/d")
        with col6: crear_tarjeta("Prom. Consumo", f"{p_cons:,.2f}", "#43A047", "Tn/d")
        with col7: crear_tarjeta("Prom. Mala", f"{p_mala:,.2f}", "#43A047", "Kg/d")
        with col8: crear_tarjeta("Prom. Rebaba", f"{p_reba:,.2f}", "#43A047", "Kg/d")

        # FILA 3: REAL ACUMULADO
        st.subheader(f"📁 Real Acumulado")
        col9, col10, col11, col12 = st.columns(4)
        with col9: crear_tarjeta("Total Efectivas", f"{t_efec:,.2f}", "#FB8C00", "Tn")
        with col10: crear_tarjeta("Total Consumo", f"{t_cons:,.2f}", "#FB8C00", "Tn")
        with col11: crear_tarjeta("Total Mala", f"{t_mala:,.2f}", "#FB8C00", "Kg")
        with col12: crear_tarjeta("Total Rebaba", f"{t_reba:,.2f}", "#FB8C00", "Kg")

        st.markdown("---")

        # GRÁFICA Y TABLA (UNIFICADOS)
        st.subheader("📊 Gráfica de Tendencia y Datos Diarios")
        opciones_v = {c_efec: "Efectivas", c_cons: "Consumo", c_mala: "Mala (Kg)", c_reba: "Rebaba (Kg)"}
        vars_sel = st.multiselect("Variables:", options=list(opciones_v.keys()), default=[c_efec], format_func=lambda x: opciones_v[x])

        if vars_sel:
            df_plot = df_filtrado.copy()
            df_plot[c_fecha] = df_plot[c_fecha].dt.strftime('%d-%m-%Y')
            
            # Gráfica
            fig = px.bar(df_plot, x=c_fecha, y=vars_sel, barmode="group", text_auto='.2f')
            fig.update_traces(textfont_size=24, textposition="outside", cliponaxis=False)
            fig.update_layout(height=500, margin=dict(t=50, b=0))
            st.plotly_chart(fig, use_container_width=True)

            # Tabla (Justo debajo de la gráfica)
            st.markdown("### 📋 Datos Detallados por Día")
            df_tabla = df_filtrado[[c_fecha] + vars_sel].copy()
            df_tabla[c_fecha] = df_tabla[c_fecha].dt.strftime('%d-%m-%Y')
            st.dataframe(df_tabla.style.format({col: "{:,.2f}" for col in vars_sel}), use_container_width=True)

        st.markdown("---")

        # DETALLE POR FECHA (TAL CUAL LA IMAGEN)
        st.subheader("📅 Detalle por Fecha")
        fecha_sel = st.selectbox("Selecciona una fecha:", df_filtrado[c_fecha].dt.date.unique())
        df_dia = df_filtrado[df_filtrado[c_fecha].dt.date == fecha_sel]
        
        if not df_dia.empty:
            d1, d2, d3, d4, d5 = st.columns(5)
            with d1: crear_tarjeta("Buenas (Tn)", f"{df_dia[c_efec].values[0]:,.2f}", "#607D8B")
            with d2: crear_tarjeta("Consumo (Tn)", f"{df_dia[c_cons].values[0]:,.2f}", "#607D8B")
            with d3: crear_tarjeta("Mala (Kg)", f"{df_dia[c_mala].values[0]:,.2f}", "#607D8B")
            with d4: crear_tarjeta("Rebaba (Kg)", f"{df_dia[c_reba].values[0]:,.2f}", "#607D8B")
            # El Desperdicio en % como en tu imagen
            valor_desp = df_dia[c_desp].values[0] if c_desp else 0
            with d5: crear_tarjeta("Desperdicio", f"{valor_desp * 100:,.2f}" if valor_desp < 1 else f"{valor_desp:,.2f}", "#D32F2F", "%")

else:
    st.info("👋 Sube el archivo Excel para ver el Dashboard restaurado.")