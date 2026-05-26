import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta, date
import json, re

# Configuración de la página web de la aplicación
st.set_page_config(page_title="Propuesta Pliego: Sistema Posidonia", layout="wide", initial_sidebar_state="expanded")

# --- BASE DE DATOS (SUPABASE con fallback SQLite local) ---
SUPABASE_DISPONIBLE = False
_supabase = None

try:
    from supabase import create_client
    if "supabase" in st.secrets:
        _supabase = create_client(st.secrets["supabase"]["url"], st.secrets["supabase"]["key"])
        SUPABASE_DISPONIBLE = True
except Exception:
    pass

if not SUPABASE_DISPONIBLE:
    import sqlite3
    _sqlite_conn = sqlite3.connect('posidonia.db')
    _sqlite_conn.execute('''CREATE TABLE IF NOT EXISTS simulaciones
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  nombre TEXT UNIQUE,
                  fecha TEXT,
                  parametros TEXT,
                  resultados TEXT)''')
    _sqlite_conn.execute('''CREATE TABLE IF NOT EXISTS propuesta
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  sec1_resumen TEXT,
                  sec2_empresa TEXT,
                  sec3_objetivos TEXT,
                  sec3_limitaciones TEXT,
                  sec3_arquitectura TEXT,
                  sec4_cronograma TEXT,
                  sec6_criterios TEXT,
                  sec7_contacto TEXT,
                  updated_at TEXT)''')
    _sqlite_conn.commit()
    _sqlite_conn.close()

def guardar_simulacion(nombre, parametros, resultados):
    data = {
        "nombre": nombre,
        "fecha": datetime.now().isoformat(),
        "parametros": json.dumps(parametros, ensure_ascii=False),
        "resultados": json.dumps(resultados, ensure_ascii=False)
    }
    if SUPABASE_DISPONIBLE:
        try:
            _supabase.table("simulaciones").insert(data).execute()
            return True
        except Exception as e:
            st.error(f"Error de Supabase: {e}")
            return False
    else:
        import sqlite3
        conn = sqlite3.connect('posidonia.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO simulaciones (nombre, fecha, parametros, resultados) VALUES (?, ?, ?, ?)",
                      (nombre, data["fecha"], data["parametros"], data["resultados"]))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            st.warning(f"Ya existe una simulación llamada '{nombre}' en la BD local.")
            return False
        finally:
            conn.close()

def eliminar_simulacion(nombre):
    if SUPABASE_DISPONIBLE:
        _supabase.table("simulaciones").delete().eq("nombre", nombre).execute()
    else:
        import sqlite3
        conn = sqlite3.connect('posidonia.db')
        c = conn.cursor()
        c.execute("DELETE FROM simulaciones WHERE nombre=?", (nombre,))
        conn.commit()
        conn.close()

def cargar_simulacion(nombre):
    if SUPABASE_DISPONIBLE:
        res = _supabase.table("simulaciones").select("parametros,resultados").eq("nombre", nombre).execute()
        if res.data:
            return json.loads(res.data[0]["parametros"]), json.loads(res.data[0]["resultados"])
    else:
        import sqlite3
        conn = sqlite3.connect('posidonia.db')
        c = conn.cursor()
        c.execute("SELECT parametros, resultados FROM simulaciones WHERE nombre=?", (nombre,))
        row = c.fetchone()
        conn.close()
        if row:
            return json.loads(row[0]), json.loads(row[1])
    return None, None

def listar_simulaciones():
    if SUPABASE_DISPONIBLE:
        res = _supabase.table("simulaciones").select("nombre,fecha").order("fecha", desc=True).execute()
        return [(r["nombre"], r["fecha"]) for r in res.data] if res.data else []
    else:
        import sqlite3
        conn = sqlite3.connect('posidonia.db')
        c = conn.cursor()
        c.execute("SELECT nombre, fecha FROM simulaciones ORDER BY fecha DESC")
        rows = c.fetchall()
        conn.close()
        return rows

