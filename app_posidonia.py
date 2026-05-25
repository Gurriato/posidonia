import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

# Configuración de la página web de la aplicación
st.set_page_config(page_title="Propuesta Pliego: Sistema Posidonia", layout="wide", initial_sidebar_state="expanded")

# --- FUNCIÓN DE FORMATEO EUROPEO ---
def fmt(valor, dees=0):
    try:
        valor = float(valor)
    except (ValueError, TypeError):
        return valor
    s = f"{valor:,.{dees}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")

# --- PANTALLA PRINCIPAL: SISTEMA DE PESTAÑAS ---
tab1, tab2 = st.tabs(["📄 Propuesta Formal RFP & Gantt", "📊 Simulador Financiero & ROI"])

# =========================================================================
# PESTAÑA 1: PROPUESTA FORMAL ADAPTADA A LA ESTRUCTURA RFP REQUESTED
# =========================================================================
with tab1:
    st.title("💼 Memoria Técnica y Administrativa: Respuesta a la RFP")
    st.markdown("**Destinatario:** Govern de les Illes Balears - Conselleria d'Agricultura, Pesca i Medi Natural")
    st.write("Servicio Llave en Mano (DaaS) de Inspección y Alertas de Fondeo Ilegal mediante Inteligencia Artificial")
    
    st.divider()
    
    # 1. RESUMEN EJECUTIVO
    st.header("1. Resumen Ejecutivo (Executive Summary)")
    st.markdown("""
    La presente propuesta tecnológica responde a la necesidad crítica de proteger de manera eficiente y escalable las praderas de *Posidonia oceanica* en el archipiélago balear, iniciando con una fase piloto optimizada en la isla de Formentera. 
    
    Nuestra solución cambia el paradigma de la vigilancia marina: eliminamos el patrullaje analógico y ciego mediante embarcaciones tripuladas y lo sustituimos por un sistema de **interceptación quirúrgica automatizada**. Combinando cámaras de análisis costero continuo, intersección geoespacial (GIS) y estaciones de drones autónomos (*Drone-in-a-Box*), el sistema solo actúa cuando se detecta una infracción probable, minimizando costes operativos y garantizando evidencias legales irrefutables con impacto ambiental inmediato.
    """)
    
    # 2. INFORMACIÓN Y CONTEXTO DE LA EMPRESA
    st.header("2. Información y Contexto de la Empresa")
    st.markdown("""
    Somos una compañía de base tecnológica de nueva creación (S.L.) especializada en ingeniería de automatización y soluciones de impacto ambiental (*Green-Tech*). Nuestra estructura corporativa ágil está integrada por un equipo interdisciplinar de **tres profesionales especialistas**, cuyo equilibrio competencial minimiza el riesgo de ejecución del proyecto:
    
    * **Dirección de Inteligencia Artificial & Sistemas:** Ingeniero especialista en el diseño de modelos de visión artificial, encargado de la arquitectura de la red neural, el pipeline de procesamiento de datos y la homografía matemática de las cámaras de costa.
    * **Dirección de Arquitectura de Datos & Big Data:** Ingeniera de origen colombiano especialista en el modelado, optimización y securización de bases de datos masivas geoespaciales (GIS) y sincronización cloud en tiempo real. Su incorporación aporta el perfil de diversidad clave para el acceso prioritario a fondos tecnológicos europeos de discriminación positiva (*Women TechEU*).
    * **Dirección Legal, Regulación & Riesgos:** Abogado especialista en derecho aeronáutico y gestión de riesgos operativos, encargado del desarrollo de los estudios de seguridad aeronáutica SORA, interlocución con AESA y el blindaje legal de las evidencias capturadas para su validez en los expedientes sancionadores.
    """)
    
    st.divider()

    # 3. ALCANCE DEL PROYECTO Y REQUISITOS TÉCNICOS
    st.header("3. Alcance del Proyecto y Requisitos Técnico (Scope of Work)")
    
    col_scope1, col_scope2 = st.columns(2)
    with col_scope1:
        st.markdown("**Objetivos Específicos & Entregables:**")
        st.markdown("""
        * **Despliegue del 'Filtro 0' (Vigilancia Pasiva):** Instalación de cámaras ópticas PTZ industriales en zonas urbanas no protegidas con visibilidad directa sobre las zonas de fondeo.
        * **Módulos de Software Core:** Licenciamiento de la plataforma cloud de procesamiento de imágenes con algoritmos de OCR (lectura de matrículas) e intersección de mapas de calor GIS de posidonia de la CAIB.
        * **Infraestructura de Interceptación:** Despliegue de estaciones automatizadas **DJI Dock 2** con aeronaves **Matrice 3D** equipadas con filtros polarizadores circulares (CPL) para anular el reflejo solar y capturar imágenes cenitales del fondo marino en la ventana crítica de 11:00 a 16:00.
        """)
    with col_scope2:
        st.markdown("**Limitaciones (Fuera de Alcance):**")
        st.markdown("""
        * La S.L. aporta la evidencia digital y la georreferenciación inversa del barco; la emisión física de la sanción económica es competencia exclusiva de la administración pública.
        * Queda excluida de la fase de pruebas la operación en condiciones meteorológicas extremas que superen los límites estructurales del hardware (vientos superiores a 12 m/s).
        """)

    st.subheader("🖥️ Arquitectura Lógica de la Solución")
    st.markdown("""
    ```text
    ┌────────────────────────┐      ┌─────────────────────────┐      ┌─────────────────────────┐
    │  CÁMARA COSTA (PTZ)    │ ───> │ IA: VISIÓN COMPUTACIONAL│ ───> │   HOMOGRAFÍA ÓPTICA     │
    │  Vigilancia Pasiva 24/7│      │ Detección de Embarcación│      │ Cálculo Coordenada GPS  │
    └────────────────────────┘      └─────────────────────────┘      └─────────────────────────┘
                                                                                  │
    ┌────────────────────────┐      ┌─────────────────────────┐      ┌────────────▼────────────┐
    │ GENERACIÓN DE EVIDENCIA│      │    DJI DOCK 2 & DRON    │      │    CRUCE GEOSPESCIAL    │
    │ Foto Cenital Ancla+CPL │ <─── │ Despegue Automático API │ <─── │ Point-in-Polygon (GIS)  │
    │  Zoom de Matrícula 56x │      │  Misión en Línea Recta  │      │  Match sobre Posidonia  │
    └────────────────────────┘      └─────────────────────────┘      └─────────────────────────┘
    ```
    """)

    st.divider()

    # 4. CRONOGRAMA DEL PROCESO DE SELECCIÓN (PLIEGO PROPUESTO)
    st.header("4. Cronograma del Proceso de Selección")
    st.write("Fechas marco propuestas para la licitación estacional con vistas a la campaña de 2027:")
    
    cronograma_data = {
        "Hito / Fase": ["Lanzamiento de la RFP / Pliego", "Fecha límite para preguntas técnicas", "Publicación de respuestas a aclaraciones", "Entrega improrrogable de propuestas", "Fase de evaluación y demos de IA", "Adjudicación definitiva del contrato"],
        "Descripción": ["Apertura oficial de la licitación por el Govern", "Periodo para resolver dudas de conectividad y GIS", "Aclaraciones publicadas en el perfil del contratante", "Cierre de recepción de ofertas técnicas y económicas", "Validación en entorno de pruebas del algoritmo de homografía", "Firma del contrato de servicios DaaS para la campaña"],
        "Fecha Estimada": ["2026-06-01", "2026-06-15", "2026-06-22", "2026-07-15", "2026-08-01", "2026-09-01"]
    }
    st.table(pd.DataFrame(cronograma_data))

    st.divider()

    # 5. ESTRUCTURA DE LA PROPUESTA REQUERIDA & CRONOGRAMA DINÁMICO GANTT
    st.header("5. Cronograma de Desarrollo Técnico (Backlog Editable para Gantt)")
    st.write("💡 Modifica las fechas de inicio o los días de duración en la tabla de abajo para actualizar dinámicamente el diagrama de Gantt de ingeniería.")

    # FIX: Inicialización convirtiendo los strings a datetime nativo de Pandas para que DateColumn sea compatible
    if "df_gantt_data" not in st.session_state:
        base_gantt = pd.DataFrame({
            "Fase / Tarea": [
                "Constitución S.L. e inyección Capital",
                "Tramitación NEOTEC & Women TechEU",
                "Ingeniería Aeronáutica (Manuales SORA)",
                "Desarrollo Algoritmo Homografía IA",
                "Presentación de Expediente a AESA",
                "Integración Cloud & APIs GIS CAIB",
                "Instalación Cámaras IP Costa",
                "Despliegue Físico DJI Dock 2",
                "Ensayos de Calibración Filtros CPL",
                "Auditoría Final y GO-LIVE 2027"
            ],
            "Eje Estratégico": ["Corporativo", "Financiero", "Regulatorio", "Software", "Regulatorio", "Software", "Infraestructura", "Infraestructura", "Operaciones", "Operaciones"],
            "Fecha Inicio": ["2026-06-01", "2026-06-15", "2026-07-01", "2026-08-01", "2026-10-01", "2026-11-01", "2026-11-15", "2027-01-15", "2027-03-01", "2027-04-01"],
            "Duración (Días)": [15, 60, 90, 120, 120, 60, 30, 45, 30, 15]
        })
        base_gantt["Fecha Inicio"] = pd.to_datetime(base_gantt["Fecha Inicio"])
        st.session_state.df_gantt_data = base_gantt

    # Editor de datos dinámico para el Backlog del Gantt
    edited_gantt_df = st.data_editor(
        st.session_state.df_gantt_data,
        num_rows="fixed",
        column_config={
            "Fecha Inicio": st.column_config.DateColumn("Fecha Inicio", format="YYYY-MM-DD"),
            "Duración (Días)": st.column_config.NumberColumn("Duración (Días)", format="%d días", min_value=1)
        },
        key="gantt_table_editor"
    )

    # Cálculo dinámico de fechas de fin para alimentar el gráfico de Plotly Express
    try:
        edited_gantt_df["Start"] = pd.to_datetime(edited_gantt_df["Fecha Inicio"])
        edited_gantt_df["Finish"] = edited_gantt_df.apply(lambda row: row["Start"] + timedelta(days=int(row["Duración (Días)"])), axis=1)
        
        # Renderizado del Diagrama de Gantt
        fig_gantt = px.timeline(
            edited_gantt_df,
            x_start="Start",
            x_end="Finish",
            y="Fase / Tarea",
            color="Eje Estratégico",
            title="📅 Cronograma de Ingeniería Automatizado (Camino a Abril 2027)",
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_gantt.update_yaxes(autorange="reversed")
        # FIX: Cambio de use_container_width=True por width='stretch'
        fig_gantt.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20), height=400)
        st.plotly_chart(fig_gantt, width='stretch')
    except Exception as e:
        st.error(f"Error al procesar el formato de fechas. Detalles: {e}")

    st.divider()

    # 6. CRITERIOS DE EVALUACIÓN
    st.header("6. Criterios de Baremación y Evaluación")
    st.markdown("""
    Nuestra propuesta destaca en los pliegos públicos al ofrecer las mejores métricas de eficiencia integral:
    * **Adecuación Tecnológica (40%):** Arquitectura basada en alertas pasivas que elimina el ruido innecesario de sobrevuelo constante en playas y respeta al completo el RGPD al auditar solo naves en presunta infracción.
    * **Eficiencia Económica (30%):** Reducción acreditada de más del 70% del coste operativo actual frente al uso de patrulleras neumáticas convencionales con tripulación física.
    * **Soporte Post-Implementación & SLA (20%):** Compromiso de monitorización cloud remota continua y sustitución/reparación de nodos de hardware en un plazo máximo de 24 horas durante los meses de campaña.
    * **Criterio de Impacto Sostenible (10%):** Huella de carbono cero en las misiones operativas directas al operar con vectores energéticos limpios y eléctricos (recarga en Dock).
    """)

    st.divider()

    # 7. PUNTOS DE CONTACTO Y ASPECTOS LEGALES
    st.header("7. Puntos de Contacto y Aspectos Legal")
    st.markdown("""
    * **Canal Único de Comunicación:** Para la resolución de dudas sobre la presente propuesta o el despliegue del MVP en Formentera, se centralizarán las comunicaciones en el correo técnico: `contact@posidonia-monitoring.tech`.
    * **Acuerdo de Confidencialidad (NDA):** Toda la información relativa al código de homografía, pesos de la red neural e información cartográfica propietaria está sujeta a secreto industrial estricto.
    * **Cláusula de Salvaguarda Legal:** La entrega de este documento se realiza en concepto de propuesta técnica para licitación y no constituye obligación contractual de prestación de servicios hasta la firma definitiva del pliego y formalización de la adjudicación por el órgano competente.
    """)

