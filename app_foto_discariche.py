import streamlit as st
import pydeck as pdk
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import os
import sqlite3
import signal


def create_database():
    # Ottieni la directory del tuo script Python
    dir_path = os.path.dirname(os.path.realpath(__file__))
    
    # Costruisci il percorso assoluto al file del database
    db_path = os.path.join(dir_path, 'discariche.db')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS discariche (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        image BLOB,
        latitude REAL,
        longitude REAL,
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

create_database()

def save_image_to_database(image, latitude, longitude):
    # Ottieni la directory del tuo script Python
    dir_path = os.path.dirname(os.path.realpath(__file__))
    
    # Costruisci il percorso assoluto al file del database
    db_path = os.path.join(dir_path, 'discariche.db')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Converti l'immagine in un formato binario
    image_data = image.read()

    # Inserisci i dati nel database
    cursor.execute('''
    INSERT INTO discariche (image, latitude, longitude) VALUES (?, ?, ?)
    ''', (image_data, latitude, longitude))
    
    conn.commit()
    conn.close()



# Funzioni per l'estrazione delle coordinate EXIF
def get_geolocation_from_image(uploaded_image):
    image = Image.open(uploaded_image)
    exif_data = image._getexif()

    if not exif_data:
        return None

    geotagging = {}
    for (idx, tag) in TAGS.items():
        if tag == 'GPSInfo':
            if idx not in exif_data:
                raise ValueError("No EXIF geotagging found")

            for (key, val) in GPSTAGS.items():
                if key in exif_data[idx]:
                    geotagging[val] = exif_data[idx][key]

    return geotagging

def get_decimal_coordinates(info):
    def rational_to_decimal(rational):
        return rational.numerator / rational.denominator

    for key in ['Latitude', 'Longitude']:
        if 'GPS' + key in info and 'GPS' + key + 'Ref' in info:
            components = info['GPS' + key]
            ref = info['GPS' + key + 'Ref']

            degrees = rational_to_decimal(components[0])
            minutes = rational_to_decimal(components[1])
            seconds = rational_to_decimal(components[2])

            info[key] = (degrees + minutes/60 + seconds/3600) * (-1 if ref in ['S', 'W'] else 1)

    if 'Latitude' in info and 'Longitude' in info:
        return [info['Latitude'], info['Longitude']]

def fetch_all_discariche():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    db_path = os.path.join(dir_path, 'discariche.db')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT latitude, longitude FROM discariche')
    all_discariche = cursor.fetchall()
    conn.close()
    
    return all_discariche
class SessionState:
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

def get_session():
    if not hasattr(st, '_session_state'):
        st._session_state = SessionState()
    return st._session_state

# Recupera tutte le discariche dal database
all_discariche = fetch_all_discariche()

data_points = [{'position': [longitude, latitude], 'color': [255, 0, 0, 200]} for latitude, longitude in all_discariche]

# App Streamlit
st.title('Monitoraggio delle discariche abusive e accumuli di rifiuti')

uploaded_file = st.file_uploader("Carica un'immagine della discarica", type=['png', 'jpg', 'jpeg'])

latitude = 45  # Coordinata di default
longitude = 9  # Coordinata di default

if uploaded_file:
    st.image(uploaded_file, caption="Immagine caricata.", use_column_width=True)

    geolocation = get_geolocation_from_image(uploaded_file)
    coordinates = get_decimal_coordinates(geolocation) if geolocation else None

    if coordinates:
        latitude, longitude = coordinates
        st.write(f"Latitudine: {latitude}, Longitudine: {longitude}")

        # Salva l'immagine e le coordinate nel database
        save_image_to_database(uploaded_file, latitude, longitude)

    # Visualizza le coordinate sulla mappa
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=pdk.ViewState(
            latitude=latitude,
            longitude=longitude,
            zoom=11,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
                'ScatterplotLayer',
                data=[{'position': [longitude, latitude], 'color': [255, 0, 0, 200]}],
                get_position='position',
                get_color='color',
                get_radius=100,
            ),
        ],
    ))

else:
    st.write("Impossibile estrarre le coordinate dall'immagine. Assicurati che l'immagine abbia metadati di geolocalizzazione.")

st.write("Grazie per il tuo contributo! L'immagine è stata acquisita dal nostro sistema, ora puoi chiudere la pagina")
