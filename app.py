import streamlit as st
import pandas as pd
import time
from textblob import TextBlob
from deep_translator import MyMemoryTranslator

# ── 1. Configuración de la página ──────────────────────────────
st.set_page_config(
    page_title="Sabor & Tradición - Análisis de Sentimiento",
    page_icon="🧠",
    layout="wide"
)

# ── 2. Estado de la Sesión (Memoria) ──────────────────────────
if "comments_data" not in st.session_state:
    st.session_state.comments_data = []
if "single_comment_text" not in st.session_state:
    st.session_state.single_comment_text = ""
if "original_es_text" not in st.session_state:
    st.session_state.original_es_text = ""
if "translate_checkbox" not in st.session_state:
    st.session_state.translate_checkbox = False

# ── 3. Funciones de Traducción ─────────────────────────────────
@st.cache_data(show_spinner=False)
def translate_text(text: str) -> str:
    """Traduce el texto usando MyMemoryTranslator (ES a EN)."""
    try:
        if not text.strip():
            return text
        return MyMemoryTranslator(source='es-ES', target='en-US').translate(text)
    except Exception:
        return text

def toggle_translation():
    """Se ejecuta al marcar o desmarcar la casilla de traducción."""
    current_text = st.session_state.single_comment_text
    
    if st.session_state.translate_checkbox:
        # Si se MARCA: Guardamos el español original y traducimos visualmente
        st.session_state.original_es_text = current_text
        if current_text.strip():
            try:
                st.session_state.single_comment_text = translate_text(current_text)
            except Exception:
                pass
    else:
        # Si se DESMARCA: Restauramos el español original
        st.session_state.single_comment_text = st.session_state.original_es_text

def clear_text():
    """Limpia todo para poder hacer una nueva consulta sin errores."""
    st.session_state.single_comment_text = ""
    st.session_state.original_es_text = ""
    st.session_state.translate_checkbox = False

# ── 4. Lógica Principal de Análisis ────────────────────────────
def add_comment(comment_es: str, category: str, pre_translated_en: str = None):
    """Analiza el sentimiento y guarda ambas versiones del texto."""
    if not comment_es.strip():
        return
        
    # Si ya tenemos la traducción (porque el usuario usó el checkbox), la usamos.
    # Si no, la generamos automáticamente.
    comment_en = pre_translated_en if pre_translated_en else translate_text(comment_es)
    
    # Analizamos la versión en INGLÉS
    blob = TextBlob(comment_en)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity

    # Clasificamos
    if polarity > 0.10:
        sentiment, emoji = "Positivo :D", "😊"
    elif polarity < -0.10:
        sentiment, emoji = "Negativo :(", "😞"
    else:
        sentiment, emoji = "Neutral 😐", "😐"

    # Guardamos ambas versiones
    st.session_state.comments_data.append({
        "Comentario_ES": comment_es,
        "Comentario_EN": comment_en,
        "Categoría": category,
        "Sentimiento": sentiment,
        "Emoji": emoji,
        "Polaridad": round(polarity, 3),
        "Subjetividad": round(subjectivity, 3)
    })

def process_single_comment():
    """Procesa el comentario y devuelve el estado de la operación."""
    text = st.session_state.single_comment_text
    if not text.strip():
        return "EMPTY"
        
    cat = st.session_state.single_cat
    
    # Identificamos el texto en español correcto dependiendo del traductor
    texto_es_a_guardar = st.session_state.original_es_text if st.session_state.translate_checkbox else text
    
    # VALIDACIÓN: Evitar duplicados
    if len(st.session_state.comments_data) > 0:
        ultimo_comentario = st.session_state.comments_data[-1]["Comentario_ES"]
        if ultimo_comentario == texto_es_a_guardar:
            return "DUPLICATE"
            
    if st.session_state.translate_checkbox:
        add_comment(texto_es_a_guardar, cat, pre_translated_en=text)
    else:
        add_comment(text, cat)
        
    return "SUCCESS"