def guardar_propuesta():
    data = {
        "sec1_resumen": st.session_state.sec1_resumen,
        "sec2_empresa": st.session_state.sec2_empresa,
        "sec3_objetivos": st.session_state.get("sec3_objetivos", ""),
        "sec3_limitaciones": st.session_state.get("sec3_limitaciones", ""),
        "sec3_arquitectura": st.session_state.get("sec3_arquitectura", ""),
        "sec4_cronograma": json.dumps([{k: (v.isoformat() if isinstance(v, (datetime, date)) else v) for k, v in row.items()} for row in st.session_state.df_cronograma.to_dict(orient="records")], ensure_ascii=False) if "df_cronograma" in st.session_state else "",
        "sec6_criterios": st.session_state.sec6_criterios,
        "sec7_contacto": st.session_state.sec7_contacto,
        "updated_at": datetime.now().isoformat()
    }
    if SUPABASE_DISPONIBLE:
        try:
            _supabase.table("propuesta").insert(data).execute()
            return True
        except Exception as e:
            st.error(f"Error de Supabase al guardar propuesta: {e}")
            return False
    else:
        import sqlite3
        conn = sqlite3.connect('posidonia.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO propuesta (sec1_resumen, sec2_empresa, sec3_objetivos, sec3_limitaciones, sec3_arquitectura, sec4_cronograma, sec6_criterios, sec7_contacto, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                      (data["sec1_resumen"], data["sec2_empresa"], data["sec3_objetivos"], data["sec3_limitaciones"], data["sec3_arquitectura"], data["sec4_cronograma"], data["sec6_criterios"], data["sec7_contacto"], data["updated_at"]))
            conn.commit()
            return True
        except Exception as e:
            st.error(f"Error al guardar propuesta: {e}")
            return False
        finally:
            conn.close()

def cargar_propuesta():
    if SUPABASE_DISPONIBLE:
        try:
            res = _supabase.table("propuesta").select("*").order("id", desc=True).limit(1).execute()
            if res.data:
                return res.data[0]
        except Exception:
            pass
    else:
        try:
            import sqlite3
            conn = sqlite3.connect('posidonia.db')
            c = conn.cursor()
            c.execute("SELECT sec1_resumen, sec2_empresa, sec3_objetivos, sec3_limitaciones, sec3_arquitectura, sec4_cronograma, sec6_criterios, sec7_contacto FROM propuesta ORDER BY id DESC LIMIT 1")
            row = c.fetchone()
            conn.close()
            if row:
                return {"sec1_resumen": row[0], "sec2_empresa": row[1], "sec3_objetivos": row[2], "sec3_limitaciones": row[3], "sec3_arquitectura": row[4], "sec4_cronograma": row[5], "sec6_criterios": row[6], "sec7_contacto": row[7]}
        except Exception:
            pass
    return None

# --- FUNCIÓN DE FORMATEO EUROPEO ---
def fmt(valor, dees=0):
    try:
        valor = float(valor)
    except (ValueError, TypeError):
        return valor
    s = f"{valor:,.{dees}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")

def _md(content):
    partes = re.split(
        r'(!\[([^\]]*)\]\(((?:img/)?[^)]+)\)|(<img[^>]+>))',
        content
    )
    i = 0
    while i < len(partes):
        t = partes[i]
        if t is None or t == "":
            i += 1
            continue
        if t.startswith("!["):
            alt = partes[i+1] if i+1 < len(partes) else ""
            ruta = partes[i+2] if i+2 < len(partes) else ""
            i += 4
            try:
                st.image(ruta, caption=alt if alt else None)
            except Exception:
                st.markdown(t)
        elif t.startswith("<img"):
            tag = t
            src_m = re.search(r'src\s*=\s*"((?:img/)?[^"]+)"', tag)
            w_m = re.search(r'width\s*=\s*"(\d+)"', tag)
            if src_m:
                kwargs = {"width": int(w_m.group(1))} if w_m else {}
                try:
                    st.image(src_m.group(1), **kwargs)
                except Exception:
                    st.markdown(tag)
            else:
                st.markdown(tag)
            i += 4
        else:
            st.markdown(t)
            i += 1

