import streamlit as st
import pandas as pd
import requests

# --- Global Configuration & State Initialization ---
# URL till FastAPI-servern
SMART_API_URL = "http://127.0.0.1:8000/smart_predict"

# Initiera session_state för splash screen
if 'show_splash' not in st.session_state:
    st.session_state.show_splash = True
if 'price' not in st.session_state:
    st.session_state.price = None
if 'error' not in st.session_state:
    st.session_state.error = None

# --- Page configuration ---
st.set_page_config(
    page_title="Taxi Fare Prediction Dashboard",
    page_icon="🚕",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- Huvudfunktion för att dölja splash screen ---
def hide_splash():
    """Sätter state till False när knappen klickas."""
    st.session_state.show_splash = False

# --- Estetik: Cool, Mörk Design med Animationer ---
custom_css = """
<style>
/* Font och Dark Mode */
html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', sans-serif;
    color: #f0f0f0; /* Ljus text */
    background-color: #1a1a2e; /* Mörk bakgrund */
}

/* Splash Screen Container - endast visuell overlay */
#splash-container {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background-color: rgba(26, 26, 46, 0.98); /* Högre opacitet för att täcka allt */
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}
#splash-content {
    background: #1a1a2e;
    padding: 40px 60px;
    border-radius: 20px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    text-align: center;
    z-index: 1001; /* Se till att content är över bakgrunden */
}

/* Knappstil */
.stButton>button {
    background-color: #ff3b5f !important; /* Röd accentfärg */
    color: white !important;
    border: none;
    padding: 10px 30px;
    border-radius: 12px;
    font-weight: 700;
    transition: background-color 0.3s;
    box-shadow: 0 4px 15px rgba(255, 59, 95, 0.4);
}
.stButton>button:hover {
    background-color: #e02a4a !important;
}

/* Sidebar & Main Area - Gör dem lättare att se mot mörk bakgrund */
[data-testid="stSidebar"], .main {
    background-color: rgba(40, 40, 60, 0.7) !important;
    border-radius: 15px;
}
/* Metriker för resultat */
[data-testid="stMetric"] {
    background-color: #28283c;
    padding: 15px;
    border-radius: 12px;
    border-left: 5px solid #ff3b5f;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
}

/* --- Parallax & Floating Animation (Visuella effekter) --- */
@keyframes float {
    0% { transform: translate(0, 0) rotate(0deg); opacity: 0.6; }
    50% { transform: translate(20px, -20px) rotate(5deg); opacity: 0.8; }
    100% { transform: translate(0, 0) rotate(0deg); opacity: 0.6; }
}

.floating-icon {
    position: fixed;
    font-size: 5vw;
    opacity: 0.6;
    color: #ff3b5f;
    z-index: -1;
    animation: float 15s ease-in-out infinite;
}

/* Individuella positioner för 'parallax'-effekt */
#icon1 { top: 10%; left: 5%; animation-delay: 0s; font-size: 80px; }
#icon2 { top: 70%; right: 15%; animation-delay: 5s; font-size: 50px; color: #4CAF50; }
#icon3 { top: 40%; left: 85%; animation-delay: 10s; font-size: 100px; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- Skapa flytande ikoner i bakgrunden (Parallax-känsla) ---




# --- 1. Splash Screen Logik (Nu med en klickbar Streamlit-knapp) ---
if st.session_state.show_splash:
    
    # Använder en stor, blockerande container för att täcka hela skärmen
    st.markdown("""
        <div id="splash-container">
            <div id="splash-content">
                <h1 style='color: white; margin-bottom: 15px;'>Resekollen AB</h1>
                <h2 style='color: #ff3b5f; margin-bottom: 30px;'>Smart Fare Estimator</h2>
                <p style='color: #ccc; margin-bottom: 90px;'>Klicka på knappen nedan för att ladda taxiprediktions-dashboarden.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    # Använd Streamlit-kolumner för att centrera knappen, vilket är mer Streamlit-vänligt
    # än att försöka styra positionen med complex CSS.
    # Knappen måste ligga utanför den fasta #splash-container för att vara interaktiv.
    
    # Skapa tre kolumner: en tom, en för knappen, och en tom.
    # Vi måste också lägga till lite marginal för att trycka ner knappen under textrutan.
    st.markdown("""
        <style>
            .stButton {
                margin-top: 250px !important; /* Flytta ner knappen visuellt */
                z-index: 1003; /* Högre än alla andra element */
                position: relative; /* Position relative works well with Streamlit centering */
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Använd kolumner för att få knappen centrerad
    col_empty1, col_center, col_empty2 = st.columns([1, 0.4, 1])
    
    with col_center:
        # Den klickbara Streamlit-knappen. on_click garanterar att den triggas.
        if st.button("Starta Dashboard", key="splash_btn", on_click=hide_splash):
            # Ingen kod behövs här, on_click hanterar state-ändringen
            pass
            
    # Stoppa renderingen av resten av sidan
    st.stop()


# --- Huvudapplikationen börjar här ---

# --- Sidebar setup ( Business rules for product owner/admin)
with st.sidebar:
    st.header("⚙️ Business Rules (Product Owner Settings)")
    st.markdown(
        "Justera baspris och taxor för att se omedelbar effekt på prediktionen."
    )

    custom_base_fare = st.number_input(
        "Base Fare ($)", min_value=1.0, value=3.5, step=0.1
    )
    custom_per_km_rate = st.number_input(
        "Rate Per km ($)", min_value=0.5, value=1.5, step=0.05
    )
    custom_per_minute_rate = st.number_input(
        "Rate Per Minute ($)", min_value=0.1, value=0.4, step=0.05
    )

    st.markdown("---")


# --- Main Page Content ---
st.title("Resekollen AB: Smart Fare Estimator 🌍")
st.markdown("Ange dina reseuppgifter för att få ett estimerat pris för din resa.")
st.markdown("Du hittar Admin inställningar i sidomenyn till vänster.")

# --- User input for trip ---
st.header("1. Plan your trip")
col1, col2, col3 = st.columns(3)
with col1:
    start_location = st.text_input("Var är du?", "Centralstationen, Borås")
with col2:
    end_location = st.text_input("Vart ska du?", "Liseberg, Göteborg")
with col3:
    # Passenger Input
    passenger_count = st.slider("Antal passagerare", 1, 4, 1)

# --- Prediction Button and Logic ---
st.markdown("---")
if st.button("Beräkna Pris", type="primary", use_container_width=True):
    payload = {
        "start_location": start_location,
        "end_location": end_location,
        "passenger_count": passenger_count,
        "base_fare": custom_base_fare,
        "per_km_rate": custom_per_km_rate,
        "per_minute_rate": custom_per_minute_rate,
    }

    try:
        with st.spinner("Beräknar avstånd, trafik och pris..."):
            response = requests.post(SMART_API_URL, json=payload)
            response.raise_for_status()

            result = response.json()

            if "error" in result:
                st.session_state.error = result["error"]
                st.session_state.price = None
            else:
                # Lagra resultat i session_state för visning
                st.session_state.price = result.get("predicted_price")
                st.session_state.distance = result.get("calculated_distance_km")
                st.session_state.duration = result.get("calculated_duration_minutes")
                st.session_state.start_loc = start_location
                st.session_state.end_loc = end_location
                st.session_state.error = None

                # Koordinater för kartan
                st.session_state.start_lat = result.get("start_lat")
                st.session_state.start_lon = result.get("start_lon")
                st.session_state.end_lat = result.get("end_lat")
                st.session_state.end_lon = result.get("end_lon")

    except requests.exceptions.RequestException as e:
        # Fel om FastAPI-servern inte kör
        st.session_state.error = f"Kunde inte ansluta till API:et: {e}. Körs din FastAPI-server?"
        st.session_state.price = None

# --- Visa Resultat ---
if st.session_state.error:
    st.error(st.session_state.error)

elif st.session_state.price is not None:
    st.header("2. Ditt Uppskattade Pris")
    col_res1, col_res2, col_res3 = st.columns(3)

    with col_res1:
        st.metric("Uppskattat Pris", f"${st.session_state.price:.2f}", delta_color="off")
    with col_res2:
        st.metric("Distans", f"{st.session_state.distance:.2f} km")
    with col_res3:
        st.metric("Restid", f"{st.session_state.duration:.0f} min")

    # --- Visualisering av Rutten ---
    st.markdown("---")
    st.subheader("Visualiserad Rutt")

    # Beräkna median för att centrera kartan över resan (Borås - Göteborg)
    center_lat = (st.session_state.start_lat + st.session_state.end_lat) / 2
    center_lon = (st.session_state.start_lon + st.session_state.end_lon) / 2

    # DataFrame för kartan
    map_data = pd.DataFrame(
        {
            "lat": [st.session_state.start_lat, st.session_state.end_lat],
            "lon": [st.session_state.start_lon, st.session_state.end_lon],
            "label": ["Start", "Slut"],
        }
    )

    # st.map med zoom för att täcka hela resan (Fitted map)
    st.map(
        map_data,
        latitude=center_lat,
        longitude=center_lon,
        zoom=7,
        use_container_width=True,
        
    )