def load_default_examples():
    """Carga 15 ejemplos variados (Positivos, Negativos y Neutrales)."""
    examples = [
        ("La comida está cara pero es demasiado buena, vale totalmente la pena.", "Precio / Valor"),
        ("El mesero fue muy grosero y tardaron 45 minutos en traer el plato.", "Atención y Servicio"),
        ("El lugar es acogedor, limpio y la música está a buen volumen.", "Ambiente"),
        ("La carne estaba fría y sin sabor.", "Comida y Calidad"),
        ("Un restaurante normal, nada fuera de lo común.", "General"),
        ("Las porciones son gigantes y los postres son espectaculares.", "Comida y Calidad"),
        ("El precio me parece excesivo para la calidad del producto.", "Precio / Valor"),
        ("La atención fue pésima, el mesero fue muy grosero y la comida estaba horrible", "General"),
        ("Excelente servicio, nos atendieron rápido y con una sonrisa en todo momento.", "Atención y Servicio"),
        ("Había demasiado ruido y el aire acondicionado estaba apagado, me sentí incómodo.", "Ambiente"),
        ("La comida cumplió su propósito, pero no me sorprendió para nada.", "Comida y Calidad"),
        ("Precios justos para la cantidad de comida que sirven.", "Precio / Valor"),
        ("Nos cobraron un plato extra que no pedimos, terrible experiencia en la caja.", "Atención y Servicio"),
        ("Me encantó la decoración del salón, es un lugar perfecto para relajarse.", "Ambiente"),
        ("Fui a almorzar el martes, el menú del día es igual al de siempre.", "General")
    ]
    for text, cat in examples:
        add_comment(text, cat)

# ── 5. Interfaz Principal ──────────────────────────────────────
st.title("🧠 Análisis de Sentimiento - Restaurante Sabor & Tradición")
st.caption("Combina tu sistema interactivo con el panel de resumen.")
st.divider()

col_left, col_right = st.columns([1.2, 1.8])

# ================= COLUMNA IZQUIERDA: INGRESOS =================
with col_left:
    st.subheader("✍️ Ingresar Opiniones")
    
    tab_single, tab_bulk = st.tabs(["Comentario Único", "Carga Masiva"])
    
    # --- Pestaña: Comentario Único ---
    with tab_single:
        with st.container(border=True):
            col_input, col_option = st.columns([3, 1])
            
            with col_input:
                st.text_area(
                    "Texto a analizar:",
                    placeholder="Ej.: The food was cold. / Es un lugar agradable…",
                    height=120,
                    key="single_comment_text"
                )
                
            with col_option:
                st.checkbox(
                    "🌐 Traducir ES→EN",
                    key="translate_checkbox",
                    on_change=toggle_translation
                )
            
            st.selectbox(
                "Categoría evaluada:",
                ["Comida y Calidad", "Atención y Servicio", "Precio / Valor", "Ambiente", "General"],
                key="single_cat"
            )
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                # Quitamos el on_click para poder mostrar el spinner en el flujo principal
                btn_analizar = st.button("🚀 Analizar y Guardar", use_container_width=True)
            with col_btn2:
                st.button("🗑️ Limpiar Caja", on_click=clear_text, use_container_width=True)

            # Acciones del botón analizar
            if btn_analizar:
                with st.spinner("⏳ Analizando y traduciendo texto..."):
                    time.sleep(0.5) # Pequeña pausa para que la animación sea visible
                    status = process_single_comment()
                
                if status == "DUPLICATE":
                    st.warning("⚠️ Este comentario ya fue analizado. Modifícalo para realizar un nuevo análisis.")
                elif status == "EMPTY":
                    st.error("❌ Por favor, escribe un texto válido antes de analizar.")
                elif status == "SUCCESS":
                    st.success("✅ ¡Comentario analizado y guardado con éxito!")

    # --- Pestaña: Carga Masiva ---
    with tab_bulk:
        st.markdown("Escribe varios comentarios en español (uno por línea):")
        bulk_text = st.text_area("Lista de comentarios:", height=120)
        bulk_category = st.selectbox(
            "Categoría general:",
            ["Comida y Calidad", "Atención y Servicio", "Precio / Valor", "Ambiente", "General"],
            key="bulk_cat"
        )
        if st.button("📥 Procesar Lista", use_container_width=True):
            lines = [line.strip() for line in bulk_text.split("\n") if line.strip()]
            if lines:
                with st.spinner("⏳ Procesando lote de comentarios..."):
                    time.sleep(0.5)
                    for line in lines:
                        add_comment(line, bulk_category)
                st.success(f"✅ Se procesaron {len(lines)} comentarios con éxito.")
            else:
                st.warning("❌ Ingresa al menos una línea con texto.")

    st.markdown("---")
    st.subheader("⚙️ Acciones Rápidas")
    c1, c2 = st.columns(2)
    if c1.button("🧪 Cargar Ejemplos", use_container_width=True):
        with st.spinner("Cargando base de datos de prueba..."):
            time.sleep(0.5)
            load_default_examples()
        st.rerun()
    if c2.button("🗑️ Vaciar Todo", use_container_width=True):
        st.session_state.comments_data = []
        st.rerun()