# --- INICIALIZAR ESTADO DE SESIÓN ---
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False

if "sec1_resumen" not in st.session_state:
    st.session_state.sec1_resumen = """La presente propuesta tecnológica responde a la necesidad crítica de proteger de manera eficiente y escalable las praderas de *Posidonia oceanica* en el archipiélago balear, iniciando con una fase piloto optimizada en la isla de Formentera. 

Nuestra solución cambia el paradigma de la vigilancia marina: eliminamos el patrullaje analógico y ciego mediante embarcaciones tripuladas y lo sustituimos por un sistema de **interceptación quirúrgica automatizada**. Combinando cámaras de análisis costero continuo, intersección geoespacial (GIS) y estaciones de drones autónomos (*Drone-in-a-Box*), el sistema solo actúa cuando se detecta una infracción probable, minimizando costes operativos y garantizando evidencias legales irrefutables con impacto ambiental inmediato."""

if "sec2_empresa" not in st.session_state:
    st.session_state.sec2_empresa = """Somos una compañía de base tecnológica de nueva creación (S.L.) especializada en ingeniería de automatización y soluciones de impacto ambiental (*Green-Tech*). Nuestra estructura corporativa ágil está integrada por un equipo interdisciplinar de **tres profesionales especialistas**, cuyo equilibrio competencial minimiza el riesgo de ejecución del proyecto:

* **Dirección de Inteligencia Artificial & Sistemas:** Ingeniero especialista en el diseño de modelos de visión artificial, encargado de la arquitectura de la red neural, el pipeline de procesamiento de datos y la homografía matemática de las cámaras de costa.
* **Dirección de Arquitectura de Datos & Big Data:** Ingeniera de origen colombiano especialista en el modelado, optimización y securización de bases de datos masivas geoespaciales (GIS) y sincronización cloud en tiempo real. Su incorporación aporta el perfil de diversidad clave para el acceso prioritario a fondos tecnológicos europeos de discriminación positiva (*Women TechEU*).
* **Dirección Legal, Regulación & Riesgos:** Abogado especialista en derecho aeronáutico y gestión de riesgos operativos, encargado del desarrollo de los estudios de seguridad aeronáutica SORA, interlocución con AESA y el blindaje legal de las evidencias capturadas para su validez en los expedientes sancionadores."""

if "sec6_criterios" not in st.session_state:
    st.session_state.sec6_criterios = """Nuestra propuesta destaca en los pliegos públicos al ofrecer las mejores métricas de eficiencia integral:
* **Adecuación Tecnológica (40%):** Arquitectura basada en alertas pasivas que elimina el ruido innecesario de sobrevuelo constante en playas y respeta al completo el RGPD al auditar solo naves en presunta infracción.
* **Eficiencia Económica (30%):** Reducción acreditada de más del 70% del coste operativo actual frente al uso de patrulleras neumáticas convencionales con tripulación física.
* **Soporte Post-Implementación & SLA (20%):** Compromiso de monitorización cloud remota continua y sustitución/reparación de nodos de hardware en un plazo máximo de 24 horas durante los meses de campaña.
* **Criterio de Impacto Sostenible (10%):** Huella de carbono cero en las misiones operativas directas al operar con vectores energéticos limpios y eléctricos (recarga en Dock)."""

if "sec7_contacto" not in st.session_state:
    st.session_state.sec7_contacto = """* **Canal Único de Comunicación:** Para la resolución de dudas sobre la presente propuesta o el despliegue del MVP en Formentera, se centralizarán las comunicaciones en el correo técnico: `contact@posidonia-monitoring.tech`.
* **Acuerdo de Confidencialidad (NDA):** Toda la información relativa al código de homografía, pesos de la red neural e información cartográfica propietaria está sujeta a secreto industrial estricto.
* **Cláusula de Salvaguarda Legal:** La entrega de este documento se realiza en concepto de propuesta técnica para licitación y no constituye obligación contractual de prestación de servicios hasta la firma definitiva del pliego y formalización de la adjudicación por el órgano competente."""

