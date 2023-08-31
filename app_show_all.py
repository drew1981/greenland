import streamlit as st
import pydeck as pdk
import sqlite3
import os

# Funzione per ottenere i dati dal database
def fetch_data_from_db():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    db_path = os.path.join(dir_path, 'discariche.db')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT id, latitude, longitude FROM discariche')
    data = cursor.fetchall()
    conn.close()
    
    return data

data = fetch_data_from_db()

# Estrai le coordinate e assegna un colore in base all'ID (o un altro criterio che preferisci)
points = [{"coordinates": [row[2], row[1]], "color": [255, row[0] % 256, 0, 200]} for row in data]

# Crea l'app Streamlit
st.title('Discariche o Accumuli segnalati')

# Visualizza le coordinate sulla mappa
layer = pdk.Layer(
    type='ScatterplotLayer',
    data=points,
    get_position='coordinates',
    get_radius=800,
    get_fill_color='color',
    pickable=True
)

view_state = pdk.ViewState(latitude=45, longitude=9, zoom=5)
deck = pdk.Deck(layers=[layer], initial_view_state=view_state)

st.pydeck_chart(deck)