# ================= COLUMNA DERECHA: DASHBOARD =================
with col_right:
    st.subheader("📊 Resumen del Negocio")
    
    if not st.session_state.comments_data:
        st.info("💡 Aún no hay comentarios cargados. Carga ejemplos o ingresa uno manualmente para ver el análisis.")
    else:
        df = pd.DataFrame(st.session_state.comments_data)
        
        # Cálculos de Métricas
        total_comments = len(df)
        positives = len(df[df["Sentimiento"] == "Positivo :D"])
        neutrals = len(df[df["Sentimiento"] == "Neutral 😐"])
        negatives = len(df[df["Sentimiento"] == "Negativo :("])
        
        sentiment_counts = df["Sentimiento"].value_counts()
        prevailing_sentiment = sentiment_counts.idxmax()
        avg_polarity = df["Polaridad"].mean()
        avg_subjectivity = df["Subjetividad"].mean()

        # KPIs Rápidos
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total", total_comments)
        m2.metric("Positivos", positives)
        m3.metric("Neutrales", neutrals)
        m4.metric("Negativos", negatives)

        st.markdown("---")
        
        # Gráficos Visuales
        diag_col1, diag_col2 = st.columns(2)
        with diag_col1:
            st.markdown(f"**Sentimiento General:** {prevailing_sentiment}")
            st.metric("Promedio Polaridad", f"{avg_polarity:.3f}", delta="rango [-1, 1]")
            norm_polarity = (avg_polarity + 1) / 2
            st.progress(norm_polarity, text="← Negativo | Positivo →")
            
        with diag_col2:
            st.markdown("**Nivel de Subjetividad**")
            st.metric("Promedio Subjetividad", f"{avg_subjectivity:.3f}", delta="rango [0, 1]")
            st.progress(avg_subjectivity, text="← Objetivo | Subjetivo →")

        st.markdown("---")
        
        st.subheader("📋 Detalle de Comentarios Analizados")
        
        # EL INTERRUPTOR PARA TRADUCIR LA TABLA
        mostrar_ingles = st.toggle("🌐 Traducir comentarios cargados al Inglés (MyMemoryTranslator)")

        # Lógica para elegir qué texto mostrar
        columna_texto_mostrar = "Comentario_EN" if mostrar_ingles else "Comentario_ES"
        
        # Preparar y mostrar dataframe
        df_display = df[["Emoji", "Sentimiento", "Categoría", columna_texto_mostrar, "Polaridad", "Subjetividad"]].copy()
        df_display.rename(columns={columna_texto_mostrar: "Comentario"}, inplace=True)

        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True
        )
