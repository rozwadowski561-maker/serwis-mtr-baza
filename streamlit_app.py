import streamlit as st
import pandas as pd
import os
import logging
import warnings

# Wyłączenie zbędnych komunikatów w terminalu
warnings.filterwarnings("ignore", message="missing ScriptRunContext")
logging.getLogger("streamlit.runtime.scriptrunner").setLevel(logging.ERROR)
logging.getLogger("streamlit").setLevel(logging.ERROR)

# Szeroki układ strony idealny pod kafelki
st.set_page_config(page_title="MTR - Diagnostyka Chmura", layout="wide", page_icon="🛠️")

# --- STYLIZACJA KAFELKA PROCEDURY (Szary bloczek z pomarańczowym paskiem) ---
st.markdown("""
    <style>
    .procedura-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 8px;
        border-left: 5px solid #ff9800;
        height: 100%;
    }
    </style>
""", unsafe_allow_html=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE_DIR, "logo.png")

# =====================================================================
# NAGŁÓWEK APLIKACJI
# =====================================================================
col_logo, col_tytul = st.columns([1, 6])
with col_logo:
    if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=110)
    else: st.write("🛠️")
with col_tytul:
    st.title("🛠️ MTR i Tyracze System Diagnostyki Maszyn")
    st.write("Ogólnodostępna baza awarii dla zmiany Szefa Marcina Szatkowskiego")

# Twój stały ID arkusza z Google Sheets
SPREADSHEET_ID = "15Q3ZBttJYpg6XZlqNbr_u6aJQAxLVh-2GCQ6ENibYpA"

# Linki celujące dokładnie w Twoje karty z przeglądarki (gid=0 to Struktura)
URL_STRUKTURA = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=0"
URL_AWARIE = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=1458408410"

# Wczytanie i czyszczenie danych z chmury Google
try:
    # Wczytujemy arkusze i zamieniamy puste pola na pusty tekst, żeby uniknąć błędów typu "NaN"
    df_st = pd.read_csv(URL_STRUKTURA).fillna("").astype(str)
    df_aw = pd.read_csv(URL_AWARIE).fillna("").astype(str)
    
    # Standaryzacja nazw kolumn na małe litery bez spacji brzegowych
    df_st.columns = df_st.columns.str.lower().str.strip()
    df_aw.columns = df_aw.columns.str.lower().str.strip()
    
    # Dokładne czyszczenie tekstu wewnątrz komórek z ukrytych spacji i enterów
    for col in df_st.columns: df_st[col] = df_st[col].str.strip()
    for col in df_aw.columns: df_aw[col] = df_aw[col].str.strip()
    
    error_mode = False
except Exception as e:
    st.error(f"Nie można pobrać danych z Arkusza Google. Sprawdź połączenie z internetem. Szczegóły: {e}")
    error_mode = True

# =====================================================================
# SEKCJA FILTROWANIA (Pobiera hierarchię z karty Struktura)
# =====================================================================
st.subheader("🔍 Wyszukaj awarię")

if not error_mode:
    c1, c2, c3 = st.columns(3)
    
    with c1:
        dzialy = sorted(list(df_st['dzial'].dropna().unique())) if 'dzial' in df_st.columns else []
        wybrany_dzial = st.selectbox("Wybierz Dział:", [""] + dzialy)

    with c2:
        linie = []
        if wybrany_dzial and 'linia' in df_st.columns:
            linie = list(df_st[df_st['dzial'] == wybrany_dzial]['linia'].dropna().unique())
        wybrana_linia = st.selectbox("Wybierz Linię:", [""] + linie, disabled=not wybrany_dzial)

    with c3:
        maszyny = []
        if wybrana_linia and 'maszyna' in df_st.columns:
            # Zachowuje idealną kolejność ciągu technologicznego (tak jak wpisałeś w arkuszu)
            maszyny = list(df_st[(df_st['dzial'] == wybrany_dzial) & (df_st['linia'] == wybrana_linia)]['maszyna'].dropna().unique())
        wybrana_maszyna = st.selectbox("Wybierz Komponent / Stację:", [""] + maszyny, disabled=not wybrana_linia)

    # =====================================================================
    # PANEL DIAGNOSTYCZNY (Pobiera i wyświetla awarie z karty Awarie)
    # =====================================================================
    st.write("---")
    st.subheader("📋 Maszyna diagnostyk:")

    if wybrana_maszyna and 'maszyna' in df_aw.columns:
        # Pancerne porównanie: wielkość liter i spacje nie mają znaczenia przy szukaniu awarii
        awarie_maszyny = df_aw[df_aw['maszyna'].str.lower() == wybrana_maszyna.lower()]
        
        if not awarie_maszyny.empty:
            col_tabela, col_procedura = st.columns([2, 1])
            
            with col_tabela:
                st.write("👇 **Wybierz konkretny objaw, aby wyświetlić instrukcję krok po kroku:**")
                opcje_awarii = [f"⚠️ Objaw: {row['objawy']}" for _, row in awarie_maszyny.iterrows() if 'objawy' in row]
                wybrana_opcja = st.radio("Zarejestrowane usterki dla tego elementu:", opcje_awarii, label_visibility="collapsed")
                
                # Wyciągnięcie rekordu, który kliknął użytkownik
                idx_wybranej = opcje_awarii.index(wybrana_opcja)
                wpis = awarie_maszyny.iloc[idx_wybranej]
                
            with col_procedura:
                # Rozbijanie tekstu procedury na estetyczne punkty (👉) przy napotkaniu nowej linii w komórce
                linie_procedury = "".join([f"<li>{l.strip()}</li>" for l in str(wpis['do_sprawdzenia']).split('\n') if l.strip()])
                st.markdown(f"""
                    <div class="procedura-box">
                        <h4 style="margin-top:0; color: #ff9800;">👋 PROCEDURA SPRAWDZENIA:</h4>
                        <p style="font-size: 13px; color: #666; margin-bottom: 5px;">Lokalizacja: <b>{wybrana_linia} ➡️ {wybrana_maszyna}</b></p>
                        <p style="font-weight: bold; color: #d9534f; margin-top: 0; font-size: 16px;">{wpis['objawy']}</p>
                        <hr style="border: 0; border-top: 1px solid #ccc; margin-bottom: 15px;">
                        <ol style="padding-left: 20px; font-weight: bold; line-height: 1.7; color: #333; font-size: 15px;">
                            {linie_procedury}
                        </ol>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.warning(f"Brak zarejestrowanych awarii dla komponentu '{wybrana_maszyna}' w zakładce 'Awarie'.")
    else:
        st.info("Wybierz Dział, Linię oraz odpowiedni Komponent z filtrów u góry, aby otworzyć procedury diagnostyczne.")

# --- STOPKA INFORMACYJNA ---
st.write("---")
st.subheader("📝 Instrukcja obsługi bazy")
st.info("Układ i filtry ładują się z karty 'Struktura'. Usterki i opisy krok po kroku dopisujesz w karcie 'Awarie' bezpośrednio na swoim telefonie. Strona aktualizuje się sama po odświeżeniu!")
st.info("W razie problemów z aplikacją pisz: mateusz.rozwadowski@inter.ikea.com")
st.info("Nie odbieram po godzinach pracy ani na urlopie")