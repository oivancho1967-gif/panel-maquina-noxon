import streamlit as st
import json
import firebase_admin
from firebase_admin import credentials

st.set_page_config(page_title="Diagnóstico", page_icon="🏥", layout="wide")
st.title("🏥 Modo de Diagnóstico (Rayos X)")
st.markdown("Revisando por qué Firebase rechaza tu archivo...")

try:
    # 1. Leer de los secretos
    cred_dict = json.loads(st.secrets["firebase"]["json_content"])
    st.success("✔️ Paso 1: Archivo leído desde la caja fuerte correctamente.")
    
    # 2. Revisar qué hay dentro (sin mostrar datos privados)
    st.write("### 🔍 ¿Qué encontró el sistema en tu archivo?")
    claves = list(cred_dict.keys())
    st.write(claves)
    
    # 3. Analizar posibles errores
    if 'apiKey' in cred_dict:
        st.error("🚨 ERROR ENCONTRADO: Subiste la llave de 'Web Config'. Firebase necesita la llave de 'Service Account'.")
    elif 'type' not in cred_dict or cred_dict['type'] != 'service_account':
        st.error("🚨 ERROR ENCONTRADO: Falta la palabra 'service_account'. El archivo que pegaste no es el correcto o está incompleto.")
    else:
        st.success("✔️ Paso 2: Es una llave de tipo 'Service Account' válida.")
        
    if 'private_key' not in cred_dict:
        st.error("🚨 ERROR ENCONTRADO: No encuentro la 'private_key' (Clave Privada) en tu texto. ¿Copiaste todo el archivo?")
    else:
        st.success("✔️ Paso 3: La Clave Privada existe.")
        try:
            # 4. Prueba de fuego
            cred_dict["private_key"] = cred_dict["private_key"].replace("\\n", "\n")
            cred = credentials.Certificate(cred_dict)
            st.success("✔️ Paso 4: ¡La llave pasó la prueba final de Firebase! Si ves esto, ya funciona.")
        except Exception as e:
            st.error(f"🚨 ERROR ENCONTRADO: La clave privada está dañada, cortada o deformada. Detalle técnico: {e}")

except Exception as e:
    st.error(f"Error general: {e}")
