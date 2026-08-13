import streamlit as st
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import pandas as pd

# 1. Configuración visual básica de la página
st.set_page_config(page_title="Monitor de Máquina", page_icon="⚙️", layout="wide")
st.title("⚙️ Panel de Control - Rendimiento de la Máquina")
st.markdown("---")

# 2. Conexión segura a Firebase (Evita conectarse dos veces)
if not firebase_admin._apps:
    # Aquí usamos la llave maestra que descargaste
    import json
    import streamlit as st
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://seguimiento-robot-eps32-default-rtdb.firebaseio.com/'
    })

# 3. Descargar los datos de la nube
nodo_registros = db.reference('Registros')
datos_crudos = nodo_registros.get()

# 4. Procesar y organizar la información
if datos_crudos:
    total_ciclos = 0
    total_segundos = 0
    
    # Recorremos la base de datos separando los lotes del brazo y el horómetro
    for push_id, info in datos_crudos.items():
        evento = info.get('evento', '')
        valor = info.get('valor', 0)
        
        # OJO: Aquí le decimos que también sume los ciclos individuales viejos 
        # y los lotes nuevos de 10 para no perder el historial
        if evento == "lote_10_ciclos" or evento == "ciclo_completado":
            total_ciclos += valor
        elif evento == "carga_finalizada":
            total_segundos += valor
            
    # Calculamos horas, minutos y segundos para que sea fácil de leer
    horas = int(total_segundos // 3600)
    minutos = int((total_segundos % 3600) // 60)
    
    # 5. Dibujar los indicadores visuales en la pantalla
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(label="🔄 Ciclos Totales Completados", value=f"{total_ciclos} ciclos")
        
    with col2:
        st.metric(label="⏱️ Tiempo Total de Operación", value=f"{horas}h {minutos}m")
        
    st.success("¡Conexión en tiempo real establecida correctamente!")

else:
    st.warning("Aún no hay datos legibles en la base de datos. ¡Pon a trabajar la máquina!")

