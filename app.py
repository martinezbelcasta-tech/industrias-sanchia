import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. CONFIGURACIÓN Y ESTILOS
st.set_page_config(page_title="Sanchia Dashboard Premium", layout="wide")

NOMBRE_ARCHIVO = "Data app.xlsx"

def cargar_datos():
    try:
        df = pd.read_excel(NOMBRE_ARCHIVO)
        df.columns = [str(c).strip().upper() for c in df.columns]
        return df, True
    except FileNotFoundError:
        return None, False

# Función para mostrar tarjetas
def crear_tarjeta(titulo, valor, color_borde, unidad=""):
    st.markdown(f"""
        <div style="background-color: #ffffff; padding: 15px; border-radius: 10px; border-left: 6px solid {color_borde}; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); margin-bottom: 15px;">
            <p style="margin:0; font-size: 13px; color: #666; font-weight: bold; text-transform: uppercase;">{titulo}</p>
            <p style="margin:0; font-size: 28px; font-weight: bold; color: {color_borde};">{valor} <span style="font-size:14px;">{unidad}</span></p>
        </div>
    """, unsafe_allow_html=True)

st.image("logo tipo industrias.jpg", width=200)
st.markdown("---")

# 2. CARGA DE DATOS AUTOMÁTICA
st.sidebar.title("Menú Principal")
pagina = st.sidebar.radio("Ir a:", ["📈 Dashboard General", "🗑️ Análisis de Desperdicios", "⚙️ Análisis de Eficiencia"])

df, archivo_encontrado = cargar_datos()

if archivo_encontrado:
    st.sidebar.success(f"✓ {NOMBRE_ARCHIVO} cargado")
    st.sidebar.info(f"Última modificación: {datetime.fromtimestamp(__import__('os').path.getmtime(NOMBRE_ARCHIVO)).strftime('%d/%m/%Y %H:%M:%S')}")
    
    if st.sidebar.button("🔄 Actualizar datos"):
        st.rerun()

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
    c_supervisor = buscar_col(["SUPERVISOR", "SUPERV"])
    c_cant_desp = buscar_col(["CANTIDAD GENERADA", "GENERADA"])

    if c_fecha:
        df[c_fecha] = pd.to_datetime(df[c_fecha])
        meses_dict = {1:"Enero", 2:"Febrero", 3:"Marzo", 4:"Abril", 5:"Mayo", 6:"Junio",
                      7:"Julio", 8:"Agosto", 9:"Septiembre", 10:"Octubre", 11:"Noviembre", 12:"Diciembre"}
        df["MES_NOMBRE"] = df[c_fecha].dt.month.map(meses_dict)
        df["AÑO"] = df[c_fecha].dt.year
        st.sidebar.markdown("---")
        años_disponibles = list(range(2026, 2101))
        año_sel = st.sidebar.selectbox("Selecciona el Año:", años_disponibles)
        df_filtrado = df[df["AÑO"] == año_sel].copy()
        meses_disponibles = ["Todos"] + list(meses_dict.values())
        mes_sel = st.sidebar.selectbox("Selecciona el Mes:", meses_disponibles)
        if mes_sel != "Todos":
            df_filtrado = df_filtrado[df_filtrado["MES_NOMBRE"] == mes_sel].copy()
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
            fig = px.bar(df_plot, x=c_fecha, y=vars_sel, barmode="group")
            fig.update_traces(textfont_size=26, textposition="outside", cliponaxis=False, texttemplate="%{y:,.2f}")
            fig.update_layout(
                height=800,
                margin=dict(t=50, b=0),
                font=dict(size=18),
                xaxis=dict(title_font=dict(size=20), tickfont=dict(size=16)),
                yaxis=dict(title_font=dict(size=20), tickfont=dict(size=16)),
                hoverlabel=dict(font_size=20, font_family="Arial")
            )
            st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True, "displayModeBar": True, "doubleClick": "reset", "modeBarButtonsToAdd": ["drawline", "drawopenpath", "eraseshape"]})

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

    elif pagina == "🗑️ Análisis de Desperdicios" and not df_filtrado.empty:
        st.subheader("🗑️ Análisis de Desperdicios por Supervisor")
        df_con_datos = df_filtrado.dropna(subset=[c_fecha])
        dias_procesados = len(df_con_datos)
        st.info(f"📢 Desperdicio Generado en {dias_procesados} días procesados")

        if c_supervisor and c_cant_desp:
            df_desp = df_filtrado.groupby(c_supervisor)[c_cant_desp].sum().reset_index()
            df_desp = df_desp.sort_values(c_cant_desp, ascending=False)

            st.markdown("### 📊 Toneladas de Desperdicio por Supervisor")
            fig_desp = px.bar(df_desp, x=c_supervisor, y=c_cant_desp, text_auto=',.2f', color=c_cant_desp,
                              color_continuous_scale="Reds", labels={c_cant_desp: "Toneladas (Tn)"})
            fig_desp.update_traces(textfont_size=24, textposition="outside")
            fig_desp.update_layout(
                height=600,
                font=dict(size=18),
                xaxis=dict(title_font=dict(size=20), tickfont=dict(size=16)),
                yaxis=dict(title_font=dict(size=20), tickfont=dict(size=16)),
                hoverlabel=dict(font_size=18)
            )
            st.plotly_chart(fig_desp, use_container_width=True)

            st.markdown("### 📋 Detalle por Supervisor (Toneladas)")
            df_desp_tabla = df_desp.copy()
            df_desp_tabla["Tn"] = df_desp_tabla[c_cant_desp].apply(lambda x: f"{x:,.2f}")
            df_desp_tabla = df_desp_tabla.drop(columns=[c_cant_desp]).rename(columns={"Tn": c_cant_desp})
            st.dataframe(df_desp_tabla, use_container_width=True)

            supervisor_top = df_desp.iloc[0][c_supervisor] if not df_desp.empty else "N/A"
            cantidad_top = df_desp.iloc[0][c_cant_desp] if not df_desp.empty else 0
            st.success(f"😢 El supervisor con más desperdicio es: **{supervisor_top}** con **{cantidad_top:,.2f} Tn**")
        else:
            st.warning("⚠️ No se encontraron las columnas de supervisor o cantidad de desperdicio en el Excel")

    elif pagina == "⚙️ Análisis de Eficiencia" and not df_filtrado.empty:
        st.subheader("⚙️ Análisis de Eficiencia de Máquinas")
        st.info("📌 Esta sección analiza el rendimiento de las máquinas basándose en los datos del Excel")

        c_maquina = buscar_col(["MAQUINA", "MÁQUINA", "MAQ"])
        c_eficiencia = buscar_col(["EFICIENCIA", "RENDIMIENTO", "%"])

        if c_maquina and c_eficiencia:
            df_ef = df_filtrado.dropna(subset=[c_maquina, c_eficiencia])
            
            if not df_ef.empty:
                df_maq = df_ef.groupby(c_maquina)[c_eficiencia].mean().reset_index()
                df_maq = df_maq.sort_values(c_eficiencia, ascending=False)

                col_ef1, col_ef2 = st.columns(2)

                with col_ef1:
                    st.markdown("### 🏆 Top 6 Máquinas con Mejor Eficiencia")
                    df_mejor = df_maq.head(6)
                    fig_mejor = px.bar(df_mejor, x=c_eficiencia, y=c_maquina, orientation='h',
                                      text_auto='.1f', color=c_eficiencia, color_continuous_scale="Greens")
                    fig_mejor.update_traces(textfont_size=16)
                    fig_mejor.update_layout(height=400, font=dict(size=14))
                    st.plotly_chart(fig_mejor, use_container_width=True)

                with col_ef2:
                    st.markdown("### ⚠️ Top 10 Máquinas con Peor Eficiencia")
                    df_peor = df_maq.tail(10).sort_values(c_eficiencia)
                    fig_peor = px.bar(df_peor, x=c_eficiencia, y=c_maquina, orientation='h',
                                     text_auto='.1f', color=c_eficiencia, color_continuous_scale="Reds")
                    fig_peor.update_traces(textfont_size=16)
                    fig_peor.update_layout(height=400, font=dict(size=14))
                    st.plotly_chart(fig_peor, use_container_width=True)

                st.markdown("### 📋 Tabla Completa de Eficiencia")
                df_tabla_ef = df_maq.copy()
                df_tabla_ef["EFICIENCIA %"] = df_tabla_ef[c_eficiencia].apply(lambda x: f"{x:.2f}%")
                df_tabla_ef = df_tabla_ef.drop(columns=[c_eficiencia]).rename(columns={"EFICIENCIA %": c_eficiencia})
                st.dataframe(df_tabla_ef, use_container_width=True)
            else:
                st.warning("⚠️ No hay datos suficientes para analizar eficiencia")
        else:
            st.warning("⚠️ Para usar esta sección necesitas agregar al Excel las columnas: MAQUINA y EFICIENCIA")
            st.markdown("""
            ### 📝 Estructura esperada en Excel:
            | FECHA | MAQUINA | TON EFECTIVAS | PIEZA MALA KG | REBABA KG | ... | EFICIENCIA |
            |-------|---------|---------------|---------------|-----------|-----|-------------|
            |2026-05-01| MAQ-01 | 1500 | 50 | 30 | ... | 85.5% |
            """)
            st.markdown("### 🎨 Vista Previa (Datos de Ejemplo)")
            
            import numpy as np
            np.random.seed(42)
            ejemplo = pd.DataFrame({
                "MÁQUINA": [f"MAQ-{i:02d}" for i in range(1, 21)],
                "EFICIENCIA (%)": np.random.uniform(70, 98, 20)
            })
            ejemplo = ejemplo.sort_values("EFICIENCIA (%)", ascending=False)
            
            col_prev1, col_prev2 = st.columns(2)
            with col_prev1:
                st.markdown("#### 🏆 Top 6 Mejor Eficiencia")
                st.dataframe(ejemplo.head(6), use_container_width=True)
            with col_prev2:
                st.markdown("#### ⚠️ Top 10 Peor Eficiencia")
                st.dataframe(ejemplo.tail(10).sort_values("EFICIENCIA (%)"), use_container_width=True)

    else:
        st.error(f"⚠️ No se encontró el archivo **{NOMBRE_ARCHIVO}** en la carpeta del proyecto.")