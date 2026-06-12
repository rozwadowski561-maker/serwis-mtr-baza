import streamlit as st
import requests

# Konfiguracja strony pod ekrany smartfonów
st.set_page_config(page_title="MTR - Diagnostyka Mobilna", layout="centered", page_icon="🛠️")

st.title("🛠️ MTR - Diagnostyka Maszyn")
st.write("Mobilna baza awarii (Podgląd live)")

# === KLUCZE DO ODCZYTU CHMURY ===
BIN_ID = "6a28dc21da38895dfea43ea0"
API_KEY = "$2a$10$y5.kSvqXKBJ1C3japhFar.w6U3dHO1OgK8k9im6VgKY0PpMkgEwBO"
URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}/latest"
# ==========================================================

@st.cache_data(ttl=10)
def pobierz_dane_z_chmury():
    headers = {"X-Master-Key": API_KEY}
    try:
        response = requests.get(URL, headers=headers)
        if response.status_code == 200:
            wynik = response.json()['record']
            
            # ZABEZPIECZENIE: Jeśli w chmurze leży tekst typu "pusta baza", zwróć pustą listę
            if isinstance(wynik, str) or not isinstance(wynik, list):
                return []
                
            # Czyszczenie ukrytych spacji w locie
            for wpis in wynik:
                if 'dzial' in wpis: wpis['dzial'] = str(wpis['dzial']).strip()
                if 'linia' in wpis: wpis['linia'] = str(wpis['linia']).strip()
                if 'maszyna' in wpis: wpis['maszyna'] = str(wpis['maszyna']).strip()
            return wynik
        return []
    except:
        return []

# Pobranie danych
dane = pobierz_dane_z_chmury()

# --- SEKCJA FILTROWANIA NA TELEFONIE ---
if dane:
    # 1. Filtr Dział
    dzialy = sorted(list(set(i['dzial'] for i in dane if i.get('dzial'))))
    wybrany_dzial = st.selectbox("Wybierz Dział:", [""] + dzialy)

    # 2. Filtr Linia
    linie = []
    if wybrany_dzial:
        linie = sorted(list(set(i['linia'] for i in dane if i.get('dzial') == wybrany_dzial and i.get('linia'))))
    wybrana_linia = st.selectbox("Wybierz Linię:", [""] + linie, disabled=not wybrany_dzial)

    # 3. Filtr Maszyna
    maszyny = []
    if wybrana_linia:
        maszyny = sorted(list(set(
            i['maszyna'] for i in dane 
            if i.get('dzial') == wybrany_dzial 
            and i.get('linia') == wybrana_linia 
            and i.get('maszyna')
        )))
    wybrana_maszyna = st.selectbox("Wybierz Maszynę:", [""] + maszyny, disabled=not wybrana_linia)

    # --- WYŚWIETLANIE WYNIKÓW ---
    filtrowane = [i for i in dane if i.get('dzial') == wybrany_dzial and i.get('linia') == wybrana_linia and i.get('maszyna') == wybrana_maszyna]

    if wybrana_maszyna and filtrowane:
        st.success(f"Znaleziono awarie ({len(filtrowane)}):")
        opcje_awarii = [f"{idx+1}. Objaw: {item['objawy']}" for idx, item in enumerate(filtrowane)]
        wybrana_opcja = st.radio("Wybierz konkretną awarię:", opcje_awarii)
        
        if wybrana_opcja:
            idx_wybranej = opcje_awarii.index(wybrana_opcja)
            wpis = filtrowane[idx_wybranej]
            
            st.info(f"**OBJAWY:**\n{wpis['objawy']}")
            st.markdown("**⚙️ PROCEDURA SPRAWDZENIA:**")
            for linia in wpis['do_sprawdzenia'].split('\n'):
                if linia.strip():
                    st.markdown(f"👉 {linia}")
    elif wybrana_maszyna:
        st.warning("Brak zarejestrowanych awarii dla tej maszyny.")
else:
    st.info("☁️ Serwer mobilny działa! Chmura jest jednak pusta. Uruchom program na swoim komputerze (PC) i kliknij 'ZAPISZ' przy dowolnej awarii, aby przesłać tutaj bazę z OneDrive.")