import streamlit as st
import pandas as pd
import os
import logging
import warnings

warnings.filterwarnings("ignore", message="missing ScriptRunContext")
logging.getLogger("streamlit.runtime.scriptrunner").setLevel(logging.ERROR)
logging.getLogger("streamlit").setLevel(logging.ERROR)

# Szeroki układ strony, tak jak na zrzucie
st.set_page_config(page_title="MTR - System Diagnostyki Maszyn", layout="wide", page_icon="🛠️")

# --- STYLIZACJA KAFELKÓW (Zgodna z grafiką) ---
st.markdown("""
    <style>
    /* Szary kafelek procedury po prawej */
    .procedura-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 8px;
        border-left: 5px solid #d9534f;
        height: 100%;
    }
    /* Główne tło kontenera diagnostyki */
    .diagnostyka-container {
        border: 1px solid #e6e9ef;
        padding: 15px;
        border-radius: 8px;
        background-color: #ffffff;
    }
    </style>
""", unsafe_allow_html=True)

# === ŚCIEŻKI DO PLIKÓW ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, "baza_wiedzy.xlsx")
# Zakładam, że Twoje logo nazywa się 'logo.png' i leży w tym samym folderze
LOGO_PATH = os.path.join(BASE_DIR, "logo.png") 

def wczytaj_dane():
    if os.path.exists(FILE_PATH):
        try:
            df = pd.read_excel(FILE_PATH)
            df.columns = [c.strip() for c in df.columns]
            return df.to_dict(orient='records')
        except: return []
    return []

if 'dane' not in st.session_state:
    st.session_state.dane = wczytaj_dane()

# =====================================================================
# NAGŁÓWEK: Logo po lewej, Tytuł po prawej
# =====================================================================
col_logo, col_tytul = st.columns([1, 6])

with col_logo:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=120)
    else:
        st.write("🛠️") # Zamiennik, jeśli logo jeszcze nie ma w folderze

with col_tytul:
    # Pionowe wyrównanie tytułu za pomocą pustej przestrzeni lub dużego nagłówka
    st.markdown("<h1 style='margin-top: 15px; color: #1e3a8a;'>MTR System Diagnostyki Maszyn</h1>", unsafe_allow_html=True)

st.write("---")

# =====================================================================
# SEKCJA FILTROWANIA (Górne selekty ukryte w sidebarze lub na górze strony)
# =====================================================================
dzialy = sorted(list(set(i['dzial'] for i in st.session_state.dane if i.get('dzial'))))
wybrany_dzial = st.selectbox("Wybierz Dział:", [""] + dzialy)

linie = []
if wybrany_dzial:
    linie = sorted(list(set(i['linia'] for i in st.session_state.dane if i.get('dzial') == wybrany_dzial and i.get('linia'))))
wybrana_linia = st.selectbox("Wybierz Linię:", [""] + linie, disabled=not wybrany_dzial)

maszyny = []
if wybrana_linia:
    maszyny = sorted(list(set(i['maszyna'] for i in st.session_state.dane if i.get('dzial') == wybrany_dzial and i.get('linia') == wybrana_linia and i.get('maszyna'))))
wybrana_maszyna = st.selectbox("Wybierz Maszynę:", [""] + maszyny, disabled=not wybrana_linia)

filtrowane = []
if wybrana_maszyna:
    filtrowane = [i for i in st.session_state.dane if i.get('dzial') == wybrany_dzial and i.get('linia') == wybrana_linia and i.get('maszyna') == wybrana_maszyna]

# =====================================================================
# GŁÓWNY PANEL DIAGNOSTYCZNY (Układ z Twojej grafiki)
# =====================================================================
st.subheader("Maszyna diagnostyk:")

if filtrowane:
    # Podział ekranu na dwie kolumny: lewa (szersza) na tabelę, prawa (węższa) na procedurę
    col_tabela, col_procedura = st.columns([2, 1])
    
    # Wybieramy pierwszy pasujący wpis do wyświetlenia (lub możesz dodać st.radio)
    wpis = filtrowane[0] 
    
    with col_tabela:
        # Tworzymy ładną, czystą tabelę podglądu danych
        tabela_df = pd.DataFrame([{
            "Dział": wpis['dzial'],
            "Linia": wpis['linia'],
            "Maszyna": wpis['maszyna'],
            "Opis Awarii": wpis['objawy']
        }])
        # Wyświetlamy jako natywną tabelę Streamlit rozciągniętą do szerokości kolumny
        st.dataframe(tabela_df, use_container_width=True, hide_index=True)
        
    with col_procedura:
        # Kod HTML tworzący szary bloczek z instrukcjami, jak na grafice
        linie_procedury = "".join([f"<li>{l.strip()}</li>" for l in str(wpis['do_sprawdzenia']).split('\n') if l.strip()])
        
        st.markdown(f"""
            <div class="procedura-box">
                <h4 style="margin-top:0;">👋 PROCEDURA:</h4>
                <ol style="padding-left: 20px; font-weight: bold; color: #333;">
                    {linie_procedury}
                </ol>
            </div>
        """, unsafe_allow_html=True)
else:
    st.info("Wybierz Dział, Linię oraz Maszynę z filtrów powyżej, aby wyświetlić diagnostykę.")

# =====================================================================
# SEKCJA EDYCJI / DODAWANIA (Na samym dole pod linią rozdzielającą)
# =====================================================================
st.write("---")
st.subheader("📝 Dodaj nową awarię lub edytuj wybraną")
# ... Tutaj zostawiasz swój istniejący kod formularza `with st.form("formularz_wpisu"):` ...