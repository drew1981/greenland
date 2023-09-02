import streamlit as st
import requests

API_WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather"
API_FORECAST_URL = "http://api.openweathermap.org/data/2.5/forecast"
API_KEY = "2580df11423db041d0eba7ad5a1a7252"  # La tua chiave API

def get_weather_data(city_name):
    params = {
        'q': city_name,
        'appid': API_KEY,
        'units': 'metric',
    }
    response = requests.get(API_WEATHER_URL, params=params)
    return response.json()

def get_forecast_data(city_name):
    params = {
        'q': city_name,
        'appid': API_KEY,
        'units': 'metric',
    }
    response = requests.get(API_FORECAST_URL, params=params)
    return response.json()

st.title("EZ Meteo")

city_name = st.text_input("Inserisci il nome della città:")

if city_name:
    data = get_weather_data(city_name)
    
    if data.get("cod") == 200:
        weather_icon = data['weather'][0]['icon']
        icon_url = f"http://openweathermap.org/img/w/{weather_icon}.png"
        
        st.write(f"**Temperatura attuale:** {data['main']['temp']}°C")
        st.write(f"**Condizioni:** {data['weather'][0]['description'].capitalize()}")
        st.image(icon_url)  # Mostra l'icona delle condizioni meteo
        st.write(f"**Umidità:** {data['main']['humidity']}%")
        st.write(f"**Velocità del vento:** {data['wind']['speed']} m/s")
        
        st.write("\n**Previsioni per le prossime ore:**")
        forecast_data = get_forecast_data(city_name)
        for forecast in forecast_data['list'][:5]:  # Mostra le previsioni per le prossime 5 entrate (15 ore)
            dt_txt = forecast['dt_txt']
            temperature = forecast['main']['temp']
            description = forecast['weather'][0]['description'].capitalize()
            icon = forecast['weather'][0]['icon']
            icon_url = f"http://openweathermap.org/img/w/{icon}.png"
            
            st.write(f"**{dt_txt}** - {description} - {temperature}°C")
            st.image(icon_url, use_column_width=True)
    else:
        st.write("Errore nel recupero dei dati. Assicurati che il nome della città sia corretto.")
