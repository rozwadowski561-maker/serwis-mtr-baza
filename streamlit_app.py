import streamlit as st
import pandas as pd

# Konfiguracja strony pod telefony i PC
st.set_page_config(page_title="MTR - Diagnostyka Chmura", layout="wide", page_icon="🛠️")

st.title("🛠️ MTR - System Diagnostyki Maszyn")
st.write("Ogólnodostępna baza awarii (PC + Telefon)")

# --- TUTAJ WPISZ ID TWOJEGO ARKUSZA ---
# Twój link wygląda tak: https://docs.google.com/spreadsheets/d/15q3zbttjypg6xziqnbr_u6ajqaxlvh-2gcq6emibypa/edit...
# Musisz skopiować tylko ten długi ciąg znaków między /d/ a /edit
SHEET_ID ="15Q3ZBttJYpg6XZlqNbr_u6aJQAxLVh-2GCQ6ENibYpA"

# Bezpośredni link do pobierania jako CSV (nie wymaga żadnych bibliotek!)
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# Wczytanie danych
try:
    df = pd.read_csv(URL)
    # Konwersja nazw kolumn na małe litery, żeby nie było niespodzianek
    df.columns = df.columns.str.lower().str.strip()
except Exception as e:
    st.error(f"Błąd połączenia z Arkuszem Google. Sprawdź SHEET_ID. Szczegóły: {e}")
    df = pd.DataFrame(columns=['dzial', 'linia', 'maszyna', 'objawy', 'do_sprawdzenia'])

# Czyszczenie z pustych wierszy
if not df.empty:
    df = df.dropna(how='all')
    df = df.astype(str)

# --- SEKCJA FILTROWANIA ---
st.subheader("🔍 Wyszukaj awarię")

dzialy = sorted(list(df['dzial'].dropna().unique())) if 'dzial' in df.columns and not df.empty else []
wybrany_dzial = st.selectbox("Wybierz Dział:", [""] + dzialy)

linie = []
if wybrany_dzial:
    linie = sorted(list(df[df['dzial'] == wybrany_dzial]['linia'].dropna().unique()))
wybrana_linia = st.selectbox("Wybierz Linię:", [""] + linie, disabled=not wybrany_dzial)

maszyny = []
if wybrana_linia:
    maszyny = sorted(list(df[(df['dzial'] == wybrany_dzial) & (df['linia'] == wybrana_linia)]['maszyna'].dropna().unique()))
wybrana_maszyna = st.selectbox("Wybierz Maszynę:", [""] + maszyny, disabled=not wybrana_linia)

# Filtrowanie rekordów
filtrowane = pd.DataFrame()
if wybrana_maszyna:
    filtrowane = df[(df['dzial'] == wybrany_dzial) & (df['linia'] == wybrana_linia) & (df['maszyna'] == wybrana_maszyna)]

# Wyświetlanie wyników
if not filtrowane.empty:
    st.success(f"Znaleziono awarie ({len(filtrowane)}):")
    opcje_awarii = [f"{idx+1}. Objaw: {row['objawy']}" for idx, row in filtrowane.iterrows()]
    wybrana_opcja = st.radio("Wybierz awarię, aby zobaczyć szczegóły:", opcje_awarii)
    
    if wybrana_opcja:
        nr_na_liscie = opcje_awarii.index(wybrana_opcja)
        wpis_do_edycji = filtrowane.iloc[nr_na_liscie]
        
        st.info(f"**OBJAWY:**\n{wpis_do_edycji['objawy']}")
        st.markdown("**⚙️ PROCEDURA SPRAWDZENIA:**")
        
        for linia in str(wpis_do_edycji['do_sprawdzenia']).split('\n'):
            if linia.strip():
                st.markdown(f"👉 {linia}")
else:
    if wybrana_maszyna:
        st.warning("Brak wpisów dla tej maszyny.")

# --- INSTRUKCJA DODAWANIA ---
st.write("---")
st.subheader("📝 Chcesz dodać nową awarię?")
st.info("Aby dodać lub edytować wpisy, otwórz swój Arkusz Google na telefonie lub komputerze. Aplikacja zaktualizuje się automatycznie!")