if "sec3_objetivos" not in st.session_state:
    st.session_state.sec3_objetivos = """* **Despliegue del 'Filtro 0' (Vigilancia Pasiva):** Instalación de cámaras ópticas PTZ industriales en zonas urbanas no protegidas con visibilidad directa sobre las zonas de fondeo.
* **Módulos de Software Core:** Licenciamiento de la plataforma cloud de procesamiento de imágenes con algoritmos de OCR (lectura de matrículas) e intersección de mapas de calor GIS de posidonia de la CAIB.
* **Infraestructura de Interceptación:** Despliegue de estaciones automatizadas **DJI Dock 2** con aeronaves **Matrice 3D** equipadas con filtros polarizadores circulares (CPL) para anular el reflejo solar y capturar imágenes cenitales del fondo marino en la ventana crítica de 11:00 a 16:00."""

if "sec3_limitaciones" not in st.session_state:
    st.session_state.sec3_limitaciones = """* La S.L. aporta la evidencia digital y la georreferenciación inversa del barco; la emisión física de la sanción económica es competencia exclusiva de la administración pública.
* Queda excluida de la fase de pruebas la operación en condiciones meteorológicas extremas que superen los límites estructurales del hardware (vientos superiores a 12 m/s)."""

if "sec3_arquitectura" not in st.session_state:
    st.session_state.sec3_arquitectura = """```text
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
```"""

if "df_cronograma" not in st.session_state:
    st.session_state.df_cronograma = pd.DataFrame([
        {"Hito / Fase": "Lanzamiento de la RFP / Pliego", "Descripción": "Apertura oficial de la licitación por el Govern", "Fecha Estimada": "2026-06-01", "Duración (Días)": 1},
        {"Hito / Fase": "Fecha límite para preguntas técnicas", "Descripción": "Periodo para resolver dudas de conectividad y GIS", "Fecha Estimada": "2026-06-15", "Duración (Días)": 1},
        {"Hito / Fase": "Publicación de respuestas a aclaraciones", "Descripción": "Aclaraciones publicadas en el perfil del contratante", "Fecha Estimada": "2026-06-22", "Duración (Días)": 1},
        {"Hito / Fase": "Entrega improrrogable de propuestas", "Descripción": "Cierre de recepción de ofertas técnicas y económicas", "Fecha Estimada": "2026-07-15", "Duración (Días)": 1},
        {"Hito / Fase": "Fase de evaluación y demos de IA", "Descripción": "Validación en entorno de pruebas del algoritmo de homografía", "Fecha Estimada": "2026-08-01", "Duración (Días)": 30},
        {"Hito / Fase": "Adjudicación definitiva del contrato", "Descripción": "Firma del contrato de servicios DaaS para la campaña", "Fecha Estimada": "2026-09-01", "Duración (Días)": 1},
    ])
    st.session_state.df_cronograma["Fecha Estimada"] = pd.to_datetime(st.session_state.df_cronograma["Fecha Estimada"])

# Cargar propuesta guardada si existe
_propuesta_guardada = cargar_propuesta()
if _propuesta_guardada:
    st.session_state.sec1_resumen = _propuesta_guardada["sec1_resumen"]
    st.session_state.sec2_empresa = _propuesta_guardada["sec2_empresa"]
    st.session_state.sec3_objetivos = _propuesta_guardada.get("sec3_objetivos", st.session_state.sec3_objetivos)
    st.session_state.sec3_limitaciones = _propuesta_guardada.get("sec3_limitaciones", st.session_state.sec3_limitaciones)
    st.session_state.sec3_arquitectura = _propuesta_guardada.get("sec3_arquitectura", st.session_state.sec3_arquitectura)
    _crono_json = _propuesta_guardada.get("sec4_cronograma")
    if _crono_json:
        try:
            _crono_lista = json.loads(_crono_json)
            _df = pd.DataFrame(_crono_lista)
            _df["Fecha Estimada"] = pd.to_datetime(_df["Fecha Estimada"])
            st.session_state.df_cronograma = _df
        except Exception:
            pass
    st.session_state.sec6_criterios = _propuesta_guardada["sec6_criterios"]
    st.session_state.sec7_contacto = _propuesta_guardada["sec7_contacto"]