# =========================================================================
# PESTAÑA 2: SIMULADOR FINANCIERO (TOTALMENTE INTACTA EN LÓGICA / COREGIDO SYNTAX WIDTH)
# =========================================================================
with tab2:
    # --- 1. ENTRADA DE VARIABLES (Side-bar) ---
    st.sidebar.header("⚙️ Variables del Simulador")
    num_drones = st.sidebar.number_input("Número de Nodos (Dron + Cámara)", min_value=1, max_value=100, value=2, step=1)
    precio_estacion = st.sidebar.number_input("Precio Pliego / Temporada (€)", min_value=0, value=30000, step=1000)
    dcto_volumen = st.sidebar.number_input("Descuento Volumen (%)", min_value=0.0, max_value=100.0, value=7.0, step=0.5) / 100
    sw_base = st.sidebar.number_input("Desarrollo SW Core IA (€)", min_value=0, value=12000, step=500)
    sora_base = st.sidebar.number_input("Trámite AESA Base (€)", min_value=0, value=4500, step=500)

    # --- 2. CÁLCULO INICIAL ---
    init_hw_dron = 13500 * num_drones * (1 - dcto_volumen)
    init_hw_camara = 3500 * num_drones
    init_sw = sw_base + (500 * (num_drones - 1) if num_drones > 1 else 0)
    init_aesa = sora_base + (1000 * (num_drones - 1) if num_drones > 1 else 0)
    init_logistica = 3000 * num_drones
    init_cloud = 1200 + (1200 * num_drones)
    init_flighthub = 360 * num_drones
    init_seguro = 600 + (350 * (num_drones - 1) if num_drones > 1 else 0)
    init_mantenimiento = 2000 * num_drones
    init_soporte = 2500 if num_drones <= 3 else 4500

    st.markdown("## 📊 Personalización de Costes e Ingresos")
    
    col_tab1, col_tab2 = st.columns(2)
    with col_tab1:
        st.subheader("🛠️ Inversión Inicial (CAPEX)")
        df_capex_raw = pd.DataFrame({
            "Concepto de Inversión": ["Hardware Drones + Docks", "Hardware Cámaras de Costa", "Desarrollo de Software IA", "Regulación AESA", "Despliegue y Logística"],
            "Coste (€)": [init_hw_dron, init_hw_camara, init_sw, init_aesa, init_logistica]
        })
        edited_capex_df = st.data_editor(df_capex_raw, num_rows="fixed", column_config={"Coste (€)": st.column_config.NumberColumn(format="%d €")}, key="capex_editor")
        total_capex = edited_capex_df["Coste (€)"].sum()

    with col_tab2:
        st.subheader("🔄 Costes Operativos (OPEX)")
        df_opex_raw = pd.DataFrame({
            "Concepto Operativo": ["Cloud + Conectividad", "Licencias DJI", "Seguros RC", "Mantenimiento Preventivo", "Soporte Software"],
            "Coste Anual (€)": [init_cloud, init_flighthub, init_seguro, init_mantenimiento, init_soporte]
        })
        edited_opex_df = st.data_editor(df_opex_raw, num_rows="fixed", column_config={"Coste Anual (€)": st.column_config.NumberColumn(format="%d €")}, key="opex_editor")
        total_opex_anual = edited_opex_df["Coste Anual (€)"].sum()

    st.subheader("💰 Subvenciones y Financiación Externa")
    df_subv_raw = pd.DataFrame({
        "Línea de Financiación": ["CDTI NEOTEC", "Women TechEU", "FOGAIBA", "ENISA Emprendedoras"],
        "Tipo": ["Fondo Perdido", "Fondo Perdido", "Fondo Perdido", "Préstamo"],
        "Importe (€)": [80000, 75000, 20000, 30000]
    })
    edited_subv_df = st.data_editor(df_subv_raw, num_rows="dynamic", column_config={"Tipo": st.column_config.SelectboxColumn("Tipo", options=["Fondo Perdido", "Préstamo"]), "Importe (€)": st.column_config.NumberColumn(format="%d €")}, key="subv_editor")
    
    total_ayudas = edited_subv_df["Importe (€)"].sum()
    total_fondo_perdido = edited_subv_df[edited_subv_df["Tipo"] == "Fondo Perdido"]["Importe (€)"].sum()

    # --- 3. PROYECCIÓN ---
    ingresos_anuales = num_drones * precio_estacion
    anios = ["Año 1", "Año 2", "Año 3", "Año 4", "Año 5"]
    lista_flujo_acum = []
    acumulado = 0
    for i in range(5):
        ing = ingresos_anuales + (total_ayudas if i == 0 else 0)
        gas = (total_capex if i == 0 else 0) + total_opex_anual + (800 * num_drones if i in [2, 4] else 0)
        acumulado += (ing - gas)
        lista_flujo_acum.append(acumulado)

    st.divider()
    
    # --- GRÁFICOS Y MÉTRICAS ---
    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        st.metric("Inversión Inicial (CAPEX)", f"{fmt(total_capex)} €")
    with m_col2:
        st.metric("Total Ayudas Captadas", f"{fmt(total_ayudas)} €")
    with m_col3:
        exposicion = total_capex - total_fondo_perdido
        st.metric("Exposición Neta Socios", f"{fmt(exposicion)} €", delta=f"{fmt(exposicion - 20000)} € vs Capital", delta_color="inverse")

    fig_roi = go.Figure()
    fig_roi.add_trace(go.Scatter(x=anios, y=lista_flujo_acum, mode='lines+markers', name='Flujo Acumulado', line=dict(color='#2ca02c', width=4)))
    fig_roi.add_trace(go.Scatter(x=anios, y=[0]*5, mode='lines', name='Equilibrio', line=dict(color='red', dash='dash')))
    fig_roi.update_layout(title="Curva de Retorno (Incluyendo Financiación Externa)", template="plotly_white", yaxis_title="Euros (€)")
    # FIX: Cambio por width='stretch'
    st.plotly_chart(fig_roi, width='stretch')

    # --- SIMULACIÓN 1-50 DRONES ---
    st.subheader("📊 Gráfico de Escalabilidad (1 a 50 Drones)")
    r_drones = list(range(1, 51))
    curva_total = []
    for n in r_drones:
        c_capex = (13500 * n * (1-dcto_volumen)) + (3500 * n) + (sw_base + (500*(n-1) if n>1 else 0)) + (sora_base + (1000*(n-1) if n>1 else 0)) + (3000 * n)
        c_opex = (1200 + 1200*n) + (360*n) + (600 + (350*(n-1) if n>1 else 0)) + (2000*n) + (2500 if n<=3 else 4500)
        curva_total.append(c_capex + c_opex)
    
    fig_esc = go.Figure()
    fig_esc.add_trace(go.Scatter(x=r_drones, y=curva_total, mode='lines', name='Inversión Total Año 1', line=dict(color='#9467bd', width=3)))
    fig_esc.update_layout(xaxis_title="Número de Drones", yaxis_title="Gasto Total Año 1 (€)", template="plotly_white")
    # FIX: Cambio por width='stretch'
    st.plotly_chart(fig_esc, width='stretch')