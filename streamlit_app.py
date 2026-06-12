import streamlit as st
import pandas as pd

# Konfiguracja strony pod telefony i PC
st.set_page_config(page_title="MTR - Diagnostyka Chmura", layout="wide", page_icon="🛠️")

st.title("🛠️ Tyracze System Diagnostyki Maszyn")
st.write("Ogólnodostępna baza awarii dla zmiany Szefa Marcina Szatkowskiego ")

# Bezpośredni link do pobierania jako CSV (z poprawnym ID Twojego arkusza)
URL = "https://docs.google.com/spreadsheets/d/15Q3ZBttJYpg6XZlqNbr_u6aJQAxLVh-2GCQ6ENibYpA/export?format=csv"

# Wczytanie danych
try:
    df = pd.read_csv(URL)
    df.columns = df.columns.str.lower().str.strip()
    error_mode = False
except Exception as e:
    st.error(f"Nie można pobrać danych z Arkusza Google. Upewnij się, że arkusz jest udostępniony dla 'Każdy mający link jako edytujący'. Szczegóły: {e}")
    df = pd.DataFrame(columns=['dzial', 'linia', 'maszyna', 'objawy', 'do_sprawdzenia'])
    error_mode = True

# Czyszczenie danych na starcie aplikacji
if not df.empty:
    df = df.dropna(how='all')
    df = df.astype(str)
    
    # Czyszczenie ukrytych spacji i enterów z tekstu w bazie
    for col in df.columns:
        df[col] = df[col].str.strip()

# --- SEKCJA FILTROWANIA ---
st.subheader("🔍 Wyszukaj awarię")

if not error_mode and not df.empty:
    # 1. Filtr Dział
    dzialy = sorted(list(df['dzial'].dropna().unique())) if 'dzial' in df.columns else []
    wybrany_dzial = st.selectbox("Wybierz Dział:", [""] + dzialy)

    # 2. Filtr Linia
    linie = []
    if wybrany_dzial and 'linia' in df.columns:
        linie = sorted(list(df[df['dzial'] == wybrany_dzial]['linia'].dropna().unique()))
    wybrana_linia = st.selectbox("Wybierz Linię:", [""] + linie, disabled=not wybrany_dzial)

    # 3. Filtr Maszyna (Homag i inne bazy teraz scalają się bez powtórzeń)
    maszyny = []
    if wybrana_linia and 'maszyna' in df.columns:
        df_filtrowany_maszyny = df[(df['dzial'] == wybrany_dzial) & (df['linia'] == wybrana_linia)]
        maszyny = sorted(list(df_filtrowany_maszyny['maszyna'].dropna().unique()))
        
    wybrana_maszyna = st.selectbox("Wybierz Maszynę:", [""] + maszyny, disabled=not wybrana_linia)

    # --- FILTROWANIE REKORDÓW I WYŚWIETLANIE ---
    filtrowane = pd.DataFrame()
    if wybrana_maszyna:
        filtrowane = df[(df['dzial'] == wybrany_dzial) & (df['linia'] == wybrana_linia) & (df['maszyna'] == wybrana_maszyna)]

    # Wyświetlanie wyników
    if not filtrowane.empty:
        st.success(f"Znaleziono awarie ({len(filtrowane)}):")
        opcje_awarii = [f"{idx+1}. Objaw: {row['objawy']}" for idx, row in filtrowane.iterrows() if 'objawy' in row]
        wybrana_opcja = st.radio("Wybierz awarię, aby zobaczyć szczegóły:", opcje_awarii)
        
        if wybrana_opcja:
            nr_na_liscie = opcje_awarii.index(wybrana_opcja)
            wpis_do_edycji = filtrowane.iloc[nr_na_liscie]
            
            if 'objawy' in wpis_do_edycji:
                st.info(f"**OBJAWY:**\n{wpis_do_edycji['objawy']}")
            if 'do_sprawdzenia' in wpis_do_edycji:
                st.markdown("**⚙️ PROCEDURA SPRAWDZENIA:**")
                for linia in str(wpis_do_edycji['do_sprawdzenia']).split('\n'):
                    if linia.strip():
                        st.markdown(f"👉 {linia}")
    else:
        if wybrana_maszyna:
            st.warning("Brak wpisów dla tej maszyny.")
else:
    if not error_mode:
        st.info("Arkusz Google jest pusty. Wpisz pierwszą awarię w arkuszu na telefonie, aby dane się pojawiły!")

# --- INSTRUKCJA ---
st.write("---")
st.subheader("📝 Dodawanie i edycja")
st.info("Aby dodać nową maszynę, linię lub procedurę, dopisz ją po prostu w nowym wierszu w aplikacji Arkusze Google na telefonie. Ta strona zaktualizuje się automatycznie!")
st.info("W razie problemów pisz mateusz.rozwadowski@inter.ikea.com"" MTR")
st.info("Nie odbieram po godzinach pracy ani na urlopie")