# --- PANTALLA PRINCIPAL: SISTEMA DE PESTAÑAS ---
tab1, tab2 = st.tabs(["📄 Propuesta Formal RFP & Gantt", "📊 Simulador Financiero & ROI"])

# =========================================================================
# PESTAÑA 1: PROPUESTA FORMAL ADAPTADA A LA ESTRUCTURA RFP REQUESTED
# =========================================================================
def _on_edit_toggle():
    if not st.session_state.edit_checkbox:
        guardar_propuesta()

with tab1:
    st.title("💼 Memoria Técnica y Administrativa: Respuesta a la RFP")
    st.markdown("**Destinatario:** Govern de les Illes Balears - Conselleria d'Agricultura, Pesca i Medi Natural")
    st.write("Servicio Llave en Mano (DaaS) de Inspección y Alertas de Fondeo Ilegal mediante Inteligencia Artificial")

    edit_mode = st.checkbox("✏️ Editar contenido de la propuesta", key="edit_checkbox", on_change=_on_edit_toggle)
    st.session_state.edit_mode = edit_mode

    st.divider()
    
    # 1. RESUMEN EJECUTIVO
    st.header("1. Resumen Ejecutivo (Executive Summary)")
    if st.session_state.edit_mode:
        st.session_state.sec1_resumen = st.text_area("Editar Resumen Ejecutivo", value=st.session_state.sec1_resumen, height=200)
        _, col_btn = st.columns([5, 1])
        with col_btn:
            if st.button("💾", key="save_sec1", help="Guardar", use_container_width=True):
                guardar_propuesta()
    else:
        _md(st.session_state.sec1_resumen)
    
    # 2. INFORMACIÓN Y CONTEXTO DE LA EMPRESA
    st.header("2. Información y Contexto de la Empresa")
    if st.session_state.edit_mode:
        st.session_state.sec2_empresa = st.text_area("Editar Información de la Empresa", value=st.session_state.sec2_empresa, height=250)
        _, col_btn = st.columns([5, 1])
        with col_btn:
            if st.button("💾", key="save_sec2", help="Guardar", use_container_width=True):
                guardar_propuesta()
    else:
        _md(st.session_state.sec2_empresa)
    
    st.divider()

    # 3. ALCANCE DEL PROYECTO Y REQUISITOS TÉCNICOS
    st.header("3. Alcance del Proyecto y Requisitos Técnico (Scope of Work)")

    if st.session_state.edit_mode:
        st.session_state.sec3_objetivos = st.text_area("**Objetivos Específicos & Entregables:**", value=st.session_state.sec3_objetivos, height=150)
        _, col_btn = st.columns([5, 1])
        with col_btn:
            if st.button("💾", key="save_sec3a", help="Guardar", use_container_width=True):
                guardar_propuesta()
        st.session_state.sec3_limitaciones = st.text_area("**Limitaciones (Fuera de Alcance):**", value=st.session_state.sec3_limitaciones, height=100)
        _, col_btn = st.columns([5, 1])
        with col_btn:
            if st.button("💾", key="save_sec3b", help="Guardar", use_container_width=True):
                guardar_propuesta()
    else:
        col_scope1, col_scope2 = st.columns(2)
        with col_scope1:
            _md("**Objetivos Específicos & Entregables:**\n\n" + st.session_state.sec3_objetivos)
        with col_scope2:
            _md("**Limitaciones (Fuera de Alcance):**\n\n" + st.session_state.sec3_limitaciones)

    st.subheader("🖥️ Arquitectura Lógica de la Solución")
    if st.session_state.edit_mode:
        st.session_state.sec3_arquitectura = st.text_area("Editar Arquitectura", value=st.session_state.sec3_arquitectura, height=200)
        _, col_btn = st.columns([5, 1])
        with col_btn:
            if st.button("💾", key="save_sec3c", help="Guardar", use_container_width=True):
                guardar_propuesta()
    else:
        _md(st.session_state.sec3_arquitectura)

    st.divider()

    # 4. CRONOGRAMA DEL PROCESO DE SELECCIÓN (PLIEGO PROPUESTO)
    st.header("4. Cronograma del Proceso de Selección")
    st.write("Fechas marco propuestas para la licitación estacional con vistas a la campaña de 2027:")

    if st.session_state.edit_mode:
        st.session_state.df_cronograma = st.data_editor(
            st.session_state.df_cronograma,
            num_rows="dynamic",
            column_config={
                "Fecha Estimada": st.column_config.DateColumn("Fecha Estimada", format="YYYY-MM-DD"),
                "Duración (Días)": st.column_config.NumberColumn("Duración (Días)", min_value=0, format="%d días")
            },
            key="cronograma_editor",
            height=300
        )
        _, col_btn = st.columns([5, 1])
        with col_btn:
            if st.button("💾", key="save_sec4", help="Guardar", use_container_width=True):
                guardar_propuesta()
    else:
        st.table(st.session_state.df_cronograma)

    try:
        _df_gantt4 = st.session_state.df_cronograma.copy()
        _df_gantt4["Start"] = pd.to_datetime(_df_gantt4["Fecha Estimada"])
        _df_gantt4["Finish"] = _df_gantt4.apply(
            lambda r: r["Start"] + timedelta(days=max(int(r["Duración (Días)"]), 1)), axis=1
        )
        fig_gantt4 = px.timeline(
            _df_gantt4,
            x_start="Start",
            x_end="Finish",
            y="Hito / Fase",
            color="Descripción",
            title="📅 Cronograma del Proceso de Selección",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_gantt4.update_yaxes(autorange="reversed")
        fig_gantt4.update_layout(
            showlegend=False,
            template="plotly_white",
            margin=dict(l=20, r=20, t=40, b=20),
            height=400
        )
        st.plotly_chart(fig_gantt4, use_container_width=True)
    except Exception as e:
        st.error(f"Error al generar Gantt: {e}")

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
    if st.session_state.edit_mode:
        col1, col2 = st.columns([6, 1])
        with col1:
            st.session_state.sec6_criterios = st.text_area("Editar Criterios de Evaluación", value=st.session_state.sec6_criterios, height=200)
        with col2:
            st.write("")
            if st.button("💾", key="save_sec6", help="Guardar esta sección", use_container_width=True):
                guardar_propuesta()
    else:
        _md(st.session_state.sec6_criterios)
 
    st.divider()
 
    # 7. PUNTOS DE CONTACTO Y ASPECTOS LEGALES
    st.header("7. Puntos de Contacto y Aspectos Legal")
    if st.session_state.edit_mode:
        col1, col2 = st.columns([6, 1])
        with col1:
            st.session_state.sec7_contacto = st.text_area("Editar Contacto y Legal", value=st.session_state.sec7_contacto, height=200)
        with col2:
            st.write("")
            if st.button("💾", key="save_sec7", help="Guardar esta sección", use_container_width=True):
                guardar_propuesta()
    else:
        _md(st.session_state.sec7_contacto)

# =========================================================================
# PESTAÑA 2: SIMULADOR FINANCIERO (TOTALMENTE INTACTA EN LÓGICA / COREGIDO SYNTAX WIDTH)
# =========================================================================
with tab2:
    # --- APLICAR PARÁMETROS CARGADOS (ANTES de renderizar widgets) ---
    if "_cargar_params" in st.session_state:
        for _k, _v in st.session_state.pop("_cargar_params").items():
            st.session_state[_k] = _v
    if "_mensaje" in st.session_state:
        st.success(st.session_state.pop("_mensaje"))

    # --- DEBUG ---
    _debug = st.sidebar.checkbox("🔧 Debug BD", value=False)
    if _debug:
        st.sidebar.write(f"**Supabase:** {'✅ Conectado' if SUPABASE_DISPONIBLE else '❌ No disponible (usando SQLite)'}")
        if SUPABASE_DISPONIBLE:
            try:
                _test = _supabase.table("simulaciones").select("count", count="exact").execute()
                st.sidebar.write(f"**Simulaciones en BD:** {_test.count}")
            except Exception as _e:
                st.sidebar.error(f"Error consultando Supabase: {_e}")

    # --- 1. ENTRADA DE VARIABLES (Side-bar) ---
    st.sidebar.header("⚙️ Variables del Simulador")
    num_drones = st.sidebar.number_input("Número de Nodos (Dron + Cámara)", min_value=1, max_value=100, value=2, step=1, key="sim_num_drones")
    precio_estacion = st.sidebar.number_input("Precio Pliego / Temporada (€)", min_value=0, value=30000, step=1000, key="sim_precio")
    dcto_volumen = st.sidebar.number_input("Descuento Volumen (%)", min_value=0.0, max_value=100.0, value=7.0, step=0.5, key="sim_dcto") / 100
    sw_base = st.sidebar.number_input("Desarrollo SW Core IA (€)", min_value=0, value=12000, step=500, key="sim_sw")
    sora_base = st.sidebar.number_input("Trámite AESA Base (€)", min_value=0, value=4500, step=500, key="sim_sora")

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
        _df_capex_base = {
            "Concepto de Inversión": ["Hardware Drones + Docks", "Hardware Cámaras de Costa", "Desarrollo de Software IA", "Regulación AESA", "Despliegue y Logística"],
            "Coste (€)": [init_hw_dron, init_hw_camara, init_sw, init_aesa, init_logistica]
        }
        df_capex_raw = st.session_state.pop("_capex_cargado", pd.DataFrame(_df_capex_base))
        edited_capex_df = st.data_editor(df_capex_raw, num_rows="dynamic", column_config={
            "Concepto de Inversión": st.column_config.TextColumn("Concepto de Inversión"),
            "Coste (€)": st.column_config.NumberColumn(format="%d €")
        }, key="capex_editor")
        total_capex = edited_capex_df["Coste (€)"].sum()

    with col_tab2:
        st.subheader("🔄 Costes Operativos (OPEX)")
        _df_opex_base = {
            "Concepto Operativo": ["Cloud + Conectividad", "Licencias DJI", "Seguros RC", "Mantenimiento Preventivo", "Soporte Software"],
            "Coste Anual (€)": [init_cloud, init_flighthub, init_seguro, init_mantenimiento, init_soporte]
        }
        df_opex_raw = st.session_state.pop("_opex_cargado", pd.DataFrame(_df_opex_base))
        edited_opex_df = st.data_editor(df_opex_raw, num_rows="dynamic", column_config={
            "Concepto Operativo": st.column_config.TextColumn("Concepto Operativo"),
            "Coste Anual (€)": st.column_config.NumberColumn(format="%d €")
        }, key="opex_editor")
        total_opex_anual = edited_opex_df["Coste Anual (€)"].sum()

    st.subheader("💰 Subvenciones y Financiación Externa")
    _df_subv_base = {
        "Línea de Financiación": ["CDTI NEOTEC", "Women TechEU", "FOGAIBA", "ENISA Emprendedoras"],
        "Tipo": ["Fondo Perdido", "Fondo Perdido", "Fondo Perdido", "Préstamo"],
        "Importe (€)": [80000, 75000, 20000, 30000]
    }
    df_subv_raw = st.session_state.pop("_subv_cargado", pd.DataFrame(_df_subv_base))
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
    
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.metric("Inversión Inicial (CAPEX)", f"{fmt(total_capex)} €")
    with m_col2:
        st.metric("Coste Operativo Anual (OPEX)", f"{fmt(total_opex_anual)} €")
    with m_col3:
        exposicion = total_capex - total_fondo_perdido
        st.metric("Exposición Neta Socios", f"{fmt(exposicion)} €", delta=f"{fmt(exposicion - 20000)} € vs Capital", delta_color="inverse")
    with m_col4:
        st.metric("Total Ayudas Captadas", f"{fmt(total_ayudas)} €")

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

    st.divider()
    st.subheader("💾 Guardar / Cargar Simulación")

    if not SUPABASE_DISPONIBLE:
        st.warning("📦 Usando SQLite local. En Streamlit Cloud, configura Supabase en los Secrets para que los datos persistan.")

    col_save1, col_save2 = st.columns([2, 1])
    with col_save1:
        sim_nombre = st.text_input("Nombre de la simulación", placeholder="Ej: Escenario optimista 2027", key="sim_nombre_input")
    with col_save2:
        if st.button("💾 Guardar Simulación", use_container_width=True):
            if sim_nombre.strip():
                parametros = {
                    "num_drones": int(num_drones),
                    "precio_estacion": int(precio_estacion),
                    "dcto_volumen": float(dcto_volumen),
                    "sw_base": int(sw_base),
                    "sora_base": int(sora_base)
                }
                resultados = {
                    "total_capex": int(total_capex),
                    "total_opex_anual": int(total_opex_anual),
                    "total_ayudas": int(total_ayudas),
                    "total_fondo_perdido": int(total_fondo_perdido),
                    "exposicion": int(exposicion),
                    "flujo_acum_5anos": [int(f) for f in lista_flujo_acum],
                    "capex_df": edited_capex_df.to_dict('records'),
                    "opex_df": edited_opex_df.to_dict('records'),
                    "subv_df": edited_subv_df.to_dict('records')
                }
                if guardar_simulacion(sim_nombre.strip(), parametros, resultados):
                    st.success(f"Simulación '{sim_nombre}' guardada")
                else:
                    if SUPABASE_DISPONIBLE:
                        st.error("Error al guardar en Supabase. Revisa que RLS esté deshabilitado en la tabla 'simulaciones'.")
                    else:
                        st.error(f"Ya existe una simulación llamada '{sim_nombre}' en la BD local.")
            else:
                st.warning("Introduce un nombre para la simulación")

    simulaciones = listar_simulaciones()
    if simulaciones:
        opciones = [f"{nom} ({fecha[:10]})" for nom, fecha in simulaciones]
        nom_select = st.selectbox("Cargar simulación guardada", opciones, key="sim_lista")
        
        idx_sel = opciones.index(nom_select)
        nombre_sel = simulaciones[idx_sel][0]
        params_preview, res_preview = cargar_simulacion(nombre_sel)
        
        if params_preview and res_preview:
            st.markdown(f"**Vista previa de '{nombre_sel}':**")
            pcol1, pcol2, pcol3, pcol4 = st.columns(4)
            pcol1.metric("Drones", params_preview["num_drones"])
            pcol2.metric("CAPEX", f"{fmt(res_preview['total_capex'])} €")
            pcol3.metric("OPEX Anual", f"{fmt(res_preview['total_opex_anual'])} €")
            pcol4.metric("Ayudas", f"{fmt(res_preview['total_ayudas'])} €")
        
        col_load, col_del = st.columns(2)
        with col_load:
            if st.button("📂 Cargar Simulación", use_container_width=True):
                if params_preview:
                    st.session_state._cargar_params = {
                        "sim_num_drones": params_preview["num_drones"],
                        "sim_precio": params_preview["precio_estacion"],
                        "sim_dcto": params_preview["dcto_volumen"] * 100,
                        "sim_sw": params_preview["sw_base"],
                        "sim_sora": params_preview["sora_base"],
                    }
                    if "capex_df" in res_preview:
                        st.session_state._capex_cargado = pd.DataFrame(res_preview["capex_df"])
                    if "opex_df" in res_preview:
                        st.session_state._opex_cargado = pd.DataFrame(res_preview["opex_df"])
                    if "subv_df" in res_preview:
                        st.session_state._subv_cargado = pd.DataFrame(res_preview["subv_df"])
                    st.session_state._mensaje = f"Simulación '{nombre_sel}' cargada"
                    st.rerun()
        with col_del:
            if st.button("🗑️ Eliminar Simulación", use_container_width=True):
                eliminar_simulacion(nombre_sel)
                st.session_state._mensaje = f"Simulación '{nombre_sel}' eliminada"
                st.rerun()
    else:
        st.info("No hay simulaciones guardadas todavía")
