import streamlit as st
import pandas as pd
import os
import logging
import warnings

warnings.filterwarnings("ignore", message="missing ScriptRunContext")
logging.getLogger("streamlit.runtime.scriptrunner").setLevel(logging.ERROR)
logging.getLogger("streamlit").setLevel(logging.ERROR)

st.set_page_config(page_title="MTR - Diagnostyka Chmura", layout="wide", page_icon="🛠️")

# --- STYLIZACJA KAFELKA PROCEDURY ---
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

# --- NAGŁÓWEK ---
col_logo, col_tytul = st.columns([1, 6])
with col_logo:
    if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=110)
    else: st.write("🛠️")
with col_tytul:
    st.title("🛠️ MTR i Tyracze System Diagnostyki Maszyn")
    st.write("Ogólnodostępna baza awarii dla zmiany Szefa Marcina Szatkowskiego")

# ID Arkusza Google
SPREADSHEET_ID = "15Q3ZBttJYpg6XZlqNbr_u6aJQAxLVh-2GCQ6ENibYpA"

# Pobieranie danych z jawnym wymuszeniem kodowania UTF-8 i czyszczenia ukrytych znaczników (utf-8-sig)
URL_STRUKTURA = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=0"
URL_AWARIE = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=1458408410"

try:
    # Wczytanie z automatycznym usunięciem ukrytych śmieci systemowych (BOM) z nagłówków
    df_st = pd.read_csv(URL_STRUKTURA, encoding='utf-8-sig').fillna("").astype(str)
    df_aw = pd.read_csv(URL_AWARIE, encoding='utf-8-sig').fillna("").astype(str)
    
    # Czyszczenie nazw kolumn: usuwamy spacji i zmieniamy na małe litery
    df_st.columns = df_st.columns.str.strip().str.lower()
    df_aw.columns = df_aw.columns.str.strip().str.lower()
    
    # Mapowanie na wypadek polskich znaków w nagłówkach (dział / dzial)
    df_st = df_st.rename(columns={'dział': 'dzial'})
    df_aw = df_aw.rename(columns={'do_sprawdzenia': 'do_sprawdzenia'})
    
    # Czyszczenie wnętrza tabeli
    for col in df_st.columns: df_st[col] = df_st[col].str.strip()
    for col in df_aw.columns: df_aw[col] = df_aw[col].str.strip()
    
    error_mode = False
except Exception as e:
    st.error(f"Nie można pobrać danych z Arkusza Google. Sprawdź czy arkusz jest udostępniony. Szczegóły błędu: {e}")
    error_mode = True

# --- SEKCJA FILTROWANIA ---
st.subheader("🔍 Wyszukaj awarię")

if not error_mode:
    # Sprawdzamy czy wymagane kolumny w ogóle istnieją po wyczyszczeniu
    if 'dzial' in df_st.columns and 'linia' in df_st.columns and 'maszyna' in df_st.columns:
        c1, c2, c3 = st.columns(3)
        
        with c1:
            dzialy = sorted(list(df_st['dzial'].dropna().unique()))
            wybrany_dzial = st.selectbox("Wybierz Dział:", [""] + dzialy)

        with c2:
            linie = []
            if wybrany_dzial:
                linie = list(df_st[df_st['dzial'] == wybrany_dzial]['linia'].dropna().unique())
            wybrana_linia = st.selectbox("Wybierz Linię:", [""] + linie, disabled=not wybrany_dzial)

        with c3:
            maszyny = []
            if wybrana_linia:
                maszyny = list(df_st[(df_st['dzial'] == wybrany_dzial) & (df_st['linia'] == wybrana_linia)]['maszyna'].dropna().unique())
            wybrana_maszyna = st.selectbox("Wybierz Komponent / Stację:", [""] + maszyny, disabled=not wybrana_linia)

        # --- PANEL GŁÓWNY ---
        st.write("---")
        st.subheader("📋 Maszyna diagnostyk:")

        if wybrana_maszyna and 'maszyna' in df_aw.columns:
            awarie_maszyny = df_aw[df_aw['maszyna'].str.lower() == wybrana_maszyna.lower()]
            
            if not awarie_maszyny.empty:
                col_tabela, col_procedura = st.columns([2, 1])
                
                with col_tabela:
                    st.write("👇 **Wybierz konkretny objaw, aby wyświetlić instrukcję:**")
                    opcje_awarii = [f"⚠️ Objaw: {row['objawy']}" for _, row in awarie_maszyny.iterrows() if 'objawy' in row]
                    wybrana_opcja = st.radio("Zarejestrowane usterki:", opcje_awarii, label_visibility="collapsed")
                    
                    idx_wybranej = opcje_awarii.index(wybrana_opcja)
                    wpis = awarie_maszyny.iloc[idx_wybranej]
                    
                with col_procedura:
                    # Pobieranie kolumny z procedurą (obsługuje małe/wielkie litery)
                    col_proc_name = 'do_sprawdzenia' if 'do_sprawdzenia' in wpis else wpis.index[2]
                    linie_procedury = "".join([f"<li>{l.strip()}</li>" for l in str(wpis[col_proc_name]).split('\n') if l.strip()])
                    
                    st.markdown(f"""
                        <div class="procedura-box">
                            <h4 style="margin-top:0; color: #ff9800;">👋 PROCEDURA SPRAWDZENIA:</h4>
                            <p style="font-size: 13px; color: #666; margin-bottom: 5px;">Lokalizacja: <b>{wybrana_linia} ➡️ {wybrana_maszyna}</b></p>
                            <p style="font-weight: bold; color: #d9534f; margin-top: 0; font-size: 16px;">{wpis['objawy'] if 'objawy' in wpis else ''}</p>
                            <hr style="border: 0; border-top: 1px solid #ccc; margin-bottom: 15px;">
                            <ol style="padding-left: 20px; font-weight: bold; line-height: 1.7; color: #333; font-size: 15px;">
                                {linie_procedury}
                            </ol>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning(f"Brak zarejestrowanych awarii dla komponentu '{wybrana_maszyna}' w zakładce 'Awarie'.")
        else:
            st.info("Wybierz Dział, Linię oraz odpowiedni Komponent z filtrów u góry, aby otworzyć procedury.")
    else:
        st.error("Błąd struktury kolumn w Arkuszu Google! Upewnij się, że nagłówki w pierwszym wierszu to: Dział, Linia, Maszyna.")

# --- STOPKA ---
st.write("---")
st.info("MTR  - Dane zaciągane na żywo z Arkusza Exel.")