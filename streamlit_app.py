import streamlit as st
import requests
from streamlit_folium import folium_static
import folium

api_key = "da92899d-7354-4823-8145-9e62c84bc561"

st.title("Weather and Air Quality Web App")
st.header("Streamlit and AirVisual API")

@st.cache
def map_creator(latitude, longitude):
    # Create a Folium map centered on the specified location
    m = folium.Map(location=[latitude, longitude], zoom_start=10)
    folium.Marker([latitude, longitude], popup="Station", tooltip="Station").add_to(m)
    folium_static(m)

@st.cache
def generate_list_of_countries():
    countries_url = f"https://api.airvisual.com/v2/countries?key={api_key}"
    countries_dict = requests.get(countries_url).json()
    return countries_dict

# Other helper functions for generating states and cities go here (similar to the existing ones)

# TODO: Add a select box for the options: ["By City, State, and Country", "By Nearest City (IP Address)", "By Latitude and Longitude"]
category = st.selectbox("Select a category", ["By City, State, and Country", "By Nearest City (IP Address)", "By Latitude and Longitude"])

if category == "By City, State, and Country":
    countries_dict = generate_list_of_countries()
    if countries_dict["status"] == "success":
        countries_list = [""]
        for country_data in countries_dict["data"]:
            countries_list.append(country_data["country"])
        country_selected = st.selectbox("Select a country", options=countries_list)
        if country_selected:
            # Generate the list of states
            states_dict = generate_list_of_states(country_selected)
            if states_dict["status"] == "success":
                states_list = [""]
                for state_data in states_dict["data"]:
                    states_list.append(state_data["state"])
                state_selected = st.selectbox("Select a state", options=states_list)
                if state_selected:
                    # Generate the list of cities
                    cities_dict = generate_list_of_cities(state_selected, country_selected)
                    if cities_dict["status"] == "success":
                        cities_list = [""]
                        for city_data in cities_dict["data"]:
                            cities_list.append(city_data["city"])
                        city_selected = st.selectbox("Select a city", options=cities_list)
                        if city_selected:
                            aqi_data_url = f"https://api.airvisual.com/v2/city?city={city_selected}&state={state_selected}&country={country_selected}&key={api_key}"
                            aqi_data_dict = requests.get(aqi_data_url).json()
                            if aqi_data_dict["status"] == "success":
                                # Display the weather and air quality data
                                location = aqi_data_dict["data"]["city"]
                                temperature = aqi_data_dict["data"]["current"]["weather"]["tp"]
                                humidity = aqi_data_dict["data"]["current"]["weather"]["hu"]
                                aqi = aqi_data_dict["data"]["current"]["pollution"]["aqius"]
                                st.subheader(f"Weather and Air Quality for {location}")
                                st.write(f"Temperature: {temperature} °C")
                                st.write(f"Humidity: {humidity}%")
                                st.write(f"Air Quality Index (AQI): {aqi}")
                                # Call the map_creator function to display the map
                                latitude = aqi_data_dict["data"]["location"]["coordinates"][1]
                                longitude = aqi_data_dict["data"]["location"]["coordinates"][0]
                                map_creator(latitude, longitude)
                            else:
                                st.warning("No data available for this location.")
                        else:
                            st.warning("Please select a city.")
                    else:
                        st.warning("No cities available for this state.")
                else:
                    st.warning("Please select a state.")
            else:
                st.warning("No states available for this country.")
        else:
            st.warning("Please select a country.")
    else:
        st.error("Too many requests. Wait for a few minutes before your next API call.")

elif category == "By Nearest City (IP Address)":
    url = f"https://api.airvisual.com/v2/nearest_city?key={api_key}"
    aqi_data_dict = requests.get(url).json()
    if aqi_data_dict["status"] == "success":
        # Display the weather and air quality data
        # Similar to the previous section
    else:
        st.warning("No data available for this location.")

elif category == "By Latitude and Longitude":
    latitude = st.text_input("Enter latitude:")
    longitude = st.text_input("Enter longitude:")
    if latitude and longitude:
        url = f"https://api.airvisual.com/v2/nearest_city?lat={latitude}&lon={longitude}&key={api_key}"
