import streamlit as st
import json
import pandas as pd
import firebase_admin
from firebase_admin import credentials, db
import textwrap

# 1. Configuración visual básica de la página
st.set_page_config(page_title="Monitor de Máquina", page_icon="⚙️", layout="wide")
st.title("⚙️ Panel de Control - Rendimiento Máquina Noxon")
st.markdown("---")

# 2. Conexión segura a Firebase
if not firebase_admin._apps:
    cred_dict = json.loads(st.secrets["firebase"]["json_content"])
    
    # --- MOTOR DE AUTO-REPARACIÓN DE LA LLAVE ---
    # Extrae el texto crudo, limpia las deformaciones y reconstruye el formato PEM exigido
    llave_bruta = cred_dict["private_key"]
    cuerpo = llave_bruta.replace("-----BEGIN PRIVATE KEY-----", "").replace("-----END PRIVATE KEY-----", "")
    cuerpo = cuerpo.replace("\\n", "").replace("\n", "").replace(" ", "")
    cred_dict["private_key"] = "-----BEGIN PRIVATE KEY-----\n" + "\n".join(textwrap.wrap(cuerpo, 64)) + "\n-----END PRIVATE KEY-----\n"
    # --------------------------------------------
    
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://seguimiento-robot-eps32-default-rtdb.firebaseio.com/'
    })

# 3. Descargar los datos de la nube
nodo_registros = db.reference('Registros')
datos_crudos = nodo_registros.get()

# 4. Procesar y organizar la información
if datos_crudos:
    lista_datos = []
    for key, value in datos_crudos.items():
        value['id_firebase'] = key
        lista_datos.append(value)
        
    df = pd.DataFrame(lista_datos)
    
    st.subheader("📊 Resumen de Producción")
    
    if 'evento' in df.columns and 'reporte_palet_noxon' in df['evento'].values:
        df_noxon = df[df['evento'] == 'reporte_palet_noxon']
        
        total_palets = df_noxon['ciclo_num'].max()
        total_film = df_noxon['film_gastado_m'].sum()
        total_vueltas = df_noxon['vueltas'].sum()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("📦 Palets Envueltos (Total)", int(total_palets))
        col2.metric("📏 Film Gastado (Metros)", f"{total_film:.2f}")
        col3.metric("🔄 Vueltas del Brazo", int(total_vueltas))
        
        st.markdown("### 📋 Historial de Palets")
        st.dataframe(df_noxon[['ciclo_num', 'vueltas', 'metros_recorridos', 'film_gastado_m']])
    else:
        st.info("Esperando a que la máquina termine el primer palet para mostrar métricas de film...")

    st.markdown("---")
    st.subheader("⚡ Tiempos de Energía y Batería")
    
    if 'evento' in df.columns:
        df_trabajo = df[df['evento'] == 'tiempo_trabajo_segundos']
        df_carga = df[df['evento'] == 'tiempo_carga_segundos']
        
        minutos_trabajo = df_trabajo['valor'].sum() / 60 if not df_trabajo.empty else 0
        minutos_carga = df_carga['valor'].sum() / 60 if not df_carga.empty else 0
        
        col_t1, col_t2 = st.columns(2)
        col_t1.metric("🚜 Tiempo Trabajando (Minutos)", f"{minutos_trabajo:.1f}")
        col_t2.metric("🔌 Tiempo Cargando (Minutos)", f"{minutos_carga:.1f}")
else:
    st.warning("No hay datos en la base de datos todavía. ¡Enciende la máquina y conecta el ESP32 para comenzar!")
