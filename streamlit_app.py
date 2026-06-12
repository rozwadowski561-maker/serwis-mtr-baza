import streamlit as st
import pandas as pd
import os
import logging
import warnings

warnings.filterwarnings("ignore", message="missing ScriptRunContext")
logging.getLogger("streamlit.runtime.scriptrunner").setLevel(logging.ERROR)
logging.getLogger("streamlit").setLevel(logging.ERROR)

st.set_page_config(page_title="MTR - Diagnostyka Chmura", layout="wide", page_icon="🛠️")

# --- STYLIZACJA KAFELKÓW I PROCEDUR ---
st.markdown("""
    <style>
    .procedura-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 8px;
        border-left: 5px solid #ff9800;
        height: 100%;
    }
    .hasla-box {
        background-color: #eff6ff;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #3b82f6;
        margin-bottom: 20px;
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
    st.write("Ogólnodostępna baza awarii dla zmiany Szefa Marcin Szatkowskiego")

# ID Arkusza Google
SPREADSHEET_ID = "15Q3ZBttJYpg6XZlqNbr_u6aJQAxLVh-2GCQ6ENibYpA"

# Linki do trzech osobnych kart z chmury Google (Twoje aktualne GID)
URL_STRUKTURA = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=0"
URL_AWARIE = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=1458408410" 
URL_HASLA = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=1929302363"

try:
    # Pobieranie danych ze wszystkich trzech zakładkek
    df_st = pd.read_csv(URL_STRUKTURA, encoding='utf-8-sig').fillna("").astype(str)
    df_aw = pd.read_csv(URL_AWARIE, encoding='utf-8-sig').fillna("").astype(str)
    df_hd = pd.read_csv(URL_HASLA, encoding='utf-8-sig').fillna("").astype(str)
    
    # Standaryzacja nagłówków kolumn
    df_st.columns = df_st.columns.str.strip().str.lower()
    df_aw.columns = df_aw.columns.str.strip().str.lower()
    df_hd.columns = df_hd.columns.str.strip().str.lower()
    
    df_st = df_st.rename(columns={'dział': 'dzial'})
    
    # Czyszczenie wnętrza tabel
    for col in df_st.columns: df_st[col] = df_st[col].str.strip()
    for col in df_aw.columns: df_aw[col] = df_aw[col].str.strip()
    for col in df_hd.columns: df_hd[col] = df_hd[col].str.strip()
    
    error_mode = False
except Exception as e:
    st.error(f"Nie można pobrać danych z Arkusza Google. Sprawdź poprawność linków i GID. Szczegóły: {e}")
    error_mode = True

# =====================================================================
# SEKCJA ŻARÓWKI (Z FUNKCJĄ OTWIERANIA I ZAMYKANIA)
# =====================================================================
if 'pokaz_hasla' not in st.session_state:
    st.session_state.pokaz_hasla = False  # Na starcie aplikacja ładuje się z ukrytymi hasłami

if not error_mode:
    st.write("---")
    
    # Dynamiczny tekst na przycisku zależny od stanu pamięci systemu
    etykieta_przycisku = "❌ ZAMKNIJ BAZĘ HASEŁ" if st.session_state.pokaz_hasla else "💡 POKAŻ HASŁA I DOSTĘPY DO MASZYN"
    
    if st.button(etykieta_przycisku, use_container_width=True):
        # Odwrócenie stanu (zamykanie/otwieranie) po kliknięciu
        st.session_state.pokaz_hasla = not st.session_state.pokaz_hasla
        st.rerun()  # Natychmiastowe przeładowanie widoku przycisku i tabeli

    # Jeśli użytkownik włączył podgląd – pokazujemy niebieski boks z hasłami
    if st.session_state.pokaz_hasla:
        st.markdown('<div class="hasla-box">', unsafe_allow_html=True)
        st.markdown("### 🔐 Ściągawka z haseł i dostępów HMI / PLC:")
        
        if not df_hd.empty:
            st.dataframe(df_hd, use_container_width=True, hide_index=True)
        else:
            st.warning("Karta z hasłami w Arkuszu Google jest obecnie pusta.")
        st.markdown('</div>', unsafe_allow_html=True)

# =====================================================================
# SEKCJA FILTROWANIA (Główna wyszukiwarka)
# =====================================================================
st.write("---")
st.subheader("🔍 Wyszukaj awarię")

if not error_mode:
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

        # --- PANEL DIAGNOSTYCZNY ---
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
        st.error("Błąd struktury kolumn w Arkuszu Google! Sprawdź nagłówki.")

# --- STOPKA ---
st.write("---")
st.info("MTR System Chmurowy v3.1 - Pełna integracja z procedurami i bazą haseł online (z opcją zamykania paneli).")