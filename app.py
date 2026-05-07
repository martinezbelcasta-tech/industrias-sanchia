import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image

# 1. CONFIGURACIÓN DE LA APP
st.set_page_config(page_title="Industrias Sanchia - Sistema Integral", layout="wide")

# --- ENCABEZADO ---
col_l, col_t = st.columns([1, 5])
with col_l:
    try:
        img = Image.open('logo tipo industrias.jpg')
        st.image(img, width=130)
    except:
        st.write("🏭")

with col_t:
    st.markdown("<h1>Industrias Sanchia</h1>", unsafe_allow_html=True)

st.divider()

# --- MENÚ DE NAVEGACIÓN ---
st.sidebar.title("🚀 Menú Principal")
pagina = st.sidebar.radio("Ir a:", ["📊 Dashboard General", "🗑️ Análisis de Desperdicios"])

st.sidebar.divider()

# --- CONFIGURACIÓN DE PERIODO ---
st.sidebar.header("📅 Configuración de Periodo")
meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
mes_sel = st.sidebar.selectbox("Selecciona el Mes:", meses, index=4)
año_sel = st.sidebar.number_input("Selecciona el Año:", min_value=2024, max_value=2030, value=2026)
dias_proyeccion = st.sidebar.slider(f"Días a proyectar ({mes_sel}):", 1, 31, 31)

# --- CARGA DE DATOS ---
archivo = st.file_uploader("Sube tu archivo 'Data app.xlsx'", type=["xlsx"])

if archivo is not None:
    df = pd.read_excel(archivo)
    df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0])
    df_activos = df[df.iloc[:, 1] > 0].copy()
    n_dias = len(df_activos)

    # --- PÁGINA 1: DASHBOARD GENERAL ---
    if pagina == "📊 Dashboard General":
        st.header(f"Resumen General - {mes_sel} {año_sel}")
        
        # Cálculos
        t_efec = df.iloc[:, 1].sum()
        t_mala = df.iloc[:, 2].sum()
        t_reba = df.iloc[:, 3].sum()
        t_cons = df.iloc[:, 4].sum()

        if n_dias > 0:
            p_efec, p_cons = t_efec / n_dias, t_cons / n_dias
            p_mala, p_reba = t_mala / n_dias, t_reba / n_dias
            pr_efec, pr_cons = p_efec * dias_proyeccion, p_cons * dias_proyeccion
            pr_mala, pr_reba = p_mala * dias_proyeccion, p_reba * dias_proyeccion
        else:
            pr_efec = pr_cons = pr_mala = pr_reba = p_efec = p_cons = p_mala = p_reba = 0

        # BLOQUE 1: PROYECCIONES
        st.subheader("📈 Proyecciones al Cierre")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("PROY. EFECTIVAS (Tn)", f"{pr_efec:,.2f}")
        c2.metric("PROY. CONSUMO (Tn)", f"{pr_cons:,.2f}")
        c3.metric("PROY. PIEZA MALA (Kg)", f"{pr_mala:,.2f}")
        c4.metric("PROY. REBABA (Kg)", f"{pr_reba:,.2f}")
        
        st.divider()

        # BLOQUE 2: PROMEDIOS
        st.subheader("📊 Rendimiento Diario Promedio")
        p1, p2, p3, p4 = st.columns(4)
        p1.metric("Prom. Efectivas", f"{p_efec:,.2f} Tn/d")
        p2.metric("Prom. Consumo", f"{p_cons:,.2f} Tn/d")
        p3.metric("Prom. Pieza Mala", f"{p_mala:,.2f} Kg/d")
        p4.metric("Prom. Rebaba", f"{p_reba:,.2f} Kg/d")

        st.divider()

        # BLOQUE 3: TOTALES ACUMULADOS (RECUPERADOS)
        st.subheader(f"📁 Real Acumulado {mes_sel}")
        a1, a2, a3, a4 = st.columns(4)
        a1.metric("Total Efectivas", f"{t_efec:,.2f} Tn")
        a2.metric("Total Consumo", f"{t_cons:,.2f} Tn")
        a3.metric("Total Mala", f"{t_mala:,.2f} Kg")
        a4.metric("Total Rebaba", f"{t_reba:,.2f} Kg")

        st.divider()

        # BLOQUE 4: CONSULTA POR FECHA
        st.subheader("📅 Detalle por Fecha")
        df['Fecha_Txt'] = df.iloc[:, 0].dt.strftime('%Y-%m-%d')
        dia_sel = st.selectbox("Selecciona una fecha:", df['Fecha_Txt'].unique())
        f = df[df['Fecha_Txt'] == dia_sel].iloc[0]
        d1, d2, d3, d4, d5 = st.columns(5)
        d1.metric("Buenas (Tn)", f"{f.iloc[1]:,.2f}")
        d2.metric("Consumo (Tn)", f"{f.iloc[4]:,.2f}")
        d3.metric("Mala (Kg)", f"{f.iloc[2]:,.2f}")
        d4.metric("Rebaba (Kg)", f"{f.iloc[3]:,.2f}")
        val_p = f.iloc[5] * 100 if f.iloc[5] < 1 else f.iloc[5]
        d5.metric("Desperdicio", f"{val_p:,.2f}%")

    # --- PÁGINA 2: ANÁLISIS DE DESPERDICIOS ---
    elif pagina == "🗑️ Análisis de Desperdicios":
        st.header(f"🗑️ Análisis de Desperdicios - {mes_sel}")
        st.info("¡Sección lista para tus instrucciones!")
        # Aquí empezaremos a trabajar los detalles de desperdicio que me digas

else:
    st.info(f"Sube el archivo para iniciar Industrias Sanchia.")