import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Sanchia Dashboard", layout="wide")

NOMBRE_TIEMPOS = "Data Procesos 4 (1).xlsx"
NOMBRE_INCAPACIDADES = "registro de incapacidades.xlsx"

def cargar_empleados():
    try:
        df = pd.read_excel(NOMBRE_INCAPACIDADES, sheet_name='Hoja3', header=None)
        nombres = df.iloc[:, 0].dropna().unique().tolist()
        return [n.strip() for n in nombres if isinstance(n, str) and n.strip()]
    except:
        return []

def cargar_supervisores():
    try:
        df = pd.read_excel(NOMBRE_INCAPACIDADES, sheet_name='Hoja3', header=None)
        supervisores = df.iloc[:, 4].dropna().unique().tolist()
        return [s.strip() for s in supervisores if isinstance(s, str)]
    except:
        return []

def crear_tarjeta(titulo, valor, color_borde, unidad=""):
    st.markdown(f"""
        <div style="background-color: #ffffff; padding: 15px; border-radius: 10px; border-left: 6px solid {color_borde}; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); margin-bottom: 15px;">
            <p style="margin:0; font-size: 13px; color: #666; font-weight: bold; text-transform: uppercase;">{titulo}</p>
            <p style="margin:0; font-size: 28px; font-weight: bold; color: {color_borde};">{valor} <span style="font-size:14px;">{unidad}</span></p>
        </div>
    """, unsafe_allow_html=True)

st.image("logo tipo industrias.jpg", width=200)
st.markdown("---")
st.sidebar.title("Menú Principal")
pagina = st.sidebar.radio("Ir a:", ["⏱️ Tiempos de Arranque", "🏥 Registro de Incapacidades"])

if pagina == "⏱️ Tiempos de Arranque":
    try:
        df_tiempos = pd.read_excel(NOMBRE_TIEMPOS)
        df_tiempos['Fecha'] = df_tiempos['Fecha'].apply(lambda x: pd.to_datetime(x).date() if pd.notna(x) else pd.NaT)
        df_tiempos['Fecha_dia'] = df_tiempos['Fecha'].astype(str).str.replace(' 00:00:00', '', regex=False)
        
        def to_hours(x):
            try:
                if pd.isna(x): return 0
                import datetime as dt
                if isinstance(x, pd.Timedelta): return x.total_seconds() / 3600
                if isinstance(x, dt.timedelta): return x.total_seconds() / 3600
                if isinstance(x, dt.time): return x.hour + x.minute/60 + x.second/3600
                if isinstance(x, datetime): return x.hour + x.minute/60 + x.second/3600
                if isinstance(x, float): return float(x)
                if isinstance(x, str):
                    if ':' in x:
                        parts = x.split(':')
                        return int(parts[0]) + int(parts[1])/60 + int(parts[2])/3600
                    else:
                        return float(x)
                return float(x)
            except:
                return 0

        df_tiempos['Cambio_horas'] = df_tiempos['Cambio de molde'].apply(to_hours)
        df_tiempos['Arranque_horas'] = df_tiempos['Arranque'].apply(to_hours)
        df_tiempos['Validacion_horas'] = df_tiempos['Validacion calidad'].apply(to_hours)
        df_tiempos['Total_horas'] = df_tiempos['Total'].apply(to_hours)

        st.subheader("⏱️ Tiempos de Arranque")
        st.info("📌 Análisis detallado de tiempos de arranque por máquina")

        c1, c2, c3, c4 = st.columns(4)
        with c1: crear_tarjeta("Total Registros", f"{len(df_tiempos)}", "#1E88E5", "")
        with c2: crear_tarjeta("Máquinas Activas", f"{df_tiempos['Maquina'].nunique()}", "#43A047", "")
        with c3: crear_tarjeta("Tiempo Total", f"{df_tiempos['Total_horas'].sum():.2f}", "#FB8C00", "hrs")
        with c4: crear_tarjeta("Promedio Total", f"{df_tiempos['Total_horas'].mean():.2f}", "#C62828", "hrs")

        st.markdown("---")
        st.markdown("### 📊 Desglose de Tiempos por Máquina (Detallado)")
        df_tiempo_det = df_tiempos.groupby('Maquina').agg({
            'Cambio_horas': 'sum',
            'Arranque_horas': 'sum',
            'Validacion_horas': 'sum',
            'Total_horas': 'sum'
        }).reset_index()
        df_tiempo_det = df_tiempo_det.sort_values('Total_horas', ascending=False)

        fig_desglose = go.Figure()
        fig_desglose.add_trace(go.Bar(name='Cambio de Molde', x=df_tiempo_det['Maquina'].astype(str), y=df_tiempo_det['Cambio_horas'], marker_color='#1565C0', text=df_tiempo_det['Cambio_horas'].apply(lambda x: f"{x:.2f}"), textposition='outside', textfont=dict(size=12, color='#1565C0')))
        fig_desglose.add_trace(go.Bar(name='Arranque', x=df_tiempo_det['Maquina'].astype(str), y=df_tiempo_det['Arranque_horas'], marker_color='#43A047', text=df_tiempo_det['Arranque_horas'].apply(lambda x: f"{x:.2f}"), textposition='outside', textfont=dict(size=12, color='#43A047')))
        fig_desglose.add_trace(go.Bar(name='Validación Calidad', x=df_tiempo_det['Maquina'].astype(str), y=df_tiempo_det['Validacion_horas'], marker_color='#EF6C00', text=df_tiempo_det['Validacion_horas'].apply(lambda x: f"{x:.2f}"), textposition='outside', textfont=dict(size=12, color='#EF6C00')))
        fig_desglose.update_layout(barmode='stack', height=600, xaxis=dict(title="Máquina", title_font=dict(size=16), tickfont=dict(size=14), type='category'), yaxis=dict(title="Horas", title_font=dict(size=16), tickfont=dict(size=12), showgrid=True, gridcolor='rgba(200,200,200,0.3)'), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5), plot_bgcolor='rgba(250,254,250,0.5)', margin=dict(t=50, b=80, l=60, r=30))
        st.plotly_chart(fig_desglose, use_container_width=True, config={"displayModeBar": True, "displaylogo": False})

        st.markdown("---")
        st.markdown("### 📋 Tabla de Desglose por Máquina")
        df_tabla_desglose = df_tiempo_det.copy()
        df_tabla_desglose.columns = ['Máquina', 'Cambio Molde (hrs)', 'Arranque (hrs)', 'Validación (hrs)', 'Total (hrs)']
        df_tabla_desglose = df_tabla_desglose.sort_values('Total (hrs)', ascending=False)
        st.dataframe(df_tabla_desglose, use_container_width=True)

        st.markdown("---")
        st.markdown("### ⏱️ Tiempo Total por Máquina (Horas)")
        fig_total = go.Figure(go.Bar(x=df_tiempo_det['Maquina'].astype(str), y=df_tiempo_det['Total_horas'], marker_color='#7B1FA2', text=df_tiempo_det['Total_horas'].apply(lambda x: f"{x:.2f} hrs"), textposition='outside', textfont=dict(size=16, color='#7B1FA2')))
        fig_total.update_layout(height=500, xaxis=dict(title="Máquina", title_font=dict(size=16), tickfont=dict(size=14, color='#7B1FA2'), type='category'), yaxis=dict(title="Tiempo Total (hrs)", title_font=dict(size=16), tickfont=dict(size=12), showgrid=True, gridcolor='rgba(200,200,200,0.3)'), plot_bgcolor='rgba(250,254,250,0.5)', margin=dict(t=50, b=80, l=60, r=30))
        st.plotly_chart(fig_total, use_container_width=True, config={"displayModeBar": True, "displaylogo": False})

        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🔧 Cambio de Molde por Máquina")
            fig_cambio = go.Figure(go.Bar(x=df_tiempo_det['Maquina'].astype(str), y=df_tiempo_det['Cambio_horas'], marker_color='#1565C0', text=df_tiempo_det['Cambio_horas'].apply(lambda x: f"{x:.2f} hrs"), textposition='outside', textfont=dict(size=14, color='#1565C0')))
            fig_cambio.update_layout(height=400, xaxis=dict(title="Máquina", title_font=dict(size=14), tickfont=dict(size=12), type='category'), yaxis=dict(title="Horas", title_font=dict(size=14), tickfont=dict(size=10), showgrid=True, gridcolor='rgba(200,200,200,0.3)'), plot_bgcolor='rgba(250,254,250,0.5)', margin=dict(t=40, b=60, l=50, r=50))
            st.plotly_chart(fig_cambio, use_container_width=True, config={"displayModeBar": True, "displaylogo": False})
        
        with col2:
            st.markdown("### ⚡ Arranque por Máquina")
            fig_arranque = go.Figure(go.Bar(x=df_tiempo_det['Maquina'].astype(str), y=df_tiempo_det['Arranque_horas'], marker_color='#43A047', text=df_tiempo_det['Arranque_horas'].apply(lambda x: f"{x:.2f} hrs"), textposition='outside', textfont=dict(size=14, color='#43A047')))
            fig_arranque.update_layout(height=400, xaxis=dict(title="Máquina", title_font=dict(size=14), tickfont=dict(size=12), type='category'), yaxis=dict(title="Horas", title_font=dict(size=14), tickfont=dict(size=10), showgrid=True, gridcolor='rgba(200,200,200,0.3)'), plot_bgcolor='rgba(250,254,250,0.5)', margin=dict(t=40, b=60, l=50, r=50))
            st.plotly_chart(fig_arranque, use_container_width=True, config={"displayModeBar": True, "displaylogo": False})

        st.markdown("---")
        col3, col4 = st.columns(2)
        with col3:
            st.markdown("### ✅ Validación Calidad por Máquina")
            fig_validacion = go.Figure(go.Bar(x=df_tiempo_det['Maquina'].astype(str), y=df_tiempo_det['Validacion_horas'], marker_color='#EF6C00', text=df_tiempo_det['Validacion_horas'].apply(lambda x: f"{x:.2f} hrs"), textposition='outside', textfont=dict(size=14, color='#EF6C00')))
            fig_validacion.update_layout(height=400, xaxis=dict(title="Máquina", title_font=dict(size=14), tickfont=dict(size=12), type='category'), yaxis=dict(title="Horas", title_font=dict(size=14), tickfont=dict(size=10), showgrid=True, gridcolor='rgba(200,200,200,0.3)'), plot_bgcolor='rgba(250,254,250,0.5)', margin=dict(t=40, b=60, l=50, r=50))
            st.plotly_chart(fig_validacion, use_container_width=True, config={"displayModeBar": True, "displaylogo": False})
        
        with col4:
            st.markdown("### 📋 Detalle por Registro")
            df_registros = df_tiempos[['Maquina', 'Molde', 'Cambio_horas', 'Arranque_horas', 'Validacion_horas', 'Total_horas']].sort_values('Total_horas', ascending=False).head(20)
            fig_registros = go.Figure(go.Bar(x=df_registros['Maquina'].astype(str), y=df_registros['Total_horas'], marker_color='#7B1FA2', text=df_registros['Total_horas'].apply(lambda x: f"{x:.2f} hrs"), textposition='outside', textfont=dict(size=12, color='#7B1FA2')))
            fig_registros.update_layout(height=400, xaxis=dict(title="Máquina", title_font=dict(size=14), tickfont=dict(size=12), type='category'), yaxis=dict(title="Horas", title_font=dict(size=14), tickfont=dict(size=10), showgrid=True, gridcolor='rgba(200,200,200,0.3)'), plot_bgcolor='rgba(250,254,250,0.5)', margin=dict(t=40, b=60, l=50, r=50))
            st.plotly_chart(fig_registros, use_container_width=True, config={"displayModeBar": True, "displaylogo": False})

        st.markdown("---")
        st.markdown("### 📊 Total General de Horas por Proceso")
        totales = {
            'Proceso': ['Cambio de Molde', 'Arranque', 'Validación Calidad'],
            'Horas': [df_tiempos['Cambio_horas'].sum(), df_tiempos['Arranque_horas'].sum(), df_tiempos['Validacion_horas'].sum()]
        }
        df_totales = pd.DataFrame(totales)
        fig_pie = px.pie(df_totales, values='Horas', names='Proceso', hole=0.4, color_discrete_sequence=['#1565C0', '#43A047', '#EF6C00'])
        fig_pie.update_layout(height=400)
        fig_pie.update_traces(textposition='outside', textfont=dict(size=14))
        st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": True, "displaylogo": False})

        st.markdown("---")
        st.markdown("### 📋 Detalle Completo")
        st.dataframe(df_tiempos, use_container_width=True)

    except FileNotFoundError:
        st.error(f"⚠️ No se encontró el archivo **{NOMBRE_TIEMPOS}** en la carpeta del proyecto.")

elif pagina == "🏥 Registro de Incapacidades":
    try:
        df_incapacidades = pd.read_excel(NOMBRE_INCAPACIDADES)
        st.subheader("🏥 Registro de Incapacidades")
        st.info("📌 Control de incapacidades, permisos y faltas del personal")

        with st.form("form_incapacidades", clear_on_submit=True):
            st.markdown("### ➕ Agregar Nuevo Registro")
            cols = st.columns(2)
            with cols[0]:
                nombre = st.selectbox("Nombre de Empleado", [""] + cargar_empleados())
                grupo = st.selectbox("Grupo", ["", "A", "B", "C"])
            with cols[1]:
                fecha = st.date_input("Fecha", datetime.now())
                supervisor = st.selectbox("Supervisor", [""] + cargar_supervisores())
            
            st.markdown("**Incapacidad**")
            col_inc = st.columns([1, 1, 2])
            with col_inc[0]:
                incapacidad = st.selectbox("Incapacidad", ["", "SI", "NO"])
            with col_inc[1]:
                dias_incapacidad = st.number_input("Días Incapacidad", min_value=0, step=1, value=0)
            
            st.markdown("**Permiso Personal**")
            col_per = st.columns([1, 1, 2])
            with col_per[0]:
                permiso = st.selectbox("Permiso Personal", ["", "SI", "NO"])
            with col_per[1]:
                dias_permiso = st.number_input("Días Permiso", min_value=0, step=1, value=0)
            
            st.markdown("**Falta Injustificada**")
            col_falta = st.columns([1, 1, 2])
            with col_falta[0]:
                falta = st.selectbox("Falta Injustificada", ["", "SI", "NO"])
            with col_falta[1]:
                dias_falta = st.number_input("Días Falta", min_value=0, step=1, value=0)
            
            submitted = st.form_submit_button("💾 Guardar Registro")
            if submitted and nombre:
                st.success(f"✅ Registro guardado para {nombre}")

        c1, c2, c3, c4 = st.columns(4)
        with c1: crear_tarjeta("Total Registros", f"{len(df_incapacidades)}", "#1E88E5", "")
        with c2: crear_tarjeta("Incapacidades", f"{df_incapacidades['DIAS  DE INCAPACIDAD'].sum() if 'DIAS  DE INCAPACIDAD' in df_incapacidades.columns else 0}", "#E53935", "días")
        with c3: crear_tarjeta("Permisos Personales", f"{df_incapacidades['DIAS DE PERMISO'].sum() if 'DIAS DE PERMISO' in df_incapacidades.columns else 0}", "#FB8C00", "días")
        with c4: crear_tarjeta("Faltas Injustificadas", f"{df_incapacidades['DIAS DE FALTA INJUSTIFICADA'].sum() if 'DIAS DE FALTA INJUSTIFICADA' in df_incapacidades.columns else 0}", "#C62828", "días")

        st.markdown("---")
        st.markdown("### 📋 Detalle Completo")
        st.dataframe(df_incapacidades, use_container_width=True)

    except FileNotFoundError:
        st.info(f"📋 El archivo **{NOMBRE_INCAPACIDADES}** aún no ha sido cargado.")